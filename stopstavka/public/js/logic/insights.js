import { lastNDays, localDateOf } from './dates.js';

// Идентификаторы триггеров; подписи — в словарях (trigger.<id>).
export const TRIGGERS = ['match', 'payday', 'boredom', 'stress', 'loneliness', 'alcohol', 'ads', 'friends', 'chasing', 'night'];

// Сила тяги по дням: максимум из дневной отметки и SOS-событий этого дня (0–10), null — нет данных.
export function urgeSeries(state, days, todayISO) {
  const byDay = new Map(lastNDays(days, todayISO).map((d) => [d, { date: d, value: null, bet: false }]));
  for (const [date, c] of Object.entries(state.checkins || {})) {
    const day = byDay.get(date);
    if (!day) continue;
    if (Number.isFinite(c.urge)) day.value = Math.max(day.value ?? 0, c.urge);
    if (c.bet) day.bet = true;
  }
  for (const u of state.urges || []) {
    const day = byDay.get(localDateOf(u.at));
    if (!day) continue;
    if (Number.isFinite(u.before)) day.value = Math.max(day.value ?? 0, u.before);
    if (u.outcome === 'bet') day.bet = true;
  }
  for (const r of state.relapses || []) {
    const day = byDay.get(r.date);
    if (day) day.bet = true;
  }
  return [...byDay.values()];
}

export function triggerCounts(state) {
  const counts = new Map();
  const add = (id) => { if (TRIGGERS.includes(id)) counts.set(id, (counts.get(id) || 0) + 1); };
  for (const c of Object.values(state.checkins || {})) (c.triggers || []).forEach(add);
  for (const u of state.urges || []) if (u.trigger) add(u.trigger);
  return [...counts.entries()]
    .map(([id, count]) => ({ id, count }))
    .sort((a, b) => b.count - a.count || TRIGGERS.indexOf(a.id) - TRIGGERS.indexOf(b.id));
}

export function resistedCount(urges = []) {
  return urges.filter((u) => u.outcome && u.outcome !== 'bet').length;
}

const PERIODS = [
  { id: 'night', from: 0, to: 6 },
  { id: 'morning', from: 6, to: 12 },
  { id: 'day', from: 12, to: 18 },
  { id: 'evening', from: 18, to: 24 },
];

// Время суток, когда чаще всего нажимали SOS (нужно минимум 3 события).
export function peakPeriod(urges = []) {
  if (urges.length < 3) return null;
  const counts = PERIODS.map((p) => ({ id: p.id, count: 0 }));
  for (const u of urges) {
    const hour = new Date(u.at).getHours();
    const idx = PERIODS.findIndex((p) => hour >= p.from && hour < p.to);
    counts[idx].count++;
  }
  counts.sort((a, b) => b.count - a.count);
  return counts[0].count > 0 ? counts[0] : null;
}
