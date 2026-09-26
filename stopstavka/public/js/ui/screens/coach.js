import { html, useEffect, useRef, useState } from '../../vendor/preact-htm.js';
import { getLang, t } from '../../core/i18n.js';
import { isPremium, store, todayISO } from '../../core/state.js';
import { getConfig, streamCoach } from '../../core/api.js';
import { Icon, TopBar } from '../components.js';
import { reasonLabel } from './onboarding.js';
import { daysClean, moneySaved } from '../../logic/progress.js';
import { formatMoney } from '../../logic/format.js';
import { CONTACTS } from '../../content/contacts.js';

const MAX_HISTORY = 20;

export function CoachScreen({ state }) {
  const [config, setConfig] = useState(undefined);
  const [draft, setDraft] = useState('');
  const [pending, setPending] = useState(null);
  const [error, setError] = useState(null);
  const [remaining, setRemaining] = useState(null);
  const [crisis, setCrisis] = useState(false);
  const abortRef = useRef(null);
  const endRef = useRef(null);
  const premium = isPremium(state);

  useEffect(() => { getConfig().then(setConfig); return () => abortRef.current?.abort(); }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ block: 'end' }); }, [state.coach.length, pending]);

  const aiEnabled = Boolean(config?.ai?.enabled);
  const busy = pending !== null;

  async function send(e) {
    e.preventDefault();
    const text = draft.trim().slice(0, 1000);
    if (!text || busy || !aiEnabled) return;
    setDraft('');
    setError(null);
    const history = [...state.coach, { role: 'user', content: text }].slice(-MAX_HISTORY);
    store.set((s) => ({ ...s, coach: [...s.coach, { role: 'user', content: text }] }));
    setPending('');
    const controller = new AbortController();
    abortRef.current = controller;
    const today = todayISO();
    let answer = '';
    try {
      await streamCoach({
        messages: history,
        lang: getLang(),
        country: state.country,
        deviceId: state.deviceId,
        context: {
          daysClean: daysClean(state.profile, today),
          saved: formatMoney(moneySaved(state.profile, state.relapses, today), state.country),
          reasons: state.profile.reasons.map(reasonLabel).slice(0, 6),
        },
      }, {
        token: premium ? state.premium.token : null,
        signal: controller.signal,
        onMeta: (meta) => {
          if (typeof meta.remaining === 'number') setRemaining(meta.remaining);
          if (meta.crisis) setCrisis(true);
        },
        onDelta: (chunk) => { answer += chunk; setPending(answer); },
        onReplace: (full) => { answer = full; setPending(answer); },
      });
      if (answer.trim()) store.set((s) => ({ ...s, coach: [...s.coach, { role: 'assistant', content: answer.trim() }] }));
    } catch (err) {
      if (err?.name !== 'AbortError') setError(err?.code || 'network');
    } finally {
      setPending(null);
    }
  }

  function clear() {
    abortRef.current?.abort();
    store.set((s) => ({ ...s, coach: [] }));
    setError(null);
  }

  const notice = config === null ? t('coach.demo') : config && !aiEnabled ? t('coach.unavailable') : null;

  return html`<${TopBar} title=${t('coach.title')} back="help"
      right=${state.coach.length ? html`<button type="button" class="icon-btn" aria-label=${t('coach.clear')} onClick=${clear}><${Icon} name="trash" /></button>` : null} />
    <main class="screen">
      <p class="small muted row"><${Icon} name="spark" size=${18} />${t('coach.disclaimer')}</p>
      ${crisis ? html`<section class="card" role="alert" style="border-color:var(--sos)">
        <h2>${t('help.now.title')}</h2>
        <p>${t('help.now.text')}</p>
        <div class="row" style="flex-wrap:wrap">
          ${(CONTACTS[state.country] || CONTACTS.kg).map((c) => html`<a class="btn danger" href=${`tel:${c.phone}`}><${Icon} name="phone" size=${18} />${c.phone}</a>`)}
        </div>
      </section>` : null}
      <div class="chat" aria-live="polite">
        <div class="bubble assistant">${t('coach.hello')}</div>
        ${state.coach.map((m) => html`<div class=${`bubble ${m.role}`}>${m.content}</div>`)}
        ${pending !== null ? html`<div class="bubble assistant">${pending || '…'}</div>` : null}
        <div ref=${endRef}></div>
      </div>
      ${notice ? html`<p class="banner">${notice}</p>` : null}
      ${error === 'limit' ? html`<div class="banner">${t('coach.limit')} <a href="#premium">${t('premium.title')}</a></div>` : null}
      ${error && error !== 'limit' ? html`<p class="error-text" role="alert">${error === 'unavailable' ? t('coach.unavailable') : t('coach.error')}</p>` : null}
      ${!premium && remaining !== null && remaining >= 0 ? html`<p class="tiny muted">${t('coach.left', { n: remaining })}</p>` : null}
      <form class="composer" onSubmit=${send}>
        <textarea class="input" rows="1" maxlength="1000" aria-label=${t('coach.placeholder')} placeholder=${t('coach.placeholder')}
          value=${draft} disabled=${!aiEnabled} onInput=${(e) => setDraft(e.currentTarget.value)}
          onKeyDown=${(e) => { if (e.key === 'Enter' && !e.shiftKey) send(e); }}></textarea>
        <button type="submit" class="btn primary" disabled=${!aiEnabled || busy || !draft.trim()} aria-label=${t('coach.send')}>
          <${Icon} name="chevron" />
        </button>
      </form>
      <p class="tiny muted">${t('coach.privacy')}</p>
    </main>`;
}
