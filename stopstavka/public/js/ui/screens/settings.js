import { html, useEffect, useState } from '../../vendor/preact-htm.js';
import { LANG_NAMES, setLang, t } from '../../core/i18n.js';
import { isPremium, navigate, showToast, store } from '../../core/state.js';
import { isDemo } from '../../core/api.js';
import { Group, Icon, Segmented, Sheet, TopBar } from '../components.js';

export const APP_VERSION = '0.1.0';

// Событие установки PWA ловим как можно раньше и показываем кнопку, когда браузер готов.
let installEvent = null;
const installListeners = new Set();
globalThis.addEventListener?.('beforeinstallprompt', (e) => {
  e.preventDefault();
  installEvent = e;
  installListeners.forEach((fn) => fn(true));
});

function useInstallAvailable() {
  const [available, setAvailable] = useState(Boolean(installEvent));
  useEffect(() => {
    installListeners.add(setAvailable);
    return () => installListeners.delete(setAvailable);
  }, []);
  return available;
}

export function SettingsScreen({ state }) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const canInstall = useInstallAvailable();

  function changeLang(lang) {
    setLang(lang);
    store.set((s) => ({ ...s, lang }));
  }

  function exportData() {
    const blob = new Blob([store.exportJSON()], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = globalThis.document.createElement('a');
    a.href = url;
    a.download = `stopstavka-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function importData(e) {
    const file = e.currentTarget.files?.[0];
    e.currentTarget.value = '';
    if (!file) return;
    try {
      store.importJSON(await file.text());
      setLang(store.get().lang || 'ru');
      showToast(t('settings.import.done'));
    } catch {
      showToast(t('settings.import.error'));
    }
  }

  function deleteAll() {
    store.reset();
    setConfirmDelete(false);
    navigate('');
  }

  async function install() {
    if (!installEvent) return;
    installEvent.prompt();
    await installEvent.userChoice.catch(() => null);
    installEvent = null;
    installListeners.forEach((fn) => fn(false));
  }

  return html`<${TopBar} title=${t('settings.title')} back="home" />
    <main class="screen">
      <section class="card">
        <${Group} label=${t('settings.lang')}>
          <${Segmented} label=${t('settings.lang')} value=${state.lang || 'ru'} onChange=${changeLang}
            options=${Object.entries(LANG_NAMES).map(([value, label]) => ({ value, label }))} />
        <//>
        <${Group} label=${t('settings.country')}>
          <${Segmented} label=${t('settings.country')} value=${state.country || 'kg'} onChange=${(country) => store.set((s) => ({ ...s, country }))}
            options=${[{ value: 'kg', label: `${t('country.kg')} · сом` }, { value: 'kz', label: `${t('country.kz')} · ₸` }]} />
        <//>
      </section>

      <nav class="card" aria-label=${t('settings.title')}>
        <a class="row between" href="#plan" style="color:inherit;text-decoration:none;min-height:44px">${t('settings.plan')}<${Icon} name="chevron" /></a>
        <a class="row between" href="#test" style="color:inherit;text-decoration:none;min-height:44px">${t('settings.retest')}<${Icon} name="chevron" /></a>
        <a class="row between" href="#premium" style="color:inherit;text-decoration:none;min-height:44px">
          ${t('settings.premium')}${isPremium(state) ? html` <span class="badge">✓</span>` : null}<${Icon} name="chevron" />
        </a>
      </nav>

      ${canInstall ? html`<button type="button" class="btn secondary block" onClick=${install}><${Icon} name="download" size=${20} />${t('settings.install')}</button>` : null}

      <section class="card">
        <h2>${t('settings.data')}</h2>
        ${isDemo() ? null : html`<button type="button" class="btn secondary" onClick=${exportData}><${Icon} name="download" size=${20} />${t('settings.export')}</button>`}
        <label class="btn secondary">
          <${Icon} name="upload" size=${20} />${t('settings.import')}
          <input type="file" accept="application/json,.json" class="sr-only" onChange=${importData} />
        </label>
        <button type="button" class="btn ghost" style="color:var(--critical)" onClick=${() => setConfirmDelete(true)}>
          <${Icon} name="trash" size=${20} />${t('settings.delete')}
        </button>
      </section>

      <section class="card">
        <h2>${t('settings.about')}</h2>
        <p>${t('settings.about.text')}</p>
        <p class="tiny muted">${t('settings.version', { v: APP_VERSION })}</p>
      </section>
    </main>
    <${Sheet} open=${confirmDelete} onClose=${() => setConfirmDelete(false)} title=${t('settings.delete')}>
      <p>${t('settings.delete.confirm')}</p>
      <button type="button" class="btn danger block" onClick=${deleteAll}>${t('settings.delete.yes')}</button>
      <button type="button" class="btn secondary block" onClick=${() => setConfirmDelete(false)}>${t('common.cancel')}</button>
    <//>`;
}
