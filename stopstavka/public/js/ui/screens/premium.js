import { html, useEffect, useState } from '../../vendor/preact-htm.js';
import { t, tList } from '../../core/i18n.js';
import { isPremium, showToast, store } from '../../core/state.js';
import { getConfig, redeemCode, track } from '../../core/api.js';
import { Field, Icon, TopBar } from '../components.js';
import { formatMoney } from '../../logic/format.js';

export function PremiumScreen({ state }) {
  const [config, setConfig] = useState(undefined);
  const [code, setCode] = useState('');
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const active = isPremium(state);

  useEffect(() => {
    getConfig().then(setConfig);
    track('premium_view', state.utm?.source);
  }, []);

  const prices = config?.prices?.[state.country] || null;
  const pay = config?.payment?.[state.country] || null;

  async function activate(e) {
    e.preventDefault();
    if (!code.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const { token, exp } = await redeemCode(code.trim(), state.deviceId);
      store.set((s) => ({ ...s, premium: { token, exp } }));
      track('premium_redeemed', state.utm?.source);
      showToast(t('premium.done'));
      setCode('');
    } catch (err) {
      setError(err.code === 'used' ? 'used' : err.code === 'rate_limited' ? 'rate' : 'invalid');
    } finally {
      setBusy(false);
    }
  }

  const until = active ? new Date(state.premium.exp).toLocaleDateString('ru-RU') : null;

  return html`<${TopBar} title=${t('premium.title')} back="settings" />
    <main class="screen">
      ${active ? html`<span class="badge"><${Icon} name="check" size=${16} />${t('premium.active', { date: until })}</span>` : null}
      <p class="lead">${t('premium.lead')}</p>
      <section class="card">
        <ul class="plain check-list">${tList('premium.features').map((f) => html`<li><${Icon} name="check" size=${18} /><span>${f}</span></li>`)}</ul>
      </section>
      ${prices ? html`<section class="card">
        <ul class="plain">
          ${['1', '3', '12'].filter((m) => prices[m]).map((m) => html`<li class="row between">
            <span>${t(`premium.plan.${m}`)}</span><strong>${formatMoney(prices[m], state.country)}</strong>
          </li>`)}
        </ul>
      </section>` : null}
      <section class="card">
        <h2>${t('premium.how')}</h2>
        <p>${pay?.phone && pay?.contact
          ? t(`premium.pay.${state.country}`, { phone: pay.phone, contact: pay.contact })
          : t('premium.pay.soon')}</p>
      </section>
      <form class="card" onSubmit=${activate}>
        <${Field} label=${t('premium.code')}
          error=${error ? t(`premium.error.${error}`) : null}>
          <input class="input" autocomplete="one-time-code" autocapitalize="characters" spellcheck="false"
            placeholder="SS-XXXX-XXXX" value=${code} onInput=${(e) => setCode(e.currentTarget.value.toUpperCase())} />
        <//>
        <button type="submit" class="btn primary" disabled=${busy || !code.trim() || config === null}>${t('premium.activate')}</button>
      </form>
    </main>`;
}
