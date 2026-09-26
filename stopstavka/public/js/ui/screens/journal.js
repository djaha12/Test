import { html, useState } from '../../vendor/preact-htm.js';
import { t } from '../../core/i18n.js';
import { isPremium, showToast, store, todayISO } from '../../core/state.js';
import { track } from '../../core/api.js';
import { Chip, Field, MoneyInput, Segmented, SettingsLink, Stat, TopBar, Group } from '../components.js';
import { TriggerBars, UrgeChart } from '../charts.js';
import { peakPeriod, resistedCount, TRIGGERS, triggerCounts, urgeSeries } from '../../logic/insights.js';
import { daysClean } from '../../logic/progress.js';

function CheckinForm({ state }) {
  const today = todayISO();
  const existing = state.checkins[today];
  const [mood, setMood] = useState(existing?.mood ?? 3);
  const [urge, setUrge] = useState(existing?.urge ?? 0);
  const [triggers, setTriggers] = useState(existing?.triggers ?? []);
  const [bet, setBet] = useState(existing?.bet ?? false);
  const [lost, setLost] = useState(existing?.lost > 0 ? existing.lost : NaN);
  const [note, setNote] = useState(existing?.note ?? '');

  function save(e) {
    e.preventDefault();
    const entry = { mood, urge, triggers, bet, lost: bet && lost > 0 ? Math.round(lost) : 0, note: note.trim().slice(0, 500) };
    store.set((s) => {
      const next = { ...s, checkins: { ...s.checkins, [today]: entry } };
      if (bet) {
        // Ставка сегодня = срыв: счётчик начинается заново, потери учитываются один раз.
        next.relapses = [...s.relapses.filter((r) => r.date !== today), { date: today, lost: entry.lost, triggers }];
        next.profile = { ...s.profile, lastBetDate: today };
      }
      return next;
    });
    track('checkin', state.utm?.source);
    showToast(t('checkin.saved'));
  }

  return html`<form class="card" onSubmit=${save}>
    <h2>${t('checkin.title.today')}</h2>
    <div class="field">
      <span>${t('checkin.mood')}</span>
      <div class="chips" role="group" aria-label=${t('checkin.mood')}>
        ${[1, 2, 3, 4, 5].map((m) => html`<${Chip} pressed=${mood === m} onClick=${() => setMood(m)}>${t(`mood.${m}`)}<//>`)}
      </div>
    </div>
    <div class="field">
      <label for="checkin-urge"><span style="font-size:14px;font-weight:600;color:var(--ink-2)">${t('checkin.urge')}</span></label>
      <div class="row between"><span class="range-value">${urge}</span><span class="muted small">/ 10</span></div>
      <input id="checkin-urge" type="range" min="0" max="10" step="1" value=${urge} onInput=${(e) => setUrge(Number(e.currentTarget.value))} />
      <div class="range-labels"><span>${t('checkin.urge.low')}</span><span>${t('checkin.urge.high')}</span></div>
    </div>
    <div class="field">
      <span>${t('checkin.triggers')}</span>
      <div class="chips">
        ${TRIGGERS.map((id) => html`<${Chip} pressed=${triggers.includes(id)}
          onClick=${() => setTriggers(triggers.includes(id) ? triggers.filter((x) => x !== id) : [...triggers, id])}>${t(`trigger.${id}`)}<//>`)}
      </div>
    </div>
    <${Group} label=${t('checkin.bet')}>
      <${Segmented} label=${t('checkin.bet')} value=${bet} onChange=${setBet}
        options=${[{ value: false, label: t('common.no') }, { value: true, label: t('common.yes') }]} />
    <//>
    ${bet ? html`<${Field} label=${t('checkin.lost')}>
      <${MoneyInput} id="checkin-lost" value=${lost} onValue=${setLost} country=${state.country} />
    <//>` : null}
    <${Field} label=${t('checkin.note')}>
      <textarea class="input" maxlength="500" value=${note} onInput=${(e) => setNote(e.currentTarget.value)}></textarea>
    <//>
    <button type="submit" class="btn primary block">${t('checkin.save')}</button>
  </form>`;
}

function Insights({ state }) {
  const premium = isPremium(state);
  const [range, setRange] = useState(14);
  const today = todayISO();
  const series = urgeSeries(state, premium ? range : 14, today);
  const hasData = series.some((d) => d.value !== null || d.bet);
  const triggers = triggerCounts(state).slice(0, 6);
  const peak = peakPeriod(state.urges);

  return html`<h2 class="section-title">${t('insights.title')}</h2>
    <div class="stats">
      <${Stat} label=${t('insights.stat.days')} value=${daysClean(state.profile, today)} />
      <${Stat} label=${t('home.resisted')} value=${t('home.times', { n: resistedCount(state.urges) })} />
    </div>
    ${!hasData && !triggers.length
      ? html`<section class="card"><p>${t('insights.empty')}</p></section>`
      : html`
        <section class="card">
          <div class="row between"><h3>${t('insights.urge.title')}</h3></div>
          ${premium
            ? html`<${Segmented} label=${t('insights.urge.title')} value=${range} onChange=${setRange}
                options=${[{ value: 14, label: t('insights.range.14') }, { value: 90, label: t('insights.range.90') }]} />`
            : html`<a class="small" href="#premium">${t('insights.range.plus')}</a>`}
          <${UrgeChart} series=${series} />
          ${peak ? html`<p class="small">${t('insights.peak', { period: t(`period.${peak.id}`) })}</p>` : null}
        </section>
        ${triggers.length ? html`<section class="card">
          <h3>${t('insights.triggers.title')}</h3>
          <${TriggerBars} items=${triggers} />
        </section>` : null}`}`;
}

export function JournalScreen({ state }) {
  return html`<${TopBar} title=${t('journal.title')} right=${html`<${SettingsLink} />`} />
    <main class="screen">
      <${CheckinForm} state=${state} />
      <${Insights} state=${state} />
    </main>`;
}
