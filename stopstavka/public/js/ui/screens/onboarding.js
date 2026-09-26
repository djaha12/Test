import { html, useState } from '../../vendor/preact-htm.js';
import { detectLang, LANG_NAMES, setLang, t } from '../../core/i18n.js';
import { navigate, store, todayISO } from '../../core/state.js';
import { track } from '../../core/api.js';
import { Chip, Field, Icon, MoneyInput, Segmented, TopBar, Group } from '../components.js';
import { PGSI_ITEMS, pgsiCategory, scorePGSI } from '../../logic/pgsi.js';
import { addDays, isValidISODate } from '../../logic/dates.js';
import { formatMoney } from '../../logic/format.js';
import { yearlySpend } from '../../logic/progress.js';

export const REASONS = ['debt', 'family', 'money', 'health', 'respect', 'future', 'trust'];

export function reasonLabel(reason) {
  return reason.startsWith('reason:') ? t(`reason.${reason.slice(7)}`) : reason;
}

export function Welcome({ state }) {
  const [lang, setLangState] = useState(state.lang || detectLang(globalThis.navigator?.languages || []));
  const [country, setCountry] = useState(state.country || (lang === 'kk' ? 'kz' : 'kg'));

  function chooseLang(next) {
    setLang(next);
    setLangState(next);
    if (next === 'kk') setCountry('kz');
    if (next === 'ky') setCountry('kg');
  }

  function start() {
    store.set((s) => ({ ...s, lang, country }));
    track('onboarding_start', state.utm?.source);
    navigate('test');
  }

  return html`<main class="screen" style="padding-top:calc(env(safe-area-inset-top,0px) + 24px)">
    <div class="row between">
      <span class="badge"><${Icon} name="shield" size=${16} />${t('app.name')}</span>
    </div>
    <h1 class="title-xl">${t('welcome.title')}</h1>
    <p class="lead">${t('welcome.lead')}</p>
    <ul class="plain check-list">
      ${['welcome.point1', 'welcome.point2', 'welcome.point3'].map((k) => html`<li><${Icon} name="check" size=${18} /><span>${t(k)}</span></li>`)}
    </ul>
    <div class="card">
      <${Group} label=${t('welcome.lang')}>
        <${Segmented} label=${t('welcome.lang')} value=${lang} onChange=${chooseLang}
          options=${Object.entries(LANG_NAMES).map(([value, label]) => ({ value, label }))} />
      <//>
      <${Group} label=${t('welcome.country')}>
        <${Segmented} label=${t('welcome.country')} value=${country} onChange=${setCountry}
          options=${[{ value: 'kg', label: t('country.kg') }, { value: 'kz', label: t('country.kz') }]} />
      <//>
    </div>
    <p class="muted small row"><${Icon} name="lock" size=${18} />${t('welcome.privacy')}</p>
    <button type="button" class="btn primary block" onClick=${start}>${t('welcome.start')}</button>
  </main>`;
}

export function TestScreen({ state }) {
  const [step, setStep] = useState('intro');
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);

  function answer(value) {
    const next = [...answers.slice(0, step), value];
    setAnswers(next);
    if (step + 1 < PGSI_ITEMS) {
      setStep(step + 1);
      return;
    }
    const score = scorePGSI(next);
    store.set((s) => ({ ...s, pgsi: [...s.pgsi, { date: todayISO(), answers: next, score }] }));
    track('test_done', state.utm?.source);
    setResult(score);
    setStep('result');
  }

  if (step === 'intro') {
    return html`<${TopBar} title=${t('app.name')} back=${state.onboarded ? 'settings' : ''} />
      <main class="screen">
        <h1 class="title-xl">${t('test.intro.title')}</h1>
        <p class="lead">${t('test.intro.text')}</p>
        <button type="button" class="btn primary block" onClick=${() => setStep(0)}>${t('test.intro.start')}</button>
      </main>`;
  }

  if (step === 'result') {
    const category = pgsiCategory(result);
    return html`<${TopBar} title=${t('app.name')} />
      <main class="screen">
        <span class="badge">${t('test.result.score', { score: result })}</span>
        <h1 class="title-xl">${t(`test.result.${category}.title`)}</h1>
        <p class="lead">${t(`test.result.${category}.text`)}</p>
        <p class="muted small">${t('test.result.note')}</p>
        ${state.onboarded
          ? html`<button type="button" class="btn primary block" onClick=${() => navigate('home')}>${t('test.result.back')}</button>`
          : html`<button type="button" class="btn primary block" onClick=${() => navigate('setup')}>${t('test.result.next')}</button>`}
        ${category === 'high' ? html`<a class="btn secondary block" href="#help">${t('help.pro.title')}</a>` : null}
      </main>`;
  }

  return html`<${TopBar} title=${t('test.progress', { n: step + 1 })} />
    <main class="screen">
      <div class="progress-dots" aria-hidden="true">
        ${Array.from({ length: PGSI_ITEMS }, (_, i) => html`<i class=${i <= step ? 'on' : ''}></i>`)}
      </div>
      <p class="muted">${t('test.lead')}</p>
      <h2 style="margin:0;font-size:22px;line-height:1.3">${t(`pgsi.q${step + 1}`)}</h2>
      <div class="options" role="group">
        ${[0, 1, 2, 3].map((v) => html`<button type="button" class="option" aria-pressed=${String(answers[step] === v)}
          onClick=${() => answer(v)}>${t(`pgsi.a${v}`)}</button>`)}
      </div>
      ${step > 0 ? html`<button type="button" class="linklike" onClick=${() => setStep(step - 1)}>${t('common.back')}</button>` : null}
    </main>`;
}

export function SetupScreen({ state, edit = false }) {
  const today = todayISO();
  const p = state.profile;
  const initialWhen = !p.lastBetDate ? 'today' : p.lastBetDate === today ? 'today'
    : p.lastBetDate === addDays(today, -1) ? 'yesterday' : 'earlier';
  const [when, setWhen] = useState(initialWhen);
  const [date, setDate] = useState(p.lastBetDate && initialWhen === 'earlier' ? p.lastBetDate : addDays(today, -2));
  const [spend, setSpend] = useState(p.weeklySpend > 0 ? p.weeklySpend : NaN);
  const [reasons, setReasons] = useState(p.reasons);
  const [custom, setCustom] = useState('');
  const [goalTitle, setGoalTitle] = useState(p.goal.title);
  const [goalAmount, setGoalAmount] = useState(p.goal.amount > 0 ? p.goal.amount : NaN);
  const [buddyName, setBuddyName] = useState(p.buddy.name);
  const [buddyPhone, setBuddyPhone] = useState(p.buddy.phone);
  const [errors, setErrors] = useState({});

  const toggleReason = (r) => setReasons(reasons.includes(r) ? reasons.filter((x) => x !== r) : [...reasons, r]);

  function addCustom() {
    const value = custom.trim().slice(0, 120);
    if (value && !reasons.includes(value)) setReasons([...reasons, value]);
    setCustom('');
  }

  function save(e) {
    e.preventDefault();
    const lastBetDate = when === 'today' ? today : when === 'yesterday' ? addDays(today, -1) : date;
    const nextErrors = {};
    if (!(spend > 0)) nextErrors.spend = t('setup.error.spend');
    if (!isValidISODate(lastBetDate) || lastBetDate > today) nextErrors.date = t('setup.error.date');
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    store.set((s) => {
      const startDate = !s.profile.startDate || lastBetDate < s.profile.startDate ? lastBetDate : s.profile.startDate;
      return {
        ...s,
        onboarded: true,
        profile: {
          ...s.profile,
          startDate: edit ? startDate : lastBetDate,
          lastBetDate,
          weeklySpend: Math.round(spend),
          reasons: custom.trim() && !reasons.includes(custom.trim()) ? [...reasons, custom.trim()] : reasons,
          goal: { title: goalTitle.trim().slice(0, 120), amount: goalAmount > 0 ? Math.round(goalAmount) : 0 },
          buddy: { name: buddyName.trim().slice(0, 60), phone: buddyPhone.replace(/[^\d+]/g, '').slice(0, 20) },
        },
      };
    });
    if (edit) {
      navigate('settings');
    } else {
      track('setup_done', state.utm?.source);
      navigate('first-step');
    }
  }

  return html`<${TopBar} title=${edit ? t('settings.plan') : t('setup.title')} back=${edit ? 'settings' : ''} />
    <form class="screen" style="display:flex;flex-direction:column;gap:14px;padding:4px 16px 24px" onSubmit=${save} novalidate>
      ${edit ? null : html`<p class="lead">${t('setup.lead')}</p>`}
      <section class="card">
        <h2>${t('setup.lastBet')}</h2>
        <${Segmented} label=${t('setup.lastBet')} value=${when} onChange=${setWhen}
          options=${[{ value: 'today', label: t('common.today') }, { value: 'yesterday', label: t('common.yesterday') }, { value: 'earlier', label: t('setup.lastBet.earlier') }]} />
        ${when === 'earlier' ? html`<${Field} label=${t('setup.lastBet.date')} error=${errors.date}>
          <input class="input" type="date" max=${today} value=${date} onInput=${(e) => setDate(e.currentTarget.value)} />
        <//>` : null}
      </section>
      <section class="card">
        <h2>${t('setup.spend')}</h2>
        <${Field} label=${t('setup.spend.hint')} error=${errors.spend}>
          <${MoneyInput} id="weekly-spend" value=${spend} onValue=${setSpend} country=${state.country} />
        <//>
        ${spend > 0 ? html`<p class="small">${t('setup.spend.year', { money: formatMoney(yearlySpend(spend), state.country) })}</p>` : null}
      </section>
      <section class="card">
        <h2>${t('setup.reasons')}</h2>
        <div class="chips">
          ${REASONS.map((r) => html`<${Chip} pressed=${reasons.includes(`reason:${r}`)} onClick=${() => toggleReason(`reason:${r}`)}>${t(`reason.${r}`)}<//>`)}
          ${reasons.filter((r) => !r.startsWith('reason:')).map((r) => html`<${Chip} pressed=${true} onClick=${() => toggleReason(r)}>${r}<//>`)}
        </div>
        <div class="row">
          <input class="input" aria-label=${t('setup.reasons.custom')} placeholder=${t('setup.reasons.custom')} value=${custom}
            onInput=${(e) => setCustom(e.currentTarget.value)} onKeyDown=${(e) => { if (e.key === 'Enter') { e.preventDefault(); addCustom(); } }} />
          <button type="button" class="btn secondary" onClick=${addCustom}>${t('setup.reasons.add')}</button>
        </div>
      </section>
      <section class="card">
        <h2>${t('setup.goal')}</h2>
        <${Field} label=${t('setup.goal.title')}>
          <input class="input" placeholder=${t('setup.goal.placeholder')} value=${goalTitle} onInput=${(e) => setGoalTitle(e.currentTarget.value)} />
        <//>
        <${Field} label=${t('setup.goal.amount')}>
          <${MoneyInput} id="goal-amount" value=${goalAmount} onValue=${setGoalAmount} country=${state.country} />
        <//>
      </section>
      <section class="card">
        <h2>${t('setup.buddy')} <span class="muted small">(${t('common.optional')})</span></h2>
        <${Field} label=${t('setup.buddy.name')}>
          <input class="input" autocomplete="off" value=${buddyName} onInput=${(e) => setBuddyName(e.currentTarget.value)} />
        <//>
        <${Field} label=${t('setup.buddy.phone')} hint=${t('setup.buddy.hint')}>
          <input class="input" type="tel" inputmode="tel" autocomplete="off" placeholder=${state.country === 'kz' ? '+7' : '+996'}
            value=${buddyPhone} onInput=${(e) => setBuddyPhone(e.currentTarget.value)} />
        <//>
      </section>
      <button type="submit" class="btn primary block">${edit ? t('common.save') : t('setup.finish')}</button>
    </form>`;
}

export function FirstStep() {
  return html`<main class="screen" style="padding-top:calc(env(safe-area-inset-top,0px) + 32px)">
    <span class="badge"><${Icon} name="shield" size=${16} />${t('protect.title')}</span>
    <h1 class="title-xl">${t('first.title')}</h1>
    <p class="lead">${t('first.text')}</p>
    <a class="btn primary block" href="#protect">${t('first.go')}</a>
    <a class="btn ghost block" href="#home">${t('first.later')}</a>
  </main>`;
}
