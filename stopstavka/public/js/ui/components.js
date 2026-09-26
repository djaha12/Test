import { html, useEffect, useRef, useState } from '../vendor/preact-htm.js';
import { onToast } from '../core/state.js';
import { t } from '../core/i18n.js';
import { CURRENCY, parseAmount } from '../logic/format.js';

// Иконки: 24×24, линия 2px, цвет — currentColor.
const ICONS = {
  home: html`<path d="M3 11 12 4l9 7" /><path d="M5 10v10h14V10" /><path d="M10 20v-6h4v6" />`,
  journal: html`<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z" /><path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H19" /><path d="M9 7h6M9 11h4" />`,
  shield: html`<path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z" /><path d="m9 12 2 2 4-4" />`,
  help: html`<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" />`,
  settings: html`<path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1" /><circle cx="15" cy="6" r="2" /><circle cx="9" cy="12" r="2" /><circle cx="17" cy="18" r="2" />`,
  back: html`<path d="m15 18-6-6 6-6" />`,
  chevron: html`<path d="m9 18 6-6-6-6" />`,
  check: html`<path d="m5 12 5 5L20 7" />`,
  close: html`<path d="M18 6 6 18M6 6l12 12" />`,
  copy: html`<rect x="8" y="8" width="12" height="12" rx="2" /><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" />`,
  share: html`<path d="M12 3v12" /><path d="m7 8 5-5 5 5" /><path d="M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" />`,
  phone: html`<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2" />`,
  message: html`<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" />`,
  spark: html`<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" /><path d="M19 17v4M17 19h4" />`,
  lock: html`<rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" />`,
  download: html`<path d="M12 4v11" /><path d="m7 10 5 5 5-5" /><path d="M5 20h14" />`,
  upload: html`<path d="M12 20V9" /><path d="m7 14 5-5 5 5" /><path d="M5 4h14" />`,
  trash: html`<path d="M4 7h16" /><path d="M10 11v6M14 11v6" /><path d="M6 7l1 13h10l1-13" /><path d="M9 7V4h6v3" />`,
  calc: html`<rect x="5" y="3" width="14" height="18" rx="2" /><path d="M8 7h8M8 12h2M14 12h2M8 16h2M14 16h2" />`,
};

export function Icon({ name, size = 24, label }) {
  return html`<svg width=${size} height=${size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
    role=${label ? 'img' : undefined} aria-label=${label} aria-hidden=${label ? undefined : 'true'}>${ICONS[name]}</svg>`;
}

export function TopBar({ title, back, right }) {
  return html`<header class="topbar">
    ${back ? html`<a class="icon-btn" href=${'#' + back} aria-label=${t('common.back')}><${Icon} name="back" /></a>` : null}
    <h1>${title}</h1>
    ${right}
  </header>`;
}

export function SettingsLink() {
  return html`<a class="icon-btn" href="#settings" aria-label=${t('nav.settings')}><${Icon} name="settings" /></a>`;
}

export function Chip({ pressed, onClick, children }) {
  return html`<button type="button" class="chip" aria-pressed=${String(Boolean(pressed))} onClick=${onClick}>${children}</button>`;
}

export function Segmented({ value, options, onChange, label }) {
  return html`<div class="segmented" role="group" aria-label=${label}>
    ${options.map((o) => html`<button type="button" aria-pressed=${String(o.value === value)} onClick=${() => onChange(o.value)}>${o.label}</button>`)}
  </div>`;
}

// Подпись для группы кнопок (Segmented, чипы). Не <label>: иначе нажатие на подпись
// нажимает первую кнопку, а её доступное имя подменяется текстом подписи.
export function Group({ label, children }) {
  return html`<div class="field">
    <span>${label}</span>
    ${children}
  </div>`;
}

export function Field({ label, hint, error, children }) {
  return html`<label class="field">
    <span>${label}</span>
    ${children}
    ${hint ? html`<small class="muted tiny">${hint}</small>` : null}
    ${error ? html`<p class="error-text" role="alert">${error}</p>` : null}
  </label>`;
}

// Поле для суммы: хранит строку, наружу отдаёт число (NaN, если пусто).
export function MoneyInput({ id, value, onValue, country, placeholder = '0' }) {
  const [text, setText] = useState(value > 0 ? String(value) : '');
  return html`<div class="input-suffix">
    <input id=${id} class="input" inputmode="numeric" autocomplete="off" placeholder=${placeholder} value=${text}
      onInput=${(e) => { setText(e.currentTarget.value); onValue(parseAmount(e.currentTarget.value)); }} />
    <em>${CURRENCY[country] || CURRENCY.kg}</em>
  </div>`;
}

export function Meter({ value, label }) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return html`<div class="meter" role="progressbar" aria-label=${label} aria-valuemin="0" aria-valuemax="100" aria-valuenow=${pct}>
    <i style=${`width:${pct}%`}></i>
  </div>`;
}

export function Stat({ label, value, hint }) {
  return html`<div class="stat">
    <span class="label">${label}</span>
    <span class="value">${value}</span>
    ${hint ? html`<span class="hint">${hint}</span>` : null}
  </div>`;
}

export function Sheet({ open, onClose, title, children }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    globalThis.addEventListener('keydown', onKey);
    ref.current?.querySelector('button, input, textarea, a')?.focus();
    return () => globalThis.removeEventListener('keydown', onKey);
  }, [open]);
  if (!open) return null;
  return html`<div class="sheet-backdrop" onClick=${(e) => { if (e.target === e.currentTarget) onClose(); }}>
    <section class="sheet" role="dialog" aria-modal="true" aria-label=${title} ref=${ref}>
      <div class="row between">
        <h2>${title}</h2>
        <button type="button" class="icon-btn" aria-label=${t('common.close')} onClick=${onClose}><${Icon} name="close" /></button>
      </div>
      ${children}
    </section>
  </div>`;
}

export function ToastHost() {
  const [text, setText] = useState('');
  useEffect(() => {
    let timer;
    onToast((message) => {
      setText(message);
      clearTimeout(timer);
      timer = setTimeout(() => setText(''), 2600);
    });
    return () => clearTimeout(timer);
  }, []);
  return text ? html`<div class="toast" role="status">${text}</div>` : null;
}

// Копирование в буфер обмена с запасным вариантом: выделяем текст, если API недоступен.
export async function copyText(text, fallbackEl) {
  try {
    await globalThis.navigator.clipboard.writeText(text);
    return true;
  } catch {
    if (fallbackEl) {
      const range = globalThis.document.createRange();
      range.selectNodeContents(fallbackEl);
      const selection = globalThis.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
    return false;
  }
}
