import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';

import { loadConfig, publicConfig } from '../server/config.js';
import { openDb } from '../server/db.js';
import { issueCodes, normalizeCode, signToken, verifyToken } from '../server/codes.js';
import { buildRequest, createCoach, detectCrisis, refusalText, sanitizeMessages, SYSTEM_PROMPT } from '../server/coach.js';
import { createApp } from '../server/index.js';

const SECRET = 'test-secret-0123456789abcdef';
const DEVICE_A = 'a'.repeat(32);
const DEVICE_B = 'b'.repeat(32);

function makeConfig(extra = {}) {
  return loadConfig({ APP_SECRET: SECRET, AI_MOCK: '1', FREE_AI_PER_DAY: '2', ADMIN_TOKEN: 'admin-token', ...extra });
}

async function startServer({ config = makeConfig(), coach } = {}) {
  const db = openDb(':memory:');
  const server = http.createServer(createApp({ config, db, coach: coach || createCoach({ config }) }));
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  return { server, db, base, config };
}

function parseSSE(text) {
  return text.split('\n\n').filter(Boolean).map((chunk) => {
    const event = /event: (.*)/.exec(chunk)?.[1];
    const data = JSON.parse(/data: (.*)/.exec(chunk)?.[1] || '{}');
    return { event, data };
  });
}

const post = (base, path, body, headers = {}) => fetch(base + path, {
  method: 'POST',
  headers: { 'content-type': 'application/json', ...headers },
  body: JSON.stringify(body),
});

let app;
before(async () => { app = await startServer(); });
after(() => app.server.close());

test('health, публичный конфиг без секретов, 404 для неизвестного API', async () => {
  assert.deepEqual(await (await fetch(`${app.base}/api/health`)).json(), { ok: true });
  const config = await (await fetch(`${app.base}/api/config`)).json();
  assert.equal(config.ai.enabled, true);
  assert.equal(config.prices.kg[1], 390);
  assert.equal(config.payment.kg, null);
  assert.ok(!JSON.stringify(config).includes(SECRET));
  assert.equal((await fetch(`${app.base}/api/nope`)).status, 404);
  const pub = publicConfig(makeConfig({ PAY_KG_PHONE: '+996555000111', PAY_KG_CONTACT: '+996555000222' }));
  assert.deepEqual(pub.payment.kg, { phone: '+996555000111', contact: '+996555000222' });
});

test('статика: index.html с заголовками безопасности, выход за папку запрещён', async () => {
  const res = await fetch(`${app.base}/`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get('content-type'), /text\/html/);
  assert.match(res.headers.get('content-security-policy'), /default-src 'self'/);
  assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
  assert.match(await res.text(), /Стоп-ставка/);
  const js = await fetch(`${app.base}/js/main.js`);
  assert.match(js.headers.get('content-type'), /javascript/);
  for (const path of ['/../package.json', '/%2e%2e/server/index.js', '/..%2fpackage.json', '/js/%00main.js']) {
    const bad = await fetch(app.base + path);
    assert.equal(bad.status, 404, path);
  }
});

test('коды подписки: нормализация, активация, повтор и чужое устройство', async () => {
  assert.equal(normalizeCode('ss-abcd-efgh'), 'SS-ABCD-EFGH');
  assert.equal(normalizeCode('abcdefgh'), 'SS-ABCD-EFGH');
  assert.equal(normalizeCode('SS-0000-1111'), null); // 0 и 1 не используются
  const [code] = issueCodes(app.db, SECRET, { days: 30 });
  const ok = await post(app.base, '/api/redeem', { code: code.toLowerCase(), deviceId: DEVICE_A });
  assert.equal(ok.status, 200);
  const { token, exp } = await ok.json();
  assert.ok(exp > Date.now() + 29 * 86400000);
  assert.ok(verifyToken(SECRET, token));
  const again = await post(app.base, '/api/redeem', { code, deviceId: DEVICE_A });
  assert.equal((await again.json()).exp, exp);
  const other = await post(app.base, '/api/redeem', { code, deviceId: DEVICE_B });
  assert.equal(other.status, 400);
  assert.equal((await other.json()).error, 'used');
  const invalid = await post(app.base, '/api/redeem', { code: 'SS-2222-3333', deviceId: DEVICE_A });
  assert.equal((await invalid.json()).error, 'invalid');
});

test('токен: подделка и истечение срока отклоняются', () => {
  const token = signToken(SECRET, { device: 'd'.repeat(32), exp: Date.now() + 1000 });
  assert.ok(verifyToken(SECRET, token));
  assert.equal(verifyToken('other-secret-0123456789', token), null);
  const [payload, sig] = token.split('.');
  const forged = Buffer.from(JSON.stringify({ p: 'plus', d: 'x', e: Date.now() + 1e9 })).toString('base64url');
  assert.equal(verifyToken(SECRET, `${forged}.${sig}`), null);
  assert.equal(verifyToken(SECRET, `${payload}.${sig}`, Date.now() + 5000), null);
  assert.equal(verifyToken(SECRET, 'garbage'), null);
});

test('активация: защита от перебора кодов', async () => {
  const fresh = await startServer();
  try {
    let last;
    for (let i = 0; i < 11; i++) last = await post(fresh.base, '/api/redeem', { code: 'SS-2222-3333', deviceId: DEVICE_A });
    assert.equal(last.status, 429);
    assert.equal((await last.json()).error, 'rate_limited');
  } finally {
    fresh.server.close();
  }
});

test('ИИ-поддержка (тестовый режим): поток, остаток бесплатных сообщений, лимит, кризис', async () => {
  const body = { messages: [{ role: 'user', content: 'Очень тянет поставить' }], lang: 'ru', country: 'kg', deviceId: DEVICE_B };
  const first = await post(app.base, '/api/coach', body);
  assert.equal(first.status, 200);
  assert.match(first.headers.get('content-type'), /text\/event-stream/);
  const events = parseSSE(await first.text());
  assert.equal(events[0].event, 'meta');
  assert.equal(events[0].data.remaining, 1);
  assert.equal(events[0].data.crisis, false);
  const text = events.filter((e) => e.event === 'delta').map((e) => e.data.text).join('');
  assert.match(text, /волна/);
  assert.equal(events.at(-1).event, 'done');

  const crisis = await post(app.base, '/api/coach', { ...body, messages: [{ role: 'user', content: 'Я не хочу жить' }] });
  assert.equal(parseSSE(await crisis.text())[0].data.crisis, true);

  const limited = await post(app.base, '/api/coach', body);
  assert.equal(limited.status, 429);
  assert.equal((await limited.json()).error, 'limit');

  // С подпиской «Плюс» лимит выше, остаток не показывается.
  const [code] = issueCodes(app.db, SECRET, { days: 30 });
  const { token } = await (await post(app.base, '/api/redeem', { code, deviceId: DEVICE_B })).json();
  const plus = await post(app.base, '/api/coach', body, { authorization: `Bearer ${token}` });
  assert.equal(plus.status, 200);
  assert.equal(parseSSE(await plus.text())[0].data.remaining, null);
  // Чужой токен не даёт «Плюс» другому устройству.
  const stolen = await post(app.base, '/api/coach', { ...body, deviceId: 'c'.repeat(32) }, { authorization: `Bearer ${token}` });
  assert.equal(parseSSE(await stolen.text())[0].data.remaining, 1);
});

test('ИИ-поддержка: плохие запросы', async () => {
  const bad = await post(app.base, '/api/coach', { messages: [{ role: 'assistant', content: 'hi' }], deviceId: DEVICE_A });
  assert.equal(bad.status, 400);
  const noDevice = await post(app.base, '/api/coach', { messages: [{ role: 'user', content: 'hi' }] });
  assert.equal(noDevice.status, 400);
  const wrongType = await fetch(`${app.base}/api/coach`, { method: 'POST', headers: { 'content-type': 'text/plain' }, body: 'x' });
  assert.equal(wrongType.status, 415);
  const huge = await post(app.base, '/api/coach', { messages: [{ role: 'user', content: 'x'.repeat(40000) }], deviceId: DEVICE_A });
  assert.equal(huge.status, 413);
});

test('ИИ-поддержка без ключа: 503', async () => {
  const off = await startServer({ config: makeConfig({ AI_MOCK: '0' }) });
  try {
    const res = await post(off.base, '/api/coach', { messages: [{ role: 'user', content: 'hi' }], deviceId: DEVICE_A });
    assert.equal(res.status, 503);
  } finally {
    off.server.close();
  }
});

test('Claude: запрос с claude-opus-5, fallbacks и кэшируемым промптом; отказ заменяется безопасным текстом', async () => {
  const config = makeConfig({ AI_MOCK: '0', ANTHROPIC_API_KEY: 'sk-test' });
  const request = buildRequest(config, {
    messages: [{ role: 'user', content: 'привет' }],
    lang: 'ky',
    country: 'kz',
    context: { daysClean: 12, saved: '36 000 ₸', reasons: ['Семья', 'x'.repeat(200)] },
  });
  assert.equal(request.model, 'claude-opus-5');
  assert.deepEqual(request.betas, ['server-side-fallback-2026-07-01']);
  assert.equal(request.fallbacks, 'default');
  assert.deepEqual(request.output_config, { effort: 'low' });
  assert.equal(request.system[0].text, SYSTEM_PROMPT);
  assert.deepEqual(request.system[0].cache_control, { type: 'ephemeral' });
  assert.match(request.system[1].text, /Язык интерфейса: ky/);
  assert.match(request.system[1].text, /150/);
  assert.ok(!request.system[1].text.includes('x'.repeat(81)));

  const noExtras = buildRequest(makeConfig({ AI_EFFORT: '', AI_FALLBACKS: '0', AI_MODEL: 'claude-haiku-4-5' }), { messages: [] });
  assert.equal(noExtras.output_config, undefined);
  assert.equal(noExtras.fallbacks, undefined);

  let captured = null;
  const fakeClient = {
    beta: {
      messages: {
        stream(params) {
          captured = params;
          const events = [
            { type: 'content_block_delta', delta: { type: 'text_delta', text: 'Частичный ' } },
            { type: 'content_block_delta', delta: { type: 'text_delta', text: 'текст' } },
          ];
          return {
            async* [Symbol.asyncIterator]() { yield* events; },
            finalMessage: async () => ({ stop_reason: 'refusal', content: [] }),
          };
        },
      },
    },
  };
  const server = await startServer({ config, coach: createCoach({ config, client: fakeClient }) });
  try {
    const res = await post(server.base, '/api/coach', {
      messages: [{ role: 'assistant', content: 'старое' }, { role: 'user', content: 'помоги' }],
      lang: 'ru', country: 'kg', deviceId: DEVICE_A,
    });
    const events = parseSSE(await res.text());
    const replace = events.find((e) => e.event === 'replace');
    assert.ok(replace, 'при отказе приходит замена');
    assert.equal(replace.data.text, refusalText('ru', 'kg'));
    assert.deepEqual(captured.messages, [{ role: 'user', content: 'помоги' }]);
  } finally {
    server.server.close();
  }
});

test('ИИ-модуль: очистка сообщений и детектор кризиса', () => {
  assert.equal(sanitizeMessages('x'), null);
  assert.equal(sanitizeMessages([{ role: 'user', content: '  ' }]), null);
  assert.deepEqual(sanitizeMessages([{ role: 'system', content: 'x' }, { role: 'user', content: ' a ' }]), [{ role: 'user', content: 'a' }]);
  assert.equal(sanitizeMessages(Array.from({ length: 30 }, (_, i) => ({ role: i % 2 ? 'assistant' : 'user', content: `m${i}` }))), null);
  assert.ok(detectCrisis('Иногда думаю, что не хочу жить'));
  assert.ok(detectCrisis('Жашагым келбейт'));
  assert.ok(detectCrisis('Өмір сүргім келмейді'));
  assert.ok(!detectCrisis('Хочу поставить на матч'));
});

test('события: учитываются только известные, статистика — по токену администратора', async () => {
  for (const name of ['app_open', 'app_open', 'test_done', 'hack']) {
    const res = await post(app.base, '/api/event', { name, source: 'TikTok' });
    assert.equal(res.status, 204);
  }
  await post(app.base, '/api/event', { name: 'app_open', source: '<script>' });
  assert.equal((await fetch(`${app.base}/api/admin/stats`)).status, 401);
  const stats = await (await fetch(`${app.base}/api/admin/stats`, { headers: { authorization: 'Bearer admin-token' } })).json();
  assert.equal(stats.totals.app_open, 3);
  assert.equal(stats.totals.test_done, 1);
  assert.equal(stats.totals.hack, undefined);
  assert.equal(stats.bySource.tiktok.app_open, 2);
  assert.equal(stats.bySource['(direct)'].app_open, 1);
});

test('конфиг: в production без APP_SECRET сервер не стартует', () => {
  assert.throws(() => loadConfig({ NODE_ENV: 'production' }), /APP_SECRET/);
  assert.throws(() => loadConfig({ APP_SECRET: 'short' }), /APP_SECRET/);
});
