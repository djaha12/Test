import http from 'node:http';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { loadConfig, publicConfig } from './config.js';
import { openDb, utcDay } from './db.js';
import { deviceHash, redeemCode, signToken, verifyToken } from './codes.js';
import { createLimiter } from './ratelimit.js';
import { eventStats, recordEvent } from './events.js';
import { classifyError, createCoach, detectCrisis, sanitizeMessages } from './coach.js';
import { createStaticHandler, SECURITY_HEADERS } from './static.js';

const PUBLIC_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'public');
const MAX_BODY = 32 * 1024;

function sendJSON(res, status, data, extra = {}) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    ...SECURITY_HEADERS,
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    ...extra,
  });
  res.end(body);
}

async function readJSON(req) {
  const type = req.headers['content-type'] || '';
  if (!type.startsWith('application/json')) throw Object.assign(new Error('bad content-type'), { status: 415 });
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY) throw Object.assign(new Error('too large'), { status: 413 });
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
  } catch {
    throw Object.assign(new Error('bad json'), { status: 400 });
  }
}

export function createApp({ config, db, coach, now = () => Date.now() }) {
  const serveStatic = createStaticHandler(PUBLIC_DIR);
  const limits = {
    redeem: createLimiter({ windowMs: 10 * 60 * 1000, max: 10, now }),
    coach: createLimiter({ windowMs: 60 * 1000, max: 20, now }),
    events: createLimiter({ windowMs: 60 * 1000, max: 120, now }),
    coachIpDaily: createLimiter({ windowMs: 24 * 60 * 60 * 1000, max: Math.max(20, config.ai.freePerDay * 10), now }),
  };

  const usage = {
    get: db.prepare('SELECT count FROM ai_usage WHERE subject = ? AND day = ?'),
    inc: db.prepare(`INSERT INTO ai_usage (subject, day, count) VALUES (?, ?, 1)
      ON CONFLICT (subject, day) DO UPDATE SET count = count + 1`),
    dec: db.prepare('UPDATE ai_usage SET count = MAX(0, count - 1) WHERE subject = ? AND day = ?'),
  };

  function clientIp(req) {
    if (config.trustProxy) {
      const forwarded = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
      if (forwarded) return forwarded;
    }
    return req.socket.remoteAddress || 'unknown';
  }

  async function handleRedeem(req, res, ip) {
    const limit = limits.redeem.hit(ip);
    if (!limit.allowed) return sendJSON(res, 429, { error: 'rate_limited' }, { 'retry-after': String(limit.retryAfter) });
    const body = await readJSON(req);
    const result = redeemCode(db, config.appSecret, { code: body.code, deviceId: body.deviceId, now: now() });
    if (result.error) return sendJSON(res, 400, { error: result.error });
    return sendJSON(res, 200, { token: signToken(config.appSecret, { device: result.device, exp: result.exp }), exp: result.exp });
  }

  async function handleCoach(req, res, ip) {
    if (!config.ai.enabled) return sendJSON(res, 503, { error: 'unavailable' });
    const limit = limits.coach.hit(ip);
    if (!limit.allowed) return sendJSON(res, 429, { error: 'rate_limited' }, { 'retry-after': String(limit.retryAfter) });

    const body = await readJSON(req);
    const messages = sanitizeMessages(body.messages);
    if (!messages || !/^[a-f0-9]{32}$/.test(body.deviceId || '')) return sendJSON(res, 400, { error: 'bad_request' });

    const device = deviceHash(config.appSecret, body.deviceId);
    const auth = String(req.headers.authorization || '');
    const premium = auth.startsWith('Bearer ') ? verifyToken(config.appSecret, auth.slice(7), now()) : null;
    const isPremium = Boolean(premium && premium.device === device);
    const subject = `${isPremium ? 'p' : 'f'}:${device}`;
    const perDay = isPremium ? config.ai.premiumPerDay : config.ai.freePerDay;
    const day = utcDay(now());
    const used = usage.get.get(subject, day)?.count || 0;
    if (used >= perDay) return sendJSON(res, 429, { error: 'limit' });
    if (!isPremium && !limits.coachIpDaily.hit(ip).allowed) return sendJSON(res, 429, { error: 'limit' });
    usage.inc.run(subject, day);

    res.writeHead(200, {
      ...SECURITY_HEADERS,
      'content-type': 'text/event-stream; charset=utf-8',
      'cache-control': 'no-cache, no-transform',
      'x-accel-buffering': 'no',
      connection: 'keep-alive',
    });
    const send = (event, data) => { if (!res.writableEnded) res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`); };
    const controller = new AbortController();
    res.on('close', () => controller.abort());

    const lastUser = messages[messages.length - 1].content;
    send('meta', { remaining: isPremium ? null : Math.max(0, perDay - used - 1), crisis: detectCrisis(lastUser) });

    let wrote = false;
    try {
      await coach.reply({
        messages,
        lang: ['ru', 'ky', 'kk'].includes(body.lang) ? body.lang : 'ru',
        country: body.country === 'kz' ? 'kz' : 'kg',
        context: body.context && typeof body.context === 'object' ? body.context : {},
      }, {
        delta: (text) => { wrote = true; send('delta', { text }); },
        replace: (text) => { wrote = true; send('replace', { text }); },
      }, controller.signal);
      send('done', {});
    } catch (err) {
      const code = classifyError(err);
      if (code !== 'aborted') {
        if (!wrote) usage.dec.run(subject, day);
        console.error('[coach]', code, err?.status || '', err?.message || err);
        send('error', { code });
      }
    } finally {
      res.end();
    }
    return undefined;
  }

  async function handleEvent(req, res, ip) {
    if (!limits.events.hit(ip).allowed) return sendJSON(res, 429, { error: 'rate_limited' });
    const body = await readJSON(req);
    recordEvent(db, { name: body.name, source: body.source, now: now() });
    res.writeHead(204, SECURITY_HEADERS);
    res.end();
    return undefined;
  }

  function handleStats(req, res, url) {
    const auth = String(req.headers.authorization || '');
    if (!config.adminToken || auth !== `Bearer ${config.adminToken}`) return sendJSON(res, 401, { error: 'unauthorized' });
    const days = Math.max(1, Math.min(365, Number(url.searchParams.get('days')) || 30));
    return sendJSON(res, 200, eventStats(db, { days, now: now() }));
  }

  return async function handler(req, res) {
    const url = new URL(req.url, 'http://localhost');
    const ip = clientIp(req);
    try {
      if (url.pathname.startsWith('/api/')) {
        if (req.method === 'GET' && url.pathname === '/api/health') return sendJSON(res, 200, { ok: true });
        if (req.method === 'GET' && url.pathname === '/api/config') return sendJSON(res, 200, publicConfig(config));
        if (req.method === 'POST' && url.pathname === '/api/redeem') return await handleRedeem(req, res, ip);
        if (req.method === 'POST' && url.pathname === '/api/coach') return await handleCoach(req, res, ip);
        if (req.method === 'POST' && url.pathname === '/api/event') return await handleEvent(req, res, ip);
        if (req.method === 'GET' && url.pathname === '/api/admin/stats') return handleStats(req, res, url);
        return sendJSON(res, 404, { error: 'not_found' });
      }
      if ((req.method === 'GET' || req.method === 'HEAD') && await serveStatic(req, res, url.pathname)) return undefined;
      return sendJSON(res, 404, { error: 'not_found' });
    } catch (err) {
      if (res.headersSent) {
        res.end();
        return undefined;
      }
      const status = err?.status || 500;
      if (status === 500) console.error('[server]', err);
      return sendJSON(res, status, { error: status === 500 ? 'server_error' : 'bad_request' });
    }
  };
}

export function start(env = process.env) {
  const config = loadConfig(env);
  mkdirSync(config.dataDir, { recursive: true });
  const db = openDb(join(config.dataDir, 'stopstavka.db'));
  const coach = createCoach({ config });
  const server = http.createServer(createApp({ config, db, coach }));
  server.listen(config.port, config.host, () => {
    const mode = config.ai.mock ? 'ИИ в тестовом режиме (AI_MOCK=1)' : config.ai.enabled ? `ИИ: ${config.ai.model}` : 'ИИ выключен (нет ANTHROPIC_API_KEY)';
    console.log(`Стоп-ставка: http://localhost:${config.port} · ${mode}`);
  });
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) start();
