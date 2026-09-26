import { html, useState } from '../../vendor/preact-htm.js';
import { t } from '../../core/i18n.js';
import { navigate, showToast, store, todayISO } from '../../core/state.js';
import { track } from '../../core/api.js';
import { Chip, Field, Icon, Meter, MoneyInput, Sheet, SettingsLink, Stat, TopBar } from '../components.js';
import { daysClean, goalProgress, moneySaved, nextMilestone } from '../../logic/progress.js';
import { resistedCount, TRIGGERS } from '../../logic/insights.js';
import { formatMoney } from '../../logic/format.js';
import { stepsFor } from '../../content/blocking.js';

export function HomeScreen({ state, openRelapse = false }) {
  const [relapseOpen, setRelapseOpen] = useState(openRelapse);
  const today = todayISO();
  const days = daysClean(state.profile, today);
  const saved = moneySaved(state.profile, state.relapses, today);
  const resisted = resistedCount(state.urges);
  const goal = state.profile.goal;
  const progress = goalProgress(saved, goal);
  const milestone = nextMilestone(days);
  const steps = stepsFor(state.country);
  const stepsDone = steps.filter((s) => state.blocking[s.id]).length;
  const checkedToday = Boolean(state.checkins[today]);
  const money = (v) => formatMoney(v, state.country);

  return html`<${TopBar} title=${t('app.name')} right=${html`<${SettingsLink} />`} />
    <main class="screen">
      <section class="home-hero" aria-live="polite">
        ${days === 0
          ? html`<span class="hero-figure">0</span><span class="hero-label">${t('home.dayOne')}</span>`
          : html`<span class="hero-figure">${days}</span><span class="hero-label">${t('home.days', { n: days })}</span>`}
        ${milestone ? html`<span class="muted small">${t('home.milestone', { m: milestone })}</span>` : null}
      </section>

      <div class="stats">
        <${Stat} label=${t('home.saved')} value=${money(saved)} hint=${t('home.saved.hint')} />
        <${Stat} label=${t('home.resisted')} value=${t('home.times', { n: resisted })} />
      </div>

      <button type="button" class="btn sos-big" onClick=${() => navigate('sos')}>
        ${t('home.sos')}<small>${t('home.sos.hint')}</small>
      </button>

      <section class="card">
        <div class="row between"><h2>${t('home.goal')}${goal.title ? `: ${goal.title}` : ''}</h2></div>
        ${progress === null
          ? html`<p>${t('home.goal.empty')}</p><a class="linklike" href="#plan">${t('common.edit')}</a>`
          : html`<${Meter} value=${progress} label=${t('home.goal')} />
            <p class="small">${progress >= 1 ? t('home.goal.done') : t('home.goal.of', { saved: money(saved), amount: money(goal.amount) })}</p>`}
      </section>

      <a class="card link" href="#journal">
        <div class="row between"><h2>${t('home.checkin.title')}</h2><${Icon} name="chevron" /></div>
        <p>${checkedToday ? t('home.checkin.done') : t('home.checkin.text')}</p>
      </a>

      <a class="card link" href="#protect">
        <div class="row between"><h2>${t('home.protect.title')}</h2><${Icon} name="chevron" /></div>
        <${Meter} value=${stepsDone / steps.length} label=${t('home.protect.title')} />
        <p class="small">${t('home.protect.progress', { done: stepsDone, total: steps.length })}</p>
      </a>

      <a class="card link" href="#truth">
        <div class="row between"><h2>${t('home.truth.title')}</h2><${Icon} name="calc" /></div>
        <p>${t('home.truth.text')}</p>
      </a>

      <button type="button" class="linklike" style="align-self:center" onClick=${() => setRelapseOpen(true)}>${t('home.relapse')}</button>
    </main>
    <${RelapseSheet} open=${relapseOpen} state=${state} onClose=${() => { setRelapseOpen(false); if (openRelapse) navigate('home'); }} />`;
}

export function RelapseSheet({ open, state, onClose }) {
  const [lost, setLost] = useState(NaN);
  const [triggers, setTriggers] = useState([]);

  function save() {
    const today = todayISO();
    store.set((s) => ({
      ...s,
      relapses: [...s.relapses.filter((r) => r.date !== today), { date: today, lost: lost > 0 ? Math.round(lost) : 0, triggers }],
      profile: { ...s.profile, lastBetDate: today },
    }));
    track('relapse', state.utm?.source);
    showToast(t('relapse.after'));
    setLost(NaN);
    setTriggers([]);
    onClose();
  }

  return html`<${Sheet} open=${open} onClose=${onClose} title=${t('relapse.title')}>
    <p class="lead">${t('relapse.text')}</p>
    <${Field} label=${`${t('relapse.lost')} (${t('common.optional')})`}>
      <${MoneyInput} id="relapse-lost" value=${lost} onValue=${setLost} country=${state.country} />
    <//>
    <div class="field">
      <span>${t('relapse.triggers')}</span>
      <div class="chips">
        ${TRIGGERS.map((id) => html`<${Chip} pressed=${triggers.includes(id)}
          onClick=${() => setTriggers(triggers.includes(id) ? triggers.filter((x) => x !== id) : [...triggers, id])}>${t(`trigger.${id}`)}<//>`)}
      </div>
    </div>
    <p class="small">${t('relapse.tip')}</p>
    <button type="button" class="btn primary block" onClick=${save}>${t('relapse.save')}</button>
  <//>`;
}
