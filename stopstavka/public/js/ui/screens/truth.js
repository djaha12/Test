import { html, useEffect, useMemo, useState } from '../../vendor/preact-htm.js';
import { t } from '../../core/i18n.js';
import { showToast, store } from '../../core/state.js';
import { track } from '../../core/api.js';
import { copyText, Field, Icon, MoneyInput, TopBar } from '../components.js';
import { BankrollChart } from '../charts.js';
import { estimateProfitChance, expectedLoss, houseShare, PRESETS, simulatePath, totalStaked } from '../../logic/betting.js';
import { formatMoney, formatPercent, parseAmount } from '../../logic/format.js';

function valid(p) {
  return p.odds > 1 && p.odds <= 100 && p.stake > 0 && Number.isInteger(p.perWeek) && p.perWeek >= 1 && p.perWeek <= 500
    && p.margin >= 0 && p.margin < 0.5;
}

export function TruthScreen({ state }) {
  const saved = state.truth;
  const [preset, setPreset] = useState(saved.preset);
  const [odds, setOdds] = useState(String(saved.odds).replace('.', ','));
  const [stake, setStake] = useState(saved.stake);
  const [perWeek, setPerWeek] = useState(String(saved.perWeek));
  const [marginPct, setMarginPct] = useState(String(Math.round(saved.margin * 1000) / 10).replace('.', ','));
  const [seed, setSeed] = useState(1);

  const params = {
    odds: parseAmount(odds),
    stake,
    perWeek: Number(perWeek),
    margin: parseAmount(marginPct) / 100,
    legs: PRESETS[preset].legs,
  };
  const ok = valid(params);

  useEffect(() => { track('truth_calc', state.utm?.source); }, []);
  useEffect(() => {
    if (!ok) return;
    store.set((s) => ({ ...s, truth: { preset, ...params } }));
  }, [preset, odds, stake, perWeek, marginPct]);

  function choosePreset(id) {
    setPreset(id);
    setMarginPct(String(PRESETS[id].margin * 100).replace('.', ','));
  }

  const results = useMemo(() => {
    if (!ok) return null;
    const year = estimateProfitChance({ ...params, weeks: 52 });
    const three = estimateProfitChance({ ...params, weeks: 156 });
    return {
      share: houseShare(params.margin, params.legs),
      staked: totalStaked(params),
      loss: expectedLoss(params),
      year,
      three,
    };
  }, [ok, params.odds, params.stake, params.perWeek, params.margin, params.legs]);

  const path = useMemo(() => (ok ? simulatePath({ ...params, seed }) : null),
    [ok, params.odds, params.stake, params.perWeek, params.margin, params.legs, seed]);

  const money = (v) => formatMoney(v, state.country);

  async function share() {
    const text = t('truth.shareText', { loss: money(results.loss), chance: formatPercent(results.year) });
    const url = globalThis.location.origin && globalThis.location.origin !== 'null' ? globalThis.location.origin : '';
    track('share', state.utm?.source);
    try {
      if (globalThis.navigator.share) {
        await globalThis.navigator.share({ text, url: url || undefined });
        return;
      }
    } catch { /* пользователь закрыл окно — пробуем скопировать */ }
    const copied = await copyText(url ? `${text} ${url}` : text);
    showToast(copied ? t('common.copied') : text);
  }

  return html`<${TopBar} title=${t('truth.title')} back=${state.onboarded ? 'protect' : 'welcome'} />
    <main class="screen">
      <p class="lead">${t('truth.lead')}</p>
      <section class="card">
        <h2>${t('truth.type')}</h2>
        <div class="chips">
          ${Object.keys(PRESETS).map((id) => html`<button type="button" class="chip" aria-pressed=${String(preset === id)}
            onClick=${() => choosePreset(id)}>${t(`truth.preset.${id}`)}</button>`)}
        </div>
        <${Field} label=${t('truth.odds')}>
          <input class="input" inputmode="decimal" value=${odds} onInput=${(e) => setOdds(e.currentTarget.value)} />
        <//>
        <${Field} label=${t('truth.stake')}>
          <${MoneyInput} id="truth-stake" value=${stake} onValue=${(v) => setStake(v)} country=${state.country} />
        <//>
        <${Field} label=${t('truth.perWeek')}>
          <input class="input" inputmode="numeric" value=${perWeek} onInput=${(e) => setPerWeek(e.currentTarget.value.replace(/\D/g, ''))} />
        <//>
        <${Field} label=${t('truth.margin')} hint=${t('truth.margin.hint')}>
          <input class="input" inputmode="decimal" value=${marginPct} onInput=${(e) => setMarginPct(e.currentTarget.value)} />
        <//>
      </section>

      ${!ok ? html`<p class="error-text" role="alert">${t('truth.invalid')}</p>` : html`
        <section class="card" aria-live="polite">
          <p class="small muted">${t('truth.result.share', { share: '' }).trim()}</p>
          <span class="big-number">${formatPercent(results.share, 1)}</span>
          <p>${t('truth.result.year', { staked: money(results.staked), loss: money(results.loss) })}</p>
          <p class="small">${t('truth.result.chance', { chance: formatPercent(results.year), chance3: formatPercent(results.three) })}</p>
        </section>
        <section class="card">
          <h3>${t('truth.chart.title')}</h3>
          <p class="small muted">${t('truth.chart.sub')}</p>
          <${BankrollChart} path=${path} expectedPerWeek=${results.loss / 52} formatMoney=${money} />
          <div class="row">
            <button type="button" class="btn secondary" style="flex:1" onClick=${() => setSeed(seed + 1)}>${t('truth.again')}</button>
            <button type="button" class="btn primary" style="flex:1" onClick=${share}><${Icon} name="share" size=${20} />${t('truth.share')}</button>
          </div>
        </section>`}
      ${state.onboarded ? null : html`<a class="btn primary block" href="#welcome">${t('truth.cta')}</a>`}
    </main>`;
}
