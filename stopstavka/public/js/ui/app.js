import { html, useEffect, useState } from '../vendor/preact-htm.js';
import { t } from '../core/i18n.js';
import { store, useAppState, useRoute } from '../core/state.js';
import { Icon, ToastHost } from './components.js';
import { FirstStep, SetupScreen, TestScreen, Welcome } from './screens/onboarding.js';
import { HomeScreen } from './screens/home.js';
import { SosScreen } from './screens/sos.js';
import { JournalScreen } from './screens/journal.js';
import { ProtectScreen } from './screens/protect.js';
import { TruthScreen } from './screens/truth.js';
import { HelpScreen } from './screens/help.js';
import { CoachScreen } from './screens/coach.js';
import { PremiumScreen } from './screens/premium.js';
import { SettingsScreen } from './screens/settings.js';

// Экраны, доступные до завершения знакомства с приложением.
const OPEN_ROUTES = new Set(['test', 'setup', 'first-step', 'sos', 'help', 'truth']);
const ONBOARDING = new Set(['test', 'setup', 'first-step']);
const NO_NAV = new Set(['', 'welcome', 'test', 'setup', 'first-step', 'sos']);
const TAB_OF = { truth: 'protect', coach: 'help', relapse: 'home' };

function BottomNav({ route }) {
  const active = TAB_OF[route] || route;
  const tab = (id, icon) => html`<a class="navlink" href=${'#' + id} aria-current=${active === id ? 'page' : undefined}>
    <${Icon} name=${icon} size=${22} /><span>${t(`nav.${id}`)}</span>
  </a>`;
  return html`<nav class="bottomnav" aria-label="Menu"><div class="inner">
    ${tab('home', 'home')}
    ${tab('journal', 'journal')}
    <a class="navlink sos" href="#sos" aria-label=${t('home.sos')}>${t('nav.sos')}</a>
    ${tab('protect', 'shield')}
    ${tab('help', 'help')}
  </div></nav>`;
}

function useOnline() {
  const [online, setOnline] = useState(globalThis.navigator?.onLine !== false);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    globalThis.addEventListener('online', on);
    globalThis.addEventListener('offline', off);
    return () => {
      globalThis.removeEventListener('online', on);
      globalThis.removeEventListener('offline', off);
    };
  }, []);
  return online;
}

function screenFor(route, state) {
  switch (route) {
    case 'test': return html`<${TestScreen} state=${state} />`;
    case 'setup': return html`<${SetupScreen} state=${state} />`;
    case 'plan': return html`<${SetupScreen} state=${state} edit=${true} />`;
    case 'first-step': return html`<${FirstStep} />`;
    case 'sos': return html`<${SosScreen} state=${state} />`;
    case 'relapse': return html`<${HomeScreen} state=${state} openRelapse=${true} />`;
    case 'journal': return html`<${JournalScreen} state=${state} />`;
    case 'protect': return html`<${ProtectScreen} state=${state} />`;
    case 'truth': return html`<${TruthScreen} state=${state} />`;
    case 'help': return html`<${HelpScreen} state=${state} />`;
    case 'coach': return html`<${CoachScreen} state=${state} />`;
    case 'premium': return html`<${PremiumScreen} state=${state} />`;
    case 'settings': return html`<${SettingsScreen} state=${state} />`;
    default: return html`<${HomeScreen} state=${state} />`;
  }
}

export function App() {
  const state = useAppState();
  const route = useRoute();
  const online = useOnline();

  let effective = route;
  if (!state.onboarded && !OPEN_ROUTES.has(route)) effective = 'welcome';
  // Тест и план требуют выбранных языка и страны; калькулятор, SOS и помощь открываются сразу (ссылки из рекламы).
  if (!state.onboarded && ONBOARDING.has(route) && !state.country) effective = 'welcome';
  const showNav = state.onboarded && !NO_NAV.has(effective);

  return html`<div class=${`app${showNav ? ' with-nav' : ''}`}>
    ${store.isPersistent() ? null : html`<p class="banner" role="alert" style="margin:8px 16px 0">${t('common.storageOff')}</p>`}
    ${online ? null : html`<p class="banner" role="status" style="margin:8px 16px 0">${t('common.offline')}</p>`}
    ${effective === 'welcome' ? html`<${Welcome} state=${state} />` : screenFor(effective, state)}
    ${showNav ? html`<${BottomNav} route=${effective} />` : null}
    <${ToastHost} />
  </div>`;
}
