// Увеличенный фрагмент SVG-листа для визуальной проверки.
// node svgclip.js <svgfile> <x_mm> <y_mm> <w_mm> <h_mm> <out.png> [px_per_mm]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [svgPath, x, y, w, h, out] = process.argv.slice(2);
  const ppm = parseFloat(process.argv[8] || '8');
  const svg = fs.readFileSync(path.resolve(svgPath), 'utf8');
  const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  const W = parseFloat(m[1]), H = parseFloat(m[2]);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: Math.round(w * ppm), height: Math.round(h * ppm) } });
  const inner = svg.replace(/<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
  const html = `<html><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="${w * ppm}" height="${h * ppm}" viewBox="${x} ${y} ${w} ${h}">${inner}</svg></body></html>`;
  await page.setContent(html);
  await page.waitForTimeout(100);
  await page.screenshot({ path: out });
  await browser.close();
  console.log('ok', out);
})();
