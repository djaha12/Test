import { html, render } from './vendor/preact-htm.js';
import { detectLang, setLang } from './core/i18n.js';
import { store } from './core/state.js';
import { isDemo, track } from './core/api.js';
import { App } from './ui/app.js';

const initial = store.get();
setLang(initial.lang || detectLang(globalThis.navigator?.languages || []));

// Источник рекламы (utm_source) запоминаем один раз — для обезличенной статистики воронки.
try {
  const params = new URLSearchParams(globalThis.location.search);
  const source = params.get('utm_source');
  if (source && !initial.utm) {
    store.set((s) => ({ ...s, utm: { source: source.slice(0, 60), campaign: (params.get('utm_campaign') || '').slice(0, 60) } }));
  }
} catch { /* адрес без параметров */ }

render(html`<${App} />`, globalThis.document.getElementById('app'));
track('app_open', store.get().utm?.source);

const secureOrigin = globalThis.location.protocol === 'https:' || globalThis.location.hostname === 'localhost';
if (secureOrigin && !isDemo() && 'serviceWorker' in globalThis.navigator) {
  globalThis.navigator.serviceWorker.register('sw.js').catch(() => {});
}
