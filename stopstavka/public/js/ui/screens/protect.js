import { html, useRef, useState } from '../../vendor/preact-htm.js';
import { t, tList } from '../../core/i18n.js';
import { showToast, store } from '../../core/state.js';
import { track } from '../../core/api.js';
import { copyText, Icon, Meter, SettingsLink, TopBar } from '../components.js';
import { DOMAINS, stepsFor } from '../../content/blocking.js';

function Domains() {
  const ref = useRef(null);
  async function copy() {
    const ok = await copyText(DOMAINS.join('\n'), ref.current);
    showToast(ok ? t('common.copied') : t('protect.domains.copy'));
  }
  return html`<div class="stack">
    <p class="small muted">${t('protect.domains.text')}</p>
    <div class="domains" ref=${ref}>${DOMAINS.join(' · ')}</div>
    <button type="button" class="btn secondary" onClick=${copy}><${Icon} name="copy" size=${20} />${t('protect.domains.copy')}</button>
  </div>`;
}

function Step({ step, done, onToggle }) {
  const [open, setOpen] = useState(false);
  const bodyId = `step-body-${step.id}`;
  return html`<section class="card step">
    <div class="step-head">
      <button type="button" class="step-check" aria-pressed=${String(done)} onClick=${onToggle}
        aria-label=${done ? t('protect.unmark') : t('protect.mark')}><${Icon} name="check" size=${18} /></button>
      <button type="button" class="step-title" aria-expanded=${String(open)} aria-controls=${bodyId} onClick=${() => setOpen(!open)}>
        ${t(`step.${step.id}.title`)}
      </button>
    </div>
    <div id=${bodyId} hidden=${!open} class="stack">
      <ol class="steps">${tList(`step.${step.id}.body`).map((line) => html`<li>${line}</li>`)}</ol>
      ${step.showDomains ? html`<${Domains} />` : null}
      ${done ? null : html`<button type="button" class="btn primary" onClick=${onToggle}><${Icon} name="check" size=${20} />${t('protect.mark')}</button>`}
    </div>
  </section>`;
}

export function ProtectScreen({ state }) {
  const steps = stepsFor(state.country);
  const done = steps.filter((s) => state.blocking[s.id]).length;

  function toggle(id) {
    const next = !state.blocking[id];
    store.set((s) => ({ ...s, blocking: { ...s.blocking, [id]: next } }));
    if (next) track('protect_step', state.utm?.source);
  }

  return html`<${TopBar} title=${t('protect.title')} right=${html`<${SettingsLink} />`} />
    <main class="screen">
      <p class="lead">${t('protect.lead')}</p>
      <section class="card">
        <div class="row between"><strong>${t('protect.progress', { done, total: steps.length })}</strong></div>
        <${Meter} value=${done / steps.length} label=${t('protect.title')} />
      </section>
      ${steps.map((s) => html`<${Step} key=${s.id} step=${s} done=${Boolean(state.blocking[s.id])} onToggle=${() => toggle(s.id)} />`)}
      <a class="card link" href="#truth">
        <div class="row between"><h2>${t('protect.truth')}</h2><${Icon} name="calc" /></div>
      </a>
    </main>`;
}
