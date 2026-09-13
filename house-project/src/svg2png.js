// Конвертация SVG-листов в PNG через headless Chromium (Playwright).
// Использование: node svg2png.js <dir> [deviceScaleFactor]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = path.resolve(process.argv[2] || '../drawings');
  const dsf = parseFloat(process.argv[3] || '1');
  const only = process.argv[4] || null;
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg') && (!only || f.includes(only)));
  const browser = await chromium.launch();
  for (const f of files) {
    const svgPath = path.join(dir, f);
    const svg = fs.readFileSync(svgPath, 'utf8');
    const m = svg.match(/<svg[^>]*width="([\d.]+)"[^>]*height="([\d.]+)"/);
    const w = Math.round(parseFloat(m[1])), h = Math.round(parseFloat(m[2]));
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dsf });
    await page.goto('file://' + svgPath, { waitUntil: 'load' });
    await page.waitForTimeout(100);
    const png = svgPath.replace(/\.svg$/, '.png');
    await page.screenshot({ path: png, fullPage: false });
    await page.close();
    console.log('ok', f, w + 'x' + h);
  }
  await browser.close();
})();
