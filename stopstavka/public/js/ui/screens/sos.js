import { html, useEffect, useState } from '../../vendor/preact-htm.js';
import { t, tList } from '../../core/i18n.js';
import { navigate, store, todayISO } from '../../core/state.js';
import { track } from '../../core/api.js';
import { randomId } from '../../core/store.js';
import { Chip, Icon } from '../components.js';
import { reasonLabel } from './onboarding.js';
import { moneySaved } from '../../logic/progress.js';
import { houseShare } from '../../logic/betting.js';
import { TRIGGERS } from '../../logic/insights.js';
import { formatMoney, formatPercent } from '../../logic/format.js';

const DURATION = 600;
const BREATH = ['in', 'hold', 'out', 'hold'];

function clock(seconds) {
  const m = Math.floor(seconds / 60);
  const s = String(seconds % 60).padStart(2, '0');
  return `${m}:${s}`;
}

export function whatsappLink(phone, text) {
  const digits = String(phone || '').replace(/\D/g, '');
  return digits ? `https://wa.me/${digits}?text=${encodeURIComponent(text)}` : null;
}

function BuddyButtons({ buddy }) {
  if (!buddy.phone) return html`<p class="muted small">${t('sos.buddy.none')} <a href="#plan">${t('common.edit')}</a></p>`;
  const message = t('sos.buddy.message');
  return html`<div class="stack">
    <p class="muted small">${buddy.name || buddy.phone} · <span class="tiny">${buddy.phone}</span></p>
    <div class="row">
      <a class="btn primary" style="flex:1" href=${whatsappLink(buddy.phone, message)} target="_blank" rel="noopener">
        <${Icon} name="message" size=${20} />${t('sos.buddy.write', { name: buddy.name || 'WhatsApp' })}
      </a>
      <a class="btn secondary" href=${`tel:${buddy.phone}`}><${Icon} name="phone" size=${20} />${t('sos.buddy.call')}</a>
    </div>
  </div>`;
}

export function SosScreen({ state }) {
  const [phase, setPhase] = useState('intensity');
  const [intensity, setIntensity] = useState(6);
  const [startedAt, setStartedAt] = useState(null);
  const [left, setLeft] = useState(DURATION);
  const [breath, setBreath] = useState(0);
  const [trigger, setTrigger] = useState(null);
  const [outcome, setOutcome] = useState(null);

  useEffect(() => {
    if (phase !== 'timer') return undefined;
    let lock = null;
    globalThis.navigator?.wakeLock?.request('screen').then((l) => { lock = l; }).catch(() => {});
    const tick = setInterval(() => {
      setLeft((v) => {
        if (v <= 1) {
          setPhase('outcome');
          return 0;
        }
        return v - 1;
      });
    }, 1000);
    const breathe = setInterval(() => setBreath((b) => (b + 1) % 4), 4000);
    return () => {
      clearInterval(tick);
      clearInterval(breathe);
      lock?.release?.().catch(() => {});
    };
  }, [phase]);

  function start() {
    setStartedAt((prev) => prev || new Date().toISOString());
    setLeft(DURATION);
    setBreath(0);
    setPhase('timer');
    track('sos_start', state.utm?.source);
  }

  function finish(result) {
    const event = { id: randomId().slice(0, 12), at: startedAt || new Date().toISOString(), before: intensity, outcome: result, trigger };
    store.set((s) => ({ ...s, urges: [...s.urges, event] }));
    track(result === 'bet' ? 'sos_bet' : 'sos_passed', state.utm?.source);
    if (result === 'bet') {
      navigate('relapse');
      return;
    }
    setOutcome(result);
    setPhase('thanks');
  }

  const saved = moneySaved(state.profile, state.relapses, todayISO());
  const share = houseShare(state.truth.margin, state.truth.legs);
  const scale = BREATH[breath] === 'in' || (BREATH[breath] === 'hold' && breath === 1) ? 1 : 0.7;

  return html`<div class="sos-screen">
    <header class="topbar">
      <h1>${t('sos.title')}</h1>
      <a class="icon-btn" href="#home" aria-label=${t('common.close')}><${Icon} name="close" /></a>
    </header>
    <main class="screen">
      ${phase === 'intensity' ? html`
        <p class="lead">${t('sos.lead')}</p>
        <section class="card">
          <label class="field" for="sos-intensity"><span>${t('sos.intensity')}</span></label>
          <div class="row between"><span class="range-value">${intensity}</span><span class="muted small">/ 10</span></div>
          <input id="sos-intensity" type="range" min="1" max="10" step="1" value=${intensity}
            onInput=${(e) => setIntensity(Number(e.currentTarget.value))} />
          <div class="range-labels"><span>${t('sos.intensity.low')}</span><span>${t('sos.intensity.high')}</span></div>
        </section>
        <button type="button" class="btn sos-big" onClick=${start}>${t('sos.start')}</button>
        <section class="card"><${BuddyButtons} buddy=${state.profile.buddy} /></section>
      ` : null}

      ${phase === 'timer' ? html`
        <div class="breath" style=${`--scale:${scale}`} aria-live="polite">
          <div>
            <strong>${t(`sos.breathe.${BREATH[breath]}`)}</strong>
            <span class="time">${t('sos.left', { time: clock(left) })}</span>
          </div>
        </div>
        <p class="muted small" style="text-align:center;margin:0">${t('sos.breathe.hint')}</p>
        ${state.profile.reasons.length ? html`<section class="card">
          <h3>${t('sos.reasons')}</h3>
          <ul class="plain check-list">${state.profile.reasons.map((r) => html`<li><${Icon} name="check" size=${18} /><span>${reasonLabel(r)}</span></li>`)}</ul>
        </section>` : null}
        ${saved > 0 ? html`<section class="card"><h3>${t('sos.saved', { money: formatMoney(saved, state.country) })}</h3></section>` : null}
        <section class="card"><p>${t('sos.math', { share: formatPercent(share, 1) })}</p></section>
        <section class="card">
          <h3>${t('sos.actions')}</h3>
          <ul class="plain check-list">${tList('sos.act').map((a) => html`<li><${Icon} name="check" size=${18} /><span>${a}</span></li>`)}</ul>
        </section>
        <section class="card"><${BuddyButtons} buddy=${state.profile.buddy} /></section>
        <a class="btn secondary block" href="#coach"><${Icon} name="spark" size=${20} />${t('sos.coach')}</a>
        <button type="button" class="btn primary block" onClick=${() => setPhase('outcome')}>${t('sos.finish')}</button>
      ` : null}

      ${phase === 'outcome' ? html`
        <h2 class="title-xl" style="font-size:24px">${t('sos.outcome.title')}</h2>
        <div class="field">
          <span>${t('sos.trigger')}</span>
          <div class="chips">${TRIGGERS.map((id) => html`<${Chip} pressed=${trigger === id} onClick=${() => setTrigger(trigger === id ? null : id)}>${t(`trigger.${id}`)}<//>`)}</div>
        </div>
        <div class="options">
          ${['passed', 'better', 'still', 'bet'].map((o) => html`<button type="button" class="option" onClick=${() => finish(o)}>${t(`sos.outcome.${o}`)}</button>`)}
        </div>
      ` : null}

      ${phase === 'thanks' ? html`
        <h2 class="title-xl" style="font-size:24px">${t(`sos.outcome.${outcome}`)}</h2>
        <p class="lead">${outcome === 'still' ? t('sos.thanks.still') : t('sos.thanks.passed')}</p>
        ${outcome === 'still' ? html`<button type="button" class="btn sos-big" onClick=${start}>${t('sos.again')}</button>
          <a class="btn secondary block" href="#coach"><${Icon} name="spark" size=${20} />${t('sos.coach')}</a>` : null}
        <a class="btn ${outcome === 'still' ? 'ghost' : 'primary'} block" href="#home">${t('sos.home')}</a>
      ` : null}
    </main>
  </div>`;
}
