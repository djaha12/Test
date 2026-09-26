// Простой лимит запросов в памяти процесса: окно фиксированной длины на ключ (например, IP).
export function createLimiter({ windowMs, max, now = () => Date.now() }) {
  const hits = new Map();
  let lastSweep = now();

  function sweep(t) {
    if (t - lastSweep < windowMs) return;
    for (const [key, entry] of hits) if (entry.reset <= t) hits.delete(key);
    lastSweep = t;
  }

  return {
    hit(key) {
      const t = now();
      sweep(t);
      let entry = hits.get(key);
      if (!entry || entry.reset <= t) {
        entry = { count: 0, reset: t + windowMs };
        hits.set(key, entry);
      }
      entry.count++;
      return { allowed: entry.count <= max, retryAfter: Math.ceil((entry.reset - t) / 1000) };
    },
  };
}
