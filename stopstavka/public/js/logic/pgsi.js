// PGSI (Problem Gambling Severity Index) — 9 вопросов, ответы 0–3, сумма 0–27.
// Пороги по шкале: 0 — без проблем, 1–2 — низкий риск, 3–7 — умеренный риск, 8+ — проблемная игра.

export const PGSI_ITEMS = 9;
export const PGSI_MAX = PGSI_ITEMS * 3;

export function isValidAnswers(answers) {
  return Array.isArray(answers)
    && answers.length === PGSI_ITEMS
    && answers.every((a) => Number.isInteger(a) && a >= 0 && a <= 3);
}

export function scorePGSI(answers) {
  if (!isValidAnswers(answers)) throw new RangeError('PGSI: нужно 9 ответов от 0 до 3');
  return answers.reduce((sum, a) => sum + a, 0);
}

export function pgsiCategory(score) {
  if (!Number.isInteger(score) || score < 0 || score > PGSI_MAX) throw new RangeError('PGSI: балл вне шкалы');
  if (score === 0) return 'none';
  if (score <= 2) return 'low';
  if (score <= 7) return 'moderate';
  return 'high';
}
