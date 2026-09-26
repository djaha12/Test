// Даты храним строками YYYY-MM-DD в часовом поясе устройства.
// Разницу считаем через UTC, чтобы переходы времени не сдвигали счёт дней.

const ISO_RE = /^(\d{4})-(\d{2})-(\d{2})$/;

export function toISODate(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function isValidISODate(value) {
  if (typeof value !== 'string') return false;
  const match = ISO_RE.exec(value);
  if (!match) return false;
  const [, y, m, d] = match.map(Number);
  const utc = new Date(Date.UTC(y, m - 1, d));
  return utc.getUTCFullYear() === y && utc.getUTCMonth() === m - 1 && utc.getUTCDate() === d;
}

function toUTC(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return Date.UTC(y, m - 1, d);
}

export function daysBetween(fromISO, toISO) {
  return Math.round((toUTC(toISO) - toUTC(fromISO)) / 86400000);
}

export function addDays(iso, count) {
  return new Date(toUTC(iso) + count * 86400000).toISOString().slice(0, 10);
}

// Последние n дней, заканчивая сегодняшним: [сегодня-(n-1), ..., сегодня].
export function lastNDays(count, todayISO) {
  return Array.from({ length: count }, (_, i) => addDays(todayISO, i - (count - 1)));
}

// Дата из ISO-времени события (например, "2026-09-26T21:15:00.000Z") в локальном дне устройства.
export function localDateOf(isoDateTime) {
  return toISODate(new Date(isoDateTime));
}
