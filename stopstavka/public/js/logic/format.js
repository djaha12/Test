// Форматирование чисел и денег без зависимости от Intl, чтобы вывод был одинаковым везде.

const NBSP = ' ';

export const CURRENCY = { kg: 'сом', kz: '₸' };

export function formatNumber(value) {
  const rounded = Math.round(Number(value) || 0);
  const sign = rounded < 0 ? '−' : '';
  const digits = String(Math.abs(rounded));
  return sign + digits.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP);
}

export function formatMoney(value, country) {
  return `${formatNumber(value)}${NBSP}${CURRENCY[country] || CURRENCY.kg}`;
}

export function formatPercent(share, digits = 0) {
  const pct = (Number(share) || 0) * 100;
  return `${pct.toFixed(digits).replace('.', ',')}%`;
}

// Русская форма множественного числа: plural(5, ['день', 'дня', 'дней']) → 'дней'.
export function pluralRu(n, forms) {
  const abs = Math.abs(n) % 100;
  const last = abs % 10;
  if (abs > 10 && abs < 20) return forms[2];
  if (last > 1 && last < 5) return forms[1];
  if (last === 1) return forms[0];
  return forms[2];
}

// Разбор суммы, введённой человеком: «12 000», «12000 сом», «12,5».
export function parseAmount(input) {
  if (typeof input === 'number') return Number.isFinite(input) && input >= 0 ? input : NaN;
  const cleaned = String(input ?? '').replace(/[\s ]/g, '').replace(',', '.').replace(/[^\d.]/g, '');
  if (!cleaned) return NaN;
  const value = Number(cleaned);
  return Number.isFinite(value) && value >= 0 ? value : NaN;
}
