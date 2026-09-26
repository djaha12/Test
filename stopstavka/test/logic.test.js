import { test } from 'node:test';
import assert from 'node:assert/strict';

import { addDays, daysBetween, isValidISODate, lastNDays, toISODate } from '../public/js/logic/dates.js';
import { PGSI_MAX, pgsiCategory, scorePGSI } from '../public/js/logic/pgsi.js';
import { daysClean, goalProgress, moneySaved, nextMilestone, totalLost, yearlySpend } from '../public/js/logic/progress.js';
import {
  estimateProfitChance, expectedLoss, houseShare, marginFromOdds, mulberry32, normalCdf, profitChance, profitChanceNormal,
  returnPerUnit, simulatePath, winProbability,
} from '../public/js/logic/betting.js';
import { peakPeriod, resistedCount, triggerCounts, urgeSeries } from '../public/js/logic/insights.js';
import { formatMoney, formatNumber, formatPercent, parseAmount, pluralRu } from '../public/js/logic/format.js';

test('даты: разница в днях и сдвиги, включая границы месяцев и високосный год', () => {
  assert.equal(daysBetween('2026-09-01', '2026-09-26'), 25);
  assert.equal(daysBetween('2024-02-28', '2024-03-01'), 2);
  assert.equal(daysBetween('2026-03-01', '2026-02-28'), -1);
  assert.equal(addDays('2026-12-31', 1), '2027-01-01');
  assert.deepEqual(lastNDays(3, '2026-09-26'), ['2026-09-24', '2026-09-25', '2026-09-26']);
  assert.equal(toISODate(new Date(2026, 8, 5)), '2026-09-05');
  assert.ok(isValidISODate('2024-02-29'));
  assert.ok(!isValidISODate('2026-02-29'));
  assert.ok(!isValidISODate('26.09.2026'));
});

test('PGSI: сумма и категории по порогам шкалы', () => {
  assert.equal(PGSI_MAX, 27);
  assert.equal(scorePGSI([0, 0, 0, 0, 0, 0, 0, 0, 0]), 0);
  assert.equal(scorePGSI([3, 3, 3, 3, 3, 3, 3, 3, 3]), 27);
  assert.equal(pgsiCategory(0), 'none');
  assert.equal(pgsiCategory(1), 'low');
  assert.equal(pgsiCategory(2), 'low');
  assert.equal(pgsiCategory(3), 'moderate');
  assert.equal(pgsiCategory(7), 'moderate');
  assert.equal(pgsiCategory(8), 'high');
  assert.throws(() => scorePGSI([1, 2, 3]), RangeError);
  assert.throws(() => scorePGSI([0, 0, 0, 0, 0, 0, 0, 0, 4]), RangeError);
  assert.throws(() => pgsiCategory(28), RangeError);
});

test('прогресс: дни без ставок, сохранённые деньги с учётом срывов, цель и вехи', () => {
  const profile = { startDate: '2026-09-01', lastBetDate: '2026-09-12', weeklySpend: 7000 };
  assert.equal(daysClean(profile, '2026-09-26'), 14);
  assert.equal(daysClean({ lastBetDate: '2026-09-27' }, '2026-09-26'), 0);
  assert.equal(daysClean({}, '2026-09-26'), 0);
  // 25 дней × 1000 в день − 5000 потерь при срыве
  assert.equal(moneySaved(profile, [{ date: '2026-09-12', lost: 5000 }], '2026-09-26'), 20000);
  assert.equal(moneySaved(profile, [{ lost: 999999 }], '2026-09-26'), 0);
  assert.equal(moneySaved({ ...profile, weeklySpend: 0 }, [], '2026-09-26'), 0);
  assert.equal(totalLost([{ lost: 100 }, { lost: -5 }, { lost: 'x' }]), 100);
  assert.equal(goalProgress(5000, { amount: 20000 }), 0.25);
  assert.equal(goalProgress(50000, { amount: 20000 }), 1);
  assert.equal(goalProgress(100, { amount: 0 }), null);
  assert.equal(yearlySpend(1000), 52000);
  assert.equal(nextMilestone(0), 1);
  assert.equal(nextMilestone(7), 14);
  assert.equal(nextMilestone(400), null);
});

test('ставки: маржа рынка и доля букмекера', () => {
  assert.ok(Math.abs(marginFromOdds([1.9, 1.9]) - 0.0526) < 0.0001);
  assert.ok(Math.abs(returnPerUnit(0.05) - 1 / 1.05) < 1e-12);
  assert.ok(Math.abs(houseShare(0.05) - 0.047619) < 1e-6);
  // экспресс из 3 событий при марже 5% на событие отдаёт букмекеру ~13.6%
  assert.ok(Math.abs(houseShare(0.05, 3) - 0.1362) < 0.0001);
  assert.ok(Math.abs(winProbability(1.85, 0.05) - (1 / 1.85) / 1.05) < 1e-12);
  // 500 × 10 в неделю × 52 недели × 4.76%
  assert.equal(Math.round(expectedLoss({ stake: 500, perWeek: 10, margin: 0.05 })), 12381);
  assert.throws(() => marginFromOdds([1.5]), RangeError);
});

test('ставки: симуляция детерминирована и в среднем сходится к ожиданию', () => {
  const params = { odds: 1.85, stake: 100, perWeek: 10, margin: 0.05, seed: 42 };
  const a = simulatePath(params);
  const b = simulatePath(params);
  assert.deepEqual(a, b);
  assert.equal(a.length, 53);
  assert.equal(a[0].net, 0);

  // Среднее по многим годам близко к ожидаемому проигрышу (закон больших чисел).
  const rng = mulberry32(3);
  const p = winProbability(1.85, 0.05);
  let total = 0;
  const years = 400;
  for (let y = 0; y < years; y++) {
    for (let i = 0; i < 520; i++) total += (rng() < p ? 85 : -100);
  }
  const mean = total / years;
  const expected = -expectedLoss({ stake: 100, perWeek: 10, margin: 0.05 });
  assert.ok(Math.abs(mean - expected) < 250, `mean ${mean} vs ${expected}`);
});

test('ставки: шанс остаться в плюсе падает с горизонтом; экспрессы теряют в разы больше', () => {
  const base = { odds: 1.85, stake: 100, perWeek: 10, margin: 0.05, runs: 3000 };
  const year = profitChance(base);
  const three = profitChance({ ...base, weeks: 156 });
  // нормальное приближение: ~12% за год и ~2% за три года
  assert.ok(year > 0.08 && year < 0.17, `год: ${year}`);
  assert.ok(three < year / 2, `за три года шанс заметно меньше: ${three}`);

  // У экспресса разброс выше, поэтому шанс случайно оказаться в плюсе за год не меньше,
  // но средний проигрыш в разы больше, и с горизонтом шанс так же тает.
  const expressYear = profitChance({ ...base, legs: 5 });
  const expressThree = profitChance({ ...base, legs: 5, weeks: 156 });
  assert.ok(expressThree < expressYear, `экспресс: ${expressThree} против ${expressYear}`);
  const lossSingle = expectedLoss({ stake: 100, perWeek: 10, margin: 0.05 });
  const lossExpress = expectedLoss({ stake: 100, perWeek: 10, margin: 0.05, legs: 5 });
  assert.ok(lossExpress / lossSingle > 4.4 && lossExpress / lossSingle < 4.7, `${lossExpress / lossSingle}`);

  assert.throws(() => profitChance({ ...base, odds: 1 }), RangeError);
  assert.throws(() => profitChance({ ...base, perWeek: 0 }), RangeError);
});

test('ставки: нормальное приближение согласуется с симуляцией и быстро считает большие объёмы', () => {
  assert.ok(Math.abs(normalCdf(0) - 0.5) < 1e-7);
  assert.ok(Math.abs(normalCdf(1.96) - 0.975) < 1e-3);
  assert.ok(Math.abs(normalCdf(-1.96) - 0.025) < 1e-3);
  const params = { odds: 1.85, stake: 100, perWeek: 40, margin: 0.05, weeks: 104 };
  const mc = profitChance({ ...params, runs: 2000, seed: 11 });
  const approx = profitChanceNormal(params);
  assert.ok(Math.abs(mc - approx) < 0.03, `симуляция ${mc} против приближения ${approx}`);
  const started = Date.now();
  const heavy = estimateProfitChance({ odds: 1.85, stake: 100, perWeek: 500, margin: 0.05, weeks: 156 });
  assert.ok(Date.now() - started < 50, 'большой объём считается мгновенно');
  assert.ok(heavy < 0.001, `при 78 000 ставок шанс практически нулевой: ${heavy}`);
});

test('аналитика: ряд тяги, триггеры, устояли, пик по времени суток', () => {
  const state = {
    checkins: {
      '2026-09-25': { urge: 6, triggers: ['match', 'payday'], bet: false },
      '2026-09-26': { urge: 3, triggers: ['match'], bet: true },
      '2026-08-01': { urge: 9, triggers: ['stress'] },
    },
    urges: [
      { at: new Date(2026, 8, 25, 21, 0).toISOString(), before: 8, outcome: 'passed', trigger: 'match' },
      { at: new Date(2026, 8, 24, 22, 0).toISOString(), before: 5, outcome: 'bet' },
      { at: new Date(2026, 8, 23, 20, 30).toISOString(), before: 4, outcome: 'better' },
    ],
    relapses: [{ date: '2026-09-20', lost: 2000 }],
  };
  const series = urgeSeries(state, 14, '2026-09-26');
  assert.equal(series.length, 14);
  const byDate = Object.fromEntries(series.map((d) => [d.date, d]));
  assert.equal(byDate['2026-09-25'].value, 8);
  assert.equal(byDate['2026-09-26'].value, 3);
  assert.equal(byDate['2026-09-26'].bet, true);
  assert.equal(byDate['2026-09-24'].bet, true);
  assert.equal(byDate['2026-09-20'].bet, true);
  assert.equal(byDate['2026-09-21'].value, null);

  const triggers = triggerCounts(state);
  assert.deepEqual(triggers[0], { id: 'match', count: 3 });
  assert.equal(resistedCount(state.urges), 2);
  assert.deepEqual(peakPeriod(state.urges), { id: 'evening', count: 3 });
  assert.equal(peakPeriod(state.urges.slice(0, 2)), null);
});

test('формат: деньги, проценты, склонения, разбор ввода', () => {
  assert.equal(formatNumber(1234567), '1 234 567');
  assert.equal(formatNumber(-1500), '−1 500');
  assert.equal(formatMoney(36000, 'kg'), '36 000 сом');
  assert.equal(formatMoney(36000, 'kz'), '36 000 ₸');
  assert.equal(formatPercent(0.0476, 1), '4,8%');
  assert.equal(pluralRu(1, ['день', 'дня', 'дней']), 'день');
  assert.equal(pluralRu(3, ['день', 'дня', 'дней']), 'дня');
  assert.equal(pluralRu(11, ['день', 'дня', 'дней']), 'дней');
  assert.equal(pluralRu(21, ['день', 'дня', 'дней']), 'день');
  assert.equal(pluralRu(112, ['день', 'дня', 'дней']), 'дней');
  assert.equal(parseAmount('12 000 сом'), 12000);
  assert.equal(parseAmount('12,5'), 12.5);
  assert.ok(Number.isNaN(parseAmount('')));
  assert.ok(Number.isNaN(parseAmount('абв')));
});
