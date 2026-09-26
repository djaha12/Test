import { createHmac, randomInt, timingSafeEqual } from 'node:crypto';

// Коды активации подписки: SS-XXXX-XXXX. В базе хранится только HMAC кода.
// Токен подписки подписан APP_SECRET и привязан к хешу устройства, поэтому сервер не хранит сессии.

const ALPHABET = '23456789ABCDEFGHJKMNPQRSTUVWXYZ';
const DAY = 86400000;

function hmac(secret, value) {
  return createHmac('sha256', secret).update(value).digest();
}

export function normalizeCode(input) {
  const cleaned = String(input || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  const body = cleaned.startsWith('SS') ? cleaned.slice(2) : cleaned;
  if (body.length !== 8 || [...body].some((c) => !ALPHABET.includes(c))) return null;
  return `SS-${body.slice(0, 4)}-${body.slice(4)}`;
}

export function generateCode() {
  let body = '';
  for (let i = 0; i < 8; i++) body += ALPHABET[randomInt(ALPHABET.length)];
  return `SS-${body.slice(0, 4)}-${body.slice(4)}`;
}

export function codeHash(secret, code) {
  return hmac(secret, `code:${code}`).toString('hex');
}

export function deviceHash(secret, deviceId) {
  return hmac(secret, `device:${deviceId}`).toString('hex').slice(0, 32);
}

export function issueCodes(db, secret, { days, count = 1, note = '', now = Date.now() }) {
  if (!Number.isInteger(days) || days < 1 || days > 3660) throw new RangeError('days: от 1 до 3660');
  if (!Number.isInteger(count) || count < 1 || count > 1000) throw new RangeError('count: от 1 до 1000');
  const insert = db.prepare('INSERT INTO codes (hash, days, note, created_at) VALUES (?, ?, ?, ?)');
  const codes = [];
  while (codes.length < count) {
    const code = generateCode();
    try {
      insert.run(codeHash(secret, code), days, String(note).slice(0, 200), now);
      codes.push(code);
    } catch {
      // крайне маловероятное совпадение — генерируем заново
    }
  }
  return codes;
}

// Активация: код одноразовый, повторная активация тем же устройством возвращает тот же срок.
export function redeemCode(db, secret, { code, deviceId, now = Date.now() }) {
  const normalized = normalizeCode(code);
  if (!normalized || !/^[a-f0-9]{32}$/.test(deviceId || '')) return { error: 'invalid' };
  const hash = codeHash(secret, normalized);
  const device = deviceHash(secret, deviceId);
  const row = db.prepare('SELECT days, redeemed_at, device FROM codes WHERE hash = ?').get(hash);
  if (!row) return { error: 'invalid' };
  if (row.redeemed_at) {
    if (row.device !== device) return { error: 'used' };
    return { ok: true, exp: row.redeemed_at + row.days * DAY, device };
  }
  const updated = db.prepare('UPDATE codes SET redeemed_at = ?, device = ? WHERE hash = ? AND redeemed_at IS NULL').run(now, device, hash);
  if (updated.changes !== 1) return { error: 'used' };
  return { ok: true, exp: now + row.days * DAY, device };
}

function b64url(buffer) {
  return Buffer.from(buffer).toString('base64url');
}

export function signToken(secret, { device, exp }) {
  const payload = b64url(JSON.stringify({ p: 'plus', d: device, e: exp }));
  return `${payload}.${b64url(hmac(secret, `token:${payload}`))}`;
}

export function verifyToken(secret, token, now = Date.now()) {
  if (typeof token !== 'string' || token.length > 600) return null;
  const [payload, signature] = token.split('.');
  if (!payload || !signature) return null;
  const expected = hmac(secret, `token:${payload}`);
  const given = Buffer.from(signature, 'base64url');
  if (given.length !== expected.length || !timingSafeEqual(given, expected)) return null;
  try {
    const data = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
    if (data.p !== 'plus' || typeof data.e !== 'number' || data.e <= now) return null;
    return { device: data.d, exp: data.e };
  } catch {
    return null;
  }
}
