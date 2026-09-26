import { html, useRef, useState } from '../vendor/preact-htm.js';
import { t } from '../core/i18n.js';

// Графики на SVG. Правила: тонкие метки, одна ось, подписи — цветом текста, подсказка при наведении
// и фокусе, табличный вид для каждого графика.

function shortDate(iso) {
  const [, m, d] = iso.split('-');
  return `${d}.${m}`;
}

export function compactNumber(value) {
  const abs = Math.abs(value);
  const sign = value < 0 ? '−' : '';
  if (abs >= 1e6) return `${sign}${(abs / 1e6).toFixed(abs >= 1e7 ? 0 : 1).replace('.', ',')} ${t('unit.m')}`;
  if (abs >= 1e3) return `${sign}${Math.round(abs / 1e3)} ${t('unit.k')}`;
  return `${sign}${Math.round(abs)}`;
}

export function niceTicks(min, max, count = 4) {
  const span = max - min || 1;
  const raw = span / count;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const f = raw / pow;
  const step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * pow;
  const lo = Math.floor(min / step) * step;
  const hi = Math.ceil(max / step) * step;
  const ticks = [];
  for (let v = lo; v <= hi + step / 2; v += step) ticks.push(Math.round(v));
  return { lo, hi, ticks };
}

function useTip() {
  const box = useRef(null);
  const [tip, setTip] = useState(null);
  function place(svgX, svgY, width, content) {
    const el = box.current;
    if (!el) return;
    const scale = el.clientWidth / width;
    const left = Math.max(70, Math.min(el.clientWidth - 70, svgX * scale));
    setTip({ left, top: svgY * scale, content });
  }
  return { box, tip, place, clear: () => setTip(null) };
}

function Tip({ tip }) {
  if (!tip) return null;
  return html`<div class="chart-tip" style=${`left:${tip.left}px;top:${tip.top}px`}>${tip.content}</div>`;
}

function columnPath(x, y, w, base) {
  const r = Math.min(4, w / 2, (base - y));
  if (base - y < 1) return '';
  return `M${x},${base}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${base}Z`;
}

// Сила тяги по дням (0–10), дни со ставкой отмечены крестиком.
export function UrgeChart({ series }) {
  const W = 340;
  const H = 180;
  const left = 22;
  const right = 6;
  const top = 18;
  const bottom = 24;
  const plotW = W - left - right;
  const plotH = H - top - bottom;
  const base = top + plotH;
  const n = series.length;
  const band = plotW / n;
  const colW = Math.max(2, Math.min(16, band * 0.62));
  const y = (v) => top + plotH - (v / 10) * plotH;
  const labelEvery = n <= 14 ? 3 : 15;
  const { box, tip, place, clear } = useTip();
  const lastIndex = series.map((d) => d.value !== null).lastIndexOf(true);

  const describe = (d) => html`<strong>${d.value === null ? t('insights.noData') : `${d.value} / 10`}</strong>
    <span>${shortDate(d.date)}${d.bet ? ` · ${t('insights.betDay')}` : ''}</span>`;

  return html`<div class="stack">
    <div class="chart" ref=${box} onPointerLeave=${clear}>
      <svg viewBox=${`0 0 ${W} ${H}`} role="img" aria-label=${t('insights.urge.title')}>
        ${[0, 5, 10].map((v) => html`<line class=${v === 0 ? 'axis' : 'grid'} x1=${left} x2=${W - right} y1=${y(v)} y2=${y(v)} />
          <text x=${left - 6} y=${y(v) + 4} text-anchor="end">${v}</text>`)}
        ${series.map((d, i) => {
          const cx = left + band * i + band / 2;
          const x = cx - colW / 2;
          const top = d.value === null ? base : y(d.value);
          return html`<g>
            ${d.value === null
              ? html`<circle class="nodata" cx=${cx} cy=${base - 3} r="1.6" />`
              : html`<path class="col" d=${columnPath(x, top, colW, base) || `M${x},${base - 2}h${colW}v2h-${colW}Z`} />`}
            ${d.bet ? html`<path class="bet-mark" d=${`M${cx - 4},${top - 12}l8,8M${cx + 4},${top - 12}l-8,8`} />` : null}
            ${i === lastIndex && n <= 14 && d.value !== null && !d.bet
              ? html`<text class="end-label" x=${cx} y=${top - 5} text-anchor="middle">${d.value}</text>`
              : null}
            ${(i % labelEvery === 0 || i === n - 1) && (n - 1 - i >= labelEvery / 2 || i === n - 1)
              ? html`<text x=${cx} y=${H - 6} text-anchor="middle">${shortDate(d.date)}</text>`
              : null}
            <rect class="col-hit" x=${left + band * i} y=${top - 16 < 0 ? 0 : 0} width=${band} height=${base}
              tabindex=${n <= 14 ? 0 : -1} aria-label=${`${shortDate(d.date)}: ${d.value === null ? t('insights.noData') : d.value}`}
              onPointerMove=${() => place(cx, Math.min(top, base) - 6, W, describe(d))}
              onFocus=${() => place(cx, Math.min(top, base) - 6, W, describe(d))}
              onBlur=${clear} />
          </g>`;
        })}
      </svg>
      <${Tip} tip=${tip} />
    </div>
    <div class="legend">
      <span><i class="key col"></i>${t('insights.urge.sub')}</span>
      <span><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 2l8 8M10 2l-8 8" stroke="var(--chart-critical)" stroke-width="2" stroke-linecap="round" /></svg>${t('insights.betDay')}</span>
    </div>
    <details class="table-view">
      <summary>${t('insights.table')}</summary>
      <div class="table-wrap"><table class="data">
        <thead><tr><th>${t('insights.col.date')}</th><th class="num">${t('insights.col.urge')}</th><th>${t('insights.col.bet')}</th></tr></thead>
        <tbody>${[...series].reverse().map((d) => html`<tr>
          <td>${shortDate(d.date)}</td>
          <td class="num">${d.value === null ? '—' : d.value}</td>
          <td>${d.bet ? t('common.yes') : '—'}</td>
        </tr>`)}</tbody>
      </table></div>
    </details>
  </div>`;
}

// Горизонтальные полосы: что чаще всего провоцирует тягу. Значение — на конце полосы.
export function TriggerBars({ items }) {
  const max = Math.max(1, ...items.map((i) => i.count));
  return html`<div class="bars">
    ${items.map((item) => html`<div class="bar-row">
      <div class="top"><span>${t(`trigger.${item.id}`)}</span><span>${t('insights.triggers.count', { n: item.count })}</span></div>
      <div class="bar-track"><div class="bar-fill" style=${`width:${(item.count / max) * 100}%`}></div></div>
    </div>`)}
  </div>`;
}

// Счёт игрока по неделям в одной истории и средний (ожидаемый) результат.
export function BankrollChart({ path, expectedPerWeek, formatMoney }) {
  const W = 340;
  const H = 210;
  const left = 46;
  const right = 12;
  const top = 12;
  const bottom = 26;
  const plotW = W - left - right;
  const plotH = H - top - bottom;
  const weeks = path.length - 1;
  const expected = path.map((p) => ({ week: p.week, net: -expectedPerWeek * p.week }));
  const values = [0, ...path.map((p) => p.net), ...expected.map((p) => p.net)];
  const { lo, hi, ticks } = niceTicks(Math.min(...values), Math.max(...values), 4);
  const x = (w) => left + (w / weeks) * plotW;
  const y = (v) => top + ((hi - v) / (hi - lo || 1)) * plotH;
  const line = (pts) => pts.map((p, i) => `${i ? 'L' : 'M'}${x(p.week).toFixed(1)},${y(p.net).toFixed(1)}`).join('');
  const { box, tip, place, clear } = useTip();
  const [focusWeek, setFocusWeek] = useState(null);

  function show(week) {
    const w = Math.max(0, Math.min(weeks, week));
    setFocusWeek(w);
    place(x(w), Math.min(y(path[w].net), y(expected[w].net)) - 8, W, html`
      <span>${t('truth.chart.week', { n: w })}</span>
      <strong>${formatMoney(path[w].net)}</strong>
      <span><i class="key"></i>${t('truth.chart.path')}</span><br />
      <span><i class="key muted"></i>${t('truth.chart.expected')}: ${formatMoney(expected[w].net)}</span>`);
  }

  function onMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const svgX = ((e.clientX - rect.left) / rect.width) * W;
    show(Math.round(((svgX - left) / plotW) * weeks));
  }

  function onKey(e) {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    e.preventDefault();
    show((focusWeek ?? weeks) + (e.key === 'ArrowRight' ? 1 : -1));
  }

  const endMain = y(path[weeks].net);
  const endExp = y(expected[weeks].net);
  const labelsFit = Math.abs(endMain - endExp) >= 14;
  const quarters = [0, 13, 26, 39, 52].filter((w) => w <= weeks);

  return html`<div class="stack">
    <div class="legend">
      <span><i class="key"></i>${t('truth.chart.path')}</span>
      <span><i class="key muted"></i>${t('truth.chart.expected')}</span>
    </div>
    <div class="chart" ref=${box}>
      <svg viewBox=${`0 0 ${W} ${H}`} role="img" aria-label=${t('truth.chart.title')}
        onPointerMove=${onMove} onPointerLeave=${() => { clear(); setFocusWeek(null); }}>
        ${ticks.map((v) => html`<line class=${v === 0 ? 'zero' : 'grid'} x1=${left} x2=${W - right} y1=${y(v)} y2=${y(v)} />
          <text x=${left - 6} y=${y(v) + 4} text-anchor="end">${compactNumber(v)}</text>`)}
        ${quarters.map((w) => html`<text x=${x(w)} y=${H - 8} text-anchor="middle">${w}</text>`)}
        <path class="line-muted" d=${line(expected)} />
        <path class="line-main" d=${line(path)} />
        ${labelsFit ? html`
          <text class="end-label" x=${W - right} y=${endMain - 6} text-anchor="end">${compactNumber(path[weeks].net)}</text>
          <text class="end-label" x=${W - right} y=${endExp + 14} text-anchor="end">${compactNumber(expected[weeks].net)}</text>` : null}
        ${focusWeek !== null ? html`
          <line class="crosshair" x1=${x(focusWeek)} x2=${x(focusWeek)} y1=${top} y2=${top + plotH} />
          <circle class="dot muted" cx=${x(focusWeek)} cy=${y(expected[focusWeek].net)} r="4.5" />
          <circle class="dot" cx=${x(focusWeek)} cy=${y(path[focusWeek].net)} r="4.5" />` : null}
        <rect x=${left} y=${top} width=${plotW} height=${plotH} fill="transparent" tabindex="0"
          aria-label=${t('truth.chart.title')} onKeyDown=${onKey} onFocus=${() => show(weeks)} onBlur=${() => { clear(); setFocusWeek(null); }} />
      </svg>
      <${Tip} tip=${tip} />
    </div>
    <details class="table-view">
      <summary>${t('insights.table')}</summary>
      <div class="table-wrap"><table class="data">
        <thead><tr><th>${t('truth.chart.week', { n: '' }).trim()}</th><th class="num">${t('truth.chart.path')}</th><th class="num">${t('truth.chart.expected')}</th></tr></thead>
        <tbody>${quarters.map((w) => html`<tr>
          <td>${w}</td><td class="num">${formatMoney(path[w].net)}</td><td class="num">${formatMoney(expected[w].net)}</td>
        </tr>`)}</tbody>
      </table></div>
    </details>
  </div>`;
}
