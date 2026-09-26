// Рисует PNG-иконки и картинку для превью ссылок из SVG с помощью Chromium (Playwright).
// Запуск: node scripts/icons.js (нужен установленный playwright).
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const icons = join(root, 'public/icons');
const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require('playwright');
} catch {
  playwright = require(join(execSync('npm root -g').toString().trim(), 'playwright'));
}

const svg = readFileSync(join(icons, 'icon.svg'), 'utf8');
const mark = svg.replace(/<rect[^>]*\/>/, '');
const maskable = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="#00856c"/>
  <g transform="translate(256 256) scale(0.72) translate(-256 -256)">${mark.replace(/<\/?svg[^>]*>/g, '')}</g></svg>`;

const og = `<div style="width:1200px;height:630px;display:flex;align-items:center;gap:56px;padding:0 88px;box-sizing:border-box;
  background:#00856c;color:#fff;font-family:system-ui,-apple-system,'Segoe UI',Roboto,'Noto Sans',sans-serif">
  <div style="width:280px;height:280px;flex:none">${svg.replace('<svg ', '<svg width="280" height="280" ').replace('fill="#00856c"', 'fill="#006b57"')}</div>
  <div>
    <div style="font-size:84px;font-weight:800;letter-spacing:-2px">Стоп-ставка</div>
    <div style="font-size:35px;line-height:1.35;margin-top:18px;opacity:.95">Помогает бросить ставки и казино.<br>Бесплатно и без регистрации.</div>
  </div>
</div>`;

const shots = [
  { file: 'icon-192.png', size: 192, html: svg },
  { file: 'icon-512.png', size: 512, html: svg },
  { file: 'apple-touch-icon.png', size: 180, html: maskable },
  { file: 'icon-maskable-512.png', size: 512, html: maskable },
  { file: 'og.png', width: 1200, height: 630, html: og },
];

const browser = await playwright.chromium.launch();
for (const shot of shots) {
  const width = shot.width || shot.size;
  const height = shot.height || shot.size;
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  const content = shot.html.startsWith('<svg') ? shot.html.replace('<svg ', `<svg width="${width}" height="${height}" `) : shot.html;
  await page.setContent(`<html><body style="margin:0;background:transparent">${content}</body></html>`);
  await page.screenshot({ path: join(icons, shot.file), omitBackground: true, clip: { x: 0, y: 0, width, height } });
  await page.close();
  console.log('icon', shot.file);
}
await browser.close();
