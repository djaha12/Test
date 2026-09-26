import ru from '../content/ru.js';
import ky from '../content/ky.js';
import kk from '../content/kk.js';

export const DICTS = { ru, ky, kk };
export const LANG_NAMES = { ru: 'Русский', ky: 'Кыргызча', kk: 'Қазақша' };

let lang = 'ru';

export function detectLang(preferred = []) {
  for (const tag of preferred) {
    const code = String(tag).toLowerCase().slice(0, 2);
    if (code === 'ky' || code === 'kk' || code === 'ru') return code;
  }
  return 'ru';
}

export function setLang(next) {
  if (DICTS[next]) lang = next;
  if (globalThis.document) globalThis.document.documentElement.lang = lang;
}

export function getLang() {
  return lang;
}

// Строка из словаря текущего языка; если перевода нет — из русского. {name} подставляется из params.
export function t(key, params = {}) {
  const entry = DICTS[lang][key] ?? DICTS.ru[key];
  if (entry === undefined) return key;
  const value = typeof entry === 'function' ? entry(params) : entry;
  if (typeof value !== 'string') return key;
  return value.replace(/\{(\w+)\}/g, (match, name) => (params[name] !== undefined ? String(params[name]) : match));
}

// Списки (советы, шаги): массив строк из словаря текущего языка или русского.
export function tList(key) {
  const entry = DICTS[lang][key] ?? DICTS.ru[key];
  return Array.isArray(entry) ? entry : [];
}
