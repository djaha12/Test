// Рендер 3D-видов через headless Chromium: node render3d.js
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const dir = path.resolve(__dirname, '../3d');
  const out = path.resolve(__dirname, '../renders');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const views = [
    ['ne', '', '01_вид_с_северо-востока'],
    ['sw', '', '02_вид_со_стороны_сада'],
    ['n', '', '03_вид_с_улицы'],
    ['top', 'roof', '04_план_2_этажа_3D'],
    ['top', 'roof_fl2', '05_план_1_этажа_3D'],
    ['int1', '', '06_интерьер_1_этаж'],
  ];
  for (const [view, hide, name] of views) {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
    const url = 'file://' + path.join(dir, 'viewer.html') + `?view=${view}&hide=${hide}&ui=0`;
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(out, name + '.png') });
    await page.close();
    console.log('ok', name);
  }
  await browser.close();
})();
