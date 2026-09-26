// Запросы к серверу приложения. Без сервера (демо-превью) приложение работает, но без ИИ и оплаты.

export class ApiError extends Error {
  constructor(code) {
    super(code);
    this.code = code;
  }
}

// Демо-сборка (одна HTML-страница без сервера) ставит этот флаг: запросы к API не делаются.
const DEMO = globalThis.__STOPSTAVKA_DEMO__ === true;

export function isDemo() {
  return DEMO;
}

let configPromise = null;

export function getConfig() {
  if (DEMO) return Promise.resolve(null);
  if (!configPromise) {
    configPromise = fetch('/api/config', { headers: { accept: 'application/json' } })
      .then((res) => (res.ok ? res.json() : null))
      .catch(() => null);
  }
  return configPromise;
}

async function postJSON(path, body, headers = {}) {
  let res;
  try {
    res = await fetch(path, {
      method: 'POST',
      headers: { 'content-type': 'application/json', ...headers },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError('network');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(data.error || 'network');
  return data;
}

export function redeemCode(code, deviceId) {
  return postJSON('/api/redeem', { code, deviceId });
}

// Обезличенная статистика воронки: только название события и источник рекламы.
export function track(name, source) {
  if (DEMO) return;
  try {
    const body = JSON.stringify({ name, source: source || undefined });
    if (globalThis.navigator?.sendBeacon) {
      globalThis.navigator.sendBeacon('/api/event', new Blob([body], { type: 'application/json' }));
    } else {
      fetch('/api/event', { method: 'POST', headers: { 'content-type': 'application/json' }, body, keepalive: true })
        .catch(() => {});
    }
  } catch {
    /* статистика не должна ломать приложение */
  }
}

function parseEvent(chunk) {
  let event = 'message';
  let data = '';
  for (const line of chunk.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) data += line.slice(5).trim();
  }
  return { event, data: data ? JSON.parse(data) : {} };
}

// Ответ ИИ приходит потоком (text/event-stream): meta, delta, replace, done, error.
export async function streamCoach(payload, { token, signal, onDelta, onReplace, onMeta }) {
  let res;
  try {
    res = await fetch('/api/coach', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        ...(token ? { authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      signal,
    });
  } catch (err) {
    if (err?.name === 'AbortError') throw err;
    throw new ApiError('network');
  }
  if (!res.ok || !res.body) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(data.error || (res.status === 503 ? 'unavailable' : 'network'));
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let index;
    while ((index = buffer.indexOf('\n\n')) >= 0) {
      const { event, data } = parseEvent(buffer.slice(0, index));
      buffer = buffer.slice(index + 2);
      if (event === 'delta') onDelta?.(data.text || '');
      else if (event === 'replace') onReplace?.(data.text || '');
      else if (event === 'meta') onMeta?.(data);
      else if (event === 'error') throw new ApiError(data.code || 'network');
    }
  }
}
