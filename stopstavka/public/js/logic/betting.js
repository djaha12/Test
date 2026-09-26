// Математика ставок: маржа букмекера, ожидаемый результат и симуляция.
//
// Модель: букмекер закладывает маржу m в коэффициенты (сумма обратных коэффициентов рынка = 1 + m).
// Честная вероятность исхода с коэффициентом k: p = (1 / k) / (1 + m).
// Тогда на каждую поставленную единицу игрок в среднем получает обратно 1 / (1 + m),
// а в экспрессе из n событий — (1 / (1 + m))^n.

export const PRESETS = {
  single: { legs: 1, margin: 0.05 },
  live: { legs: 1, margin: 0.07 },
  express3: { legs: 3, margin: 0.05 },
  express5: { legs: 5, margin: 0.05 },
};

export function marginFromOdds(odds) {
  if (!Array.isArray(odds) || odds.length < 2 || odds.some((k) => !(k > 1))) {
    throw new RangeError('Нужны минимум два коэффициента больше 1');
  }
  return odds.reduce((sum, k) => sum + 1 / k, 0) - 1;
}

export function returnPerUnit(margin, legs = 1) {
  return Math.pow(1 / (1 + margin), legs);
}

// Какая доля каждой ставки в среднем остаётся у букмекера.
export function houseShare(margin, legs = 1) {
  return 1 - returnPerUnit(margin, legs);
}

export function winProbability(odds, margin, legs = 1) {
  return Math.pow(1 / odds / (1 + margin), legs);
}

export function expectedLoss({ stake, perWeek, weeks = 52, margin, legs = 1 }) {
  return stake * perWeek * weeks * houseShare(margin, legs);
}

export function totalStaked({ stake, perWeek, weeks = 52 }) {
  return stake * perWeek * weeks;
}

// Детерминированный генератор (mulberry32): одинаковый seed даёт одинаковую «историю».
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function next() {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function checkParams({ odds, stake, perWeek, weeks = 52, margin, legs = 1 }) {
  if (!(odds > 1)) throw new RangeError('Коэффициент должен быть больше 1');
  if (!(stake > 0)) throw new RangeError('Ставка должна быть больше 0');
  if (!Number.isInteger(perWeek) || perWeek < 1 || perWeek > 500) throw new RangeError('Ставок в неделю: от 1 до 500');
  if (!Number.isInteger(weeks) || weeks < 1 || weeks > 520) throw new RangeError('Недель: от 1 до 520');
  if (!(margin >= 0 && margin < 0.5)) throw new RangeError('Маржа: от 0 до 50%');
  if (!Number.isInteger(legs) || legs < 1 || legs > 10) throw new RangeError('Событий в экспрессе: от 1 до 10');
}

function runYear(rng, { odds, stake, perWeek, weeks, margin, legs }, onWeek) {
  const p = winProbability(odds, margin, legs);
  const payout = stake * Math.pow(odds, legs);
  let net = 0;
  for (let w = 1; w <= weeks; w++) {
    for (let b = 0; b < perWeek; b++) {
      net -= stake;
      if (rng() < p) net += payout;
    }
    if (onWeek) onWeek(w, net);
  }
  return net;
}

// Одна возможная история: итог (выигрыш минус проигрыш) после каждой недели.
export function simulatePath(params) {
  const full = { weeks: 52, legs: 1, ...params };
  checkParams(full);
  const rng = mulberry32(full.seed ?? 1);
  const points = [{ week: 0, net: 0 }];
  runYear(rng, full, (week, net) => points.push({ week, net: Math.round(net) }));
  return points;
}

// Функция нормального распределения (приближение Абрамовица — Стиган для erf, точность ~1e-7).
export function normalCdf(z) {
  const sign = z < 0 ? -1 : 1;
  const x = Math.abs(z) / Math.SQRT2;
  const t = 1 / (1 + 0.3275911 * x);
  const poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  const erf = 1 - poly * Math.exp(-x * x);
  return 0.5 * (1 + sign * erf);
}

// Шанс быть в плюсе через центральную предельную теорему: подходит, когда ставок много.
export function profitChanceNormal(params) {
  const { odds, stake, perWeek, weeks = 52, margin, legs = 1 } = params;
  checkParams({ odds, stake, perWeek, weeks, margin, legs });
  const p = winProbability(odds, margin, legs);
  const win = stake * (Math.pow(odds, legs) - 1);
  const mean = p * win - (1 - p) * stake;
  const variance = p * win * win + (1 - p) * stake * stake - mean * mean;
  const n = perWeek * weeks;
  return 1 - normalCdf((0 - n * mean) / Math.sqrt(n * variance));
}

// Для интерфейса: точная симуляция, пока ставок немного, и быстрое приближение, когда их тысячи.
export function estimateProfitChance(params) {
  const { perWeek, weeks = 52 } = params;
  return perWeek * weeks <= 6000
    ? profitChance({ runs: 1500, ...params })
    : profitChanceNormal(params);
}

// Доля историй (из runs), в которых игрок в конце периода в плюсе.
export function profitChance(params) {
  const full = { weeks: 52, legs: 1, runs: 2000, ...params };
  checkParams(full);
  const rng = mulberry32(full.seed ?? 7);
  let ahead = 0;
  for (let r = 0; r < full.runs; r++) {
    if (runYear(rng, full) > 0) ahead++;
  }
  return ahead / full.runs;
}
