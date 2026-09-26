import { daysBetween } from './dates.js';

// Вехи, которые приложение отмечает на главном экране.
export const MILESTONES = [1, 3, 7, 14, 30, 60, 90, 180, 365];

export function daysClean(profile, todayISO) {
  if (!profile?.lastBetDate) return 0;
  return Math.max(0, daysBetween(profile.lastBetDate, todayISO));
}

export function totalLost(relapses = []) {
  return relapses.reduce((sum, r) => sum + (Number(r.lost) > 0 ? Number(r.lost) : 0), 0);
}

// Сколько денег не ушло на ставки с начала пути: обычные траты в неделю × прошедшие дни − потери при срывах.
export function moneySaved(profile, relapses, todayISO) {
  if (!profile?.startDate || !(profile.weeklySpend > 0)) return 0;
  const days = Math.max(0, daysBetween(profile.startDate, todayISO));
  const gross = (profile.weeklySpend / 7) * days;
  return Math.max(0, Math.round(gross - totalLost(relapses)));
}

export function goalProgress(saved, goal) {
  if (!goal || !(goal.amount > 0)) return null;
  return Math.min(1, Math.max(0, saved / goal.amount));
}

export function yearlySpend(weeklySpend) {
  return Math.round((weeklySpend > 0 ? weeklySpend : 0) * 52);
}

export function nextMilestone(days) {
  return MILESTONES.find((m) => m > days) ?? null;
}
