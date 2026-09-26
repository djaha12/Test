// Состояние приложения живёт только на устройстве (localStorage).
// Хранилище может быть недоступно (приватный режим, запрет сайта) — тогда работаем в памяти.

import { isValidISODate } from '../logic/dates.js';
import { TRIGGERS } from '../logic/insights.js';

export const STORAGE_KEY = 'stopstavka:v1';
export const SCHEMA_VERSION = 1;

const LANGS = ['ru', 'ky', 'kk'];
const COUNTRIES = ['kg', 'kz'];
const OUTCOMES = ['passed', 'better', 'still', 'bet'];
const MAX_TEXT = 500;
const MAX_ITEMS = 2000;
const MAX_COACH_MESSAGES = 40;

export function defaultState() {
  return {
    v: SCHEMA_VERSION,
    lang: null,
    country: null,
    onboarded: false,
    profile: {
      startDate: null,
      lastBetDate: null,
      weeklySpend: 0,
      reasons: [],
      goal: { title: '', amount: 0 },
      buddy: { name: '', phone: '' },
    },
    pgsi: [],
    checkins: {},
    urges: [],
    relapses: [],
    blocking: {},
    truth: { preset: 'single', odds: 1.85, stake: 500, perWeek: 10, legs: 1, margin: 0.05 },
    premium: { token: null, exp: null },
    deviceId: null,
    utm: null,
    coach: [],
  };
}

function text(value, max = MAX_TEXT) {
  return typeof value === 'string' ? value.slice(0, max) : '';
}

function num(value, min, max, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) && n >= min && n <= max ? n : fallback;
}

function date(value) {
  return isValidISODate(value) ? value : null;
}

// Приводит любые данные (в том числе из импортированного файла) к ожидаемой форме.
export function sanitize(raw) {
  const base = defaultState();
  if (!raw || typeof raw !== 'object') return base;
  const p = raw.profile && typeof raw.profile === 'object' ? raw.profile : {};

  const checkins = {};
  if (raw.checkins && typeof raw.checkins === 'object') {
    for (const [day, c] of Object.entries(raw.checkins).slice(-MAX_ITEMS)) {
      if (!isValidISODate(day) || !c || typeof c !== 'object') continue;
      checkins[day] = {
        mood: num(c.mood, 1, 5, 3),
        urge: num(c.urge, 0, 10, 0),
        triggers: Array.isArray(c.triggers) ? c.triggers.filter((t) => TRIGGERS.includes(t)) : [],
        bet: c.bet === true,
        lost: num(c.lost, 0, 1e10, 0),
        note: text(c.note),
      };
    }
  }

  const list = (value) => (Array.isArray(value) ? value.slice(-MAX_ITEMS) : []);

  return {
    ...base,
    lang: LANGS.includes(raw.lang) ? raw.lang : null,
    country: COUNTRIES.includes(raw.country) ? raw.country : null,
    onboarded: raw.onboarded === true,
    profile: {
      startDate: date(p.startDate),
      lastBetDate: date(p.lastBetDate),
      weeklySpend: num(p.weeklySpend, 0, 1e9, 0),
      reasons: Array.isArray(p.reasons) ? p.reasons.map((r) => text(r, 120)).filter(Boolean).slice(0, 12) : [],
      goal: { title: text(p.goal?.title, 120), amount: num(p.goal?.amount, 0, 1e10, 0) },
      buddy: { name: text(p.buddy?.name, 60), phone: text(p.buddy?.phone, 30).replace(/[^\d+]/g, '') },
    },
    pgsi: list(raw.pgsi)
      .filter((r) => r && isValidISODate(r.date) && Array.isArray(r.answers) && r.answers.length === 9)
      .map((r) => ({ date: r.date, answers: r.answers.map((a) => num(a, 0, 3, 0)), score: num(r.score, 0, 27, 0) })),
    checkins,
    urges: list(raw.urges)
      .filter((u) => u && typeof u.at === 'string' && !Number.isNaN(Date.parse(u.at)))
      .map((u) => ({
        id: text(u.id, 40),
        at: u.at,
        before: num(u.before, 1, 10, 5),
        outcome: OUTCOMES.includes(u.outcome) ? u.outcome : null,
        trigger: TRIGGERS.includes(u.trigger) ? u.trigger : null,
      })),
    relapses: list(raw.relapses)
      .filter((r) => r && isValidISODate(r.date))
      .map((r) => ({
        date: r.date,
        lost: num(r.lost, 0, 1e10, 0),
        triggers: Array.isArray(r.triggers) ? r.triggers.filter((t) => TRIGGERS.includes(t)) : [],
      })),
    blocking: raw.blocking && typeof raw.blocking === 'object'
      ? Object.fromEntries(Object.entries(raw.blocking).filter(([k, v]) => /^[a-z0-9-]{1,40}$/.test(k) && v === true))
      : {},
    truth: {
      preset: ['single', 'live', 'express3', 'express5'].includes(raw.truth?.preset) ? raw.truth.preset : base.truth.preset,
      odds: num(raw.truth?.odds, 1.01, 100, base.truth.odds),
      stake: num(raw.truth?.stake, 1, 1e9, base.truth.stake),
      perWeek: Math.round(num(raw.truth?.perWeek, 1, 500, base.truth.perWeek)),
      legs: Math.round(num(raw.truth?.legs, 1, 10, base.truth.legs)),
      margin: num(raw.truth?.margin, 0, 0.49, base.truth.margin),
    },
    premium: {
      token: typeof raw.premium?.token === 'string' ? raw.premium.token.slice(0, 600) : null,
      exp: num(raw.premium?.exp, 0, 1e13, 0) || null,
    },
    deviceId: /^[a-f0-9]{32}$/.test(raw.deviceId) ? raw.deviceId : null,
    utm: raw.utm && typeof raw.utm === 'object'
      ? { source: text(raw.utm.source, 60), campaign: text(raw.utm.campaign, 60) }
      : null,
    coach: list(raw.coach)
      .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
      .slice(-MAX_COACH_MESSAGES)
      .map((m) => ({ role: m.role, content: text(m.content, 4000) })),
  };
}

export function randomId() {
  const bytes = new Uint8Array(16);
  globalThis.crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

export function createStore({ storage } = {}) {
  let persistent = Boolean(storage);
  let state;
  try {
    const raw = storage?.getItem(STORAGE_KEY);
    state = sanitize(raw ? JSON.parse(raw) : null);
  } catch {
    state = defaultState();
    persistent = false;
  }
  if (!state.deviceId) state.deviceId = randomId();

  const listeners = new Set();

  function save() {
    if (!storage) return;
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(state));
      persistent = true;
    } catch {
      persistent = false;
    }
  }

  function set(update) {
    const next = typeof update === 'function' ? update(state) : { ...state, ...update };
    state = next;
    save();
    for (const fn of listeners) fn(state);
  }

  save();

  return {
    get: () => state,
    set,
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    isPersistent: () => persistent,
    exportJSON: () => JSON.stringify({ app: 'stopstavka', ...state, premium: { token: null, exp: null } }, null, 2),
    importJSON(json) {
      const parsed = JSON.parse(json);
      if (!parsed || parsed.app !== 'stopstavka') throw new Error('not-a-backup');
      set({ ...sanitize(parsed), deviceId: state.deviceId, premium: state.premium });
    },
    reset() {
      try { storage?.removeItem(STORAGE_KEY); } catch { /* хранилище недоступно */ }
      set({ ...defaultState(), deviceId: randomId() });
    },
  };
}

// Доступ к localStorage в браузере может бросать исключение — оборачиваем.
export function browserStorage() {
  try {
    const s = globalThis.localStorage;
    const probe = '__stopstavka_probe__';
    s.setItem(probe, '1');
    s.removeItem(probe);
    return s;
  } catch {
    return null;
  }
}
