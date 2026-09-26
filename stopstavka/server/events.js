import { utcDay } from './db.js';

// Обезличенная воронка для рекламы: только название события, день и источник (utm_source).
export const EVENTS = new Set([
  'app_open', 'onboarding_start', 'test_done', 'setup_done', 'sos_start', 'sos_passed', 'sos_bet',
  'checkin', 'relapse', 'protect_step', 'truth_calc', 'share', 'premium_view', 'premium_redeemed',
]);

export function cleanSource(source) {
  return typeof source === 'string' && /^[a-z0-9_.-]{1,40}$/i.test(source) ? source.toLowerCase() : '';
}

export function recordEvent(db, { name, source, now = Date.now() }) {
  if (!EVENTS.has(name)) return false;
  db.prepare(`INSERT INTO events (day, name, source, count) VALUES (?, ?, ?, 1)
    ON CONFLICT (day, name, source) DO UPDATE SET count = count + 1`).run(utcDay(now), name, cleanSource(source));
  return true;
}

export function eventStats(db, { days = 30, now = Date.now() } = {}) {
  const since = utcDay(now - (days - 1) * 86400000);
  const rows = db.prepare(`SELECT name, source, SUM(count) AS count FROM events WHERE day >= ?
    GROUP BY name, source ORDER BY name, count DESC`).all(since);
  const totals = {};
  const bySource = {};
  for (const row of rows) {
    totals[row.name] = (totals[row.name] || 0) + row.count;
    const src = row.source || '(direct)';
    bySource[src] = bySource[src] || {};
    bySource[src][row.name] = row.count;
  }
  return { since, totals, bySource };
}
