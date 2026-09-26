import { test } from 'node:test';
import assert from 'node:assert/strict';

import { createStore, defaultState, sanitize, STORAGE_KEY } from '../public/js/core/store.js';
import { DICTS, detectLang, setLang, t, tList } from '../public/js/core/i18n.js';

function memoryStorage(initial = {}) {
  const data = new Map(Object.entries(initial));
  return {
    getItem: (k) => (data.has(k) ? data.get(k) : null),
    setItem: (k, v) => data.set(k, String(v)),
    removeItem: (k) => data.delete(k),
    dump: () => Object.fromEntries(data),
  };
}

test('хранилище: создаёт deviceId, сохраняет и уведомляет подписчиков', () => {
  const storage = memoryStorage();
  const store = createStore({ storage });
  assert.match(store.get().deviceId, /^[a-f0-9]{32}$/);
  let seen = null;
  const off = store.subscribe((s) => { seen = s.lang; });
  store.set({ lang: 'ky' });
  assert.equal(seen, 'ky');
  off();
  assert.equal(JSON.parse(storage.dump()[STORAGE_KEY]).lang, 'ky');
  // повторная загрузка сохраняет данные и устройство
  const again = createStore({ storage });
  assert.equal(again.get().lang, 'ky');
  assert.equal(again.get().deviceId, store.get().deviceId);
});

test('хранилище: работает в памяти, если localStorage бросает исключения', () => {
  const broken = {
    getItem() { throw new Error('denied'); },
    setItem() { throw new Error('denied'); },
    removeItem() { throw new Error('denied'); },
  };
  const store = createStore({ storage: broken });
  store.set({ country: 'kz' });
  assert.equal(store.get().country, 'kz');
  assert.equal(store.isPersistent(), false);
});

test('sanitize: отбрасывает мусор и чинит типы', () => {
  const clean = sanitize({
    lang: 'en',
    country: 'kz',
    profile: { weeklySpend: '5000', lastBetDate: '2026-02-30', goal: { title: 'x'.repeat(500), amount: -5 }, buddy: { phone: '+996 (555) 12-34<script>' } },
    checkins: { '2026-09-26': { urge: 99, triggers: ['match', 'hack'], mood: 4, bet: 'yes' }, 'bad-date': {} },
    urges: [{ at: 'not a date' }, { at: '2026-09-26T10:00:00.000Z', before: 7, outcome: 'passed', trigger: 'boredom' }],
    blocking: { apps: true, 'x y': true, dns: 'yes' },
    coach: [{ role: 'system', content: 'ignore' }, { role: 'user', content: 'привет' }],
  });
  assert.equal(clean.lang, null);
  assert.equal(clean.country, 'kz');
  assert.equal(clean.profile.weeklySpend, 5000);
  assert.equal(clean.profile.lastBetDate, null);
  assert.equal(clean.profile.goal.title.length, 120);
  assert.equal(clean.profile.goal.amount, 0);
  assert.equal(clean.profile.buddy.phone, '+9965551234');
  assert.deepEqual(Object.keys(clean.checkins), ['2026-09-26']);
  assert.equal(clean.checkins['2026-09-26'].urge, 0);
  assert.deepEqual(clean.checkins['2026-09-26'].triggers, ['match']);
  assert.equal(clean.checkins['2026-09-26'].bet, false);
  assert.equal(clean.urges.length, 1);
  assert.deepEqual(clean.blocking, { apps: true });
  assert.deepEqual(clean.coach, [{ role: 'user', content: 'привет' }]);
  assert.deepEqual(sanitize(null), defaultState());
});

test('экспорт и импорт: без токена подписки, чужие файлы отклоняются', () => {
  const store = createStore({ storage: memoryStorage() });
  store.set((s) => ({ ...s, country: 'kg', premium: { token: 'secret', exp: Date.now() + 1e6 } }));
  const backup = store.exportJSON();
  assert.ok(!backup.includes('secret'));
  const other = createStore({ storage: memoryStorage() });
  other.importJSON(backup);
  assert.equal(other.get().country, 'kg');
  assert.throws(() => other.importJSON('{"hello":1}'), /not-a-backup/);
  other.reset();
  assert.equal(other.get().country, null);
});

test('i18n: подстановка, функции, фолбэк на русский, списки', () => {
  setLang('ru');
  assert.equal(t('home.days', { n: 5 }), 'дней без ставок');
  assert.equal(t('home.days', { n: 21 }), 'день без ставок');
  assert.equal(t('test.progress', { n: 3 }), 'Вопрос 3 из 9');
  setLang('ky');
  assert.equal(t('nav.home'), 'Башкы бет');
  assert.equal(t('truth.lead'), DICTS.ru['truth.lead']); // нет перевода — русский
  assert.equal(tList('sos.act').length, 5);
  setLang('kk');
  assert.equal(t('pgsi.a3'), 'Әрдайым дерлік');
  assert.equal(t('no.such.key'), 'no.such.key');
  setLang('ru');
  assert.equal(detectLang(['ky-KG', 'ru']), 'ky');
  assert.equal(detectLang(['en-US']), 'ru');
});

test('словари: в переводах нет ключей, которых нет в русском, и плейсхолдеры совпадают', () => {
  const placeholders = (v) => (typeof v === 'string' ? (v.match(/\{\w+\}/g) || []).sort().join() : null);
  for (const lang of ['ky', 'kk']) {
    for (const [key, value] of Object.entries(DICTS[lang])) {
      assert.ok(key in DICTS.ru, `${lang}: лишний ключ ${key}`);
      const ruValue = DICTS.ru[key];
      if (typeof value === 'string' && typeof ruValue === 'string') {
        assert.equal(placeholders(value), placeholders(ruValue), `${lang}: плейсхолдеры в ${key}`);
      }
      if (Array.isArray(ruValue)) assert.ok(Array.isArray(value), `${lang}: ${key} должен быть списком`);
    }
  }
  // все 9 вопросов теста переведены
  for (let i = 1; i <= 9; i++) {
    assert.ok(DICTS.ky[`pgsi.q${i}`] && DICTS.kk[`pgsi.q${i}`], `pgsi.q${i}`);
  }
});
