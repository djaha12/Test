import { html } from '../../vendor/preact-htm.js';
import { t, tList } from '../../core/i18n.js';
import { Icon, SettingsLink, TopBar } from '../components.js';
import { CONTACTS, GAMBLERS_ANONYMOUS_URL } from '../../content/contacts.js';

export function HelpScreen({ state }) {
  const contacts = CONTACTS[state.country] || CONTACTS.kg;
  return html`<${TopBar} title=${t('help.title')} right=${html`<${SettingsLink} />`} />
    <main class="screen">
      <section class="card" style="border-color:var(--sos)">
        <h2>${t('help.now.title')}</h2>
        <p>${t('help.now.text')}</p>
        <ul class="plain">
          ${contacts.map((c) => html`<li class="row between">
            <span><strong style="font-size:20px">${c.phone}</strong><br /><span class="small muted">${t(c.labelKey)}</span></span>
            <a class="btn danger" href=${`tel:${c.phone}`} aria-label=${`${t('sos.buddy.call')} ${c.phone}`}><${Icon} name="phone" size=${20} /></a>
          </li>`)}
        </ul>
      </section>

      <a class="card link" href="#coach">
        <div class="row between"><h2>${t('help.coach.title')}</h2><${Icon} name="spark" /></div>
        <p>${t('help.coach.text')}</p>
        <span class="btn secondary">${t('help.coach.go')}</span>
      </a>

      <section class="card">
        <h2>${t('help.pro.title')}</h2>
        <p>${t('help.pro.text')}</p>
      </section>

      <section class="card">
        <h2>${t('help.groups.title')}</h2>
        <p>${t('help.groups.text')}</p>
        <a href=${GAMBLERS_ANONYMOUS_URL} target="_blank" rel="noopener">gamblersanonymous.org</a>
      </section>

      <section class="card">
        <h2>${t('help.family.title')}</h2>
        <ul class="plain check-list">${tList('help.family').map((line) => html`<li><${Icon} name="check" size=${18} /><span>${line}</span></li>`)}</ul>
      </section>
    </main>`;
}
