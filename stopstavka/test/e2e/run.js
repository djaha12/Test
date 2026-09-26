// Сквозной прогон в Chromium на ширине телефона: node test/e2e/run.js [папка-для-скриншотов]
import http from 'node:http';
import assert from 'node:assert/strict';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { join } from 'node:path';

import { loadConfig } from '../../server/config.js';
import { openDb } from '../../server/db.js';
import { issueCodes } from '../../server/codes.js';
import { createCoach } from '../../server/coach.js';
import { createApp } from '../../server/index.js';

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require('playwright');
} catch {
  playwright = require(join(execSync('npm root -g').toString().trim(), 'playwright'));
}

const shots = process.argv[2] || null;
const config = loadConfig({ APP_SECRET: 'e2e-secret-0123456789abcdef', AI_MOCK: '1', FREE_AI_PER_DAY: '5' });
const db = openDb(':memory:');
const server = http.createServer(createApp({ config, db, coach: createCoach({ config }) }));
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const base = `http://localhost:${server.address().port}`;

const browser = await playwright.chromium.launch();
const context = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'ru-RU' });
const page = await context.newPage();
const problems = [];
page.on('pageerror', (e) => problems.push(`pageerror: ${e.message}`));
page.on('console', (m) => { if (m.type() === 'error') problems.push(`console: ${m.text()}`); });

let step = 0;
async function check(name, fn) {
  step++;
  try {
    await fn();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 0, `горизонтальная прокрутка ${overflow}px`);
    console.log(`ok ${step} - ${name}`);
  } catch (err) {
    console.log(`not ok ${step} - ${name}\n  ${err.message.split('\n')[0]}`);
    if (shots) await page.screenshot({ path: join(shots, `fail-${step}.png`), fullPage: true });
    throw err;
  }
}
const shot = async (name) => { if (shots) await page.screenshot({ path: join(shots, `${name}.png`), fullPage: true }); };
const text = (s) => page.getByText(s, { exact: false }).first();

try {
  await check('ссылка из рекламы: калькулятор открывается сразу, utm запоминается', async () => {
    await page.goto(`${base}/?utm_source=tiktok&utm_campaign=truth1#truth`);
    await text('4,8%').waitFor();
    const utm = await page.evaluate(() => JSON.parse(localStorage.getItem('stopstavka:v1')).utm);
    assert.deepEqual(utm, { source: 'tiktok', campaign: 'truth1' });
    await page.getByRole('link', { name: 'Бросить ставки — начать бесплатно' }).click();
  });

  await check('приветствие', async () => {
    await text('Ставки больше не решают за вас').waitFor();
    await shot('01-welcome');
    await page.getByRole('button', { name: 'Начать' }).click();
  });

  await check('тест PGSI из 9 вопросов', async () => {
    await page.getByRole('button', { name: 'Пройти тест' }).click();
    for (let i = 1; i <= 9; i++) {
      await text(`Вопрос ${i} из 9`).waitFor();
      await page.getByRole('button', { name: 'Иногда' }).click();
    }
    await text('Ваш результат: 9 из 27').waitFor();
    await text('Похоже, ставки стали зависимостью').waitFor();
    await page.getByRole('button', { name: 'Составить план' }).click();
  });

  await check('план: дата, траты, причины, цель, близкий', async () => {
    await page.getByRole('button', { name: 'Вчера' }).click();
    await page.locator('#weekly-spend').fill('7000');
    await text('Это примерно 364').waitFor();
    await page.getByRole('button', { name: 'Закрыть долги' }).click();
    await page.getByPlaceholder('Например: закрыть кредит').fill('Закрыть кредит');
    await page.locator('#goal-amount').fill('90000');
    await page.locator('input[type="tel"]').fill('+996 555 123 456');
    await page.getByLabel('Имя').fill('Азамат');
    await page.getByRole('button', { name: 'Сохранить план' }).click();
    await text('Первый шаг — закрыть доступ').waitFor();
  });

  await check('защита: отметка шага и инструкция с сайтами', async () => {
    await page.getByRole('link', { name: 'Заблокировать букмекеров' }).click();
    await text('Сделано 0 из 7').waitFor();
    await page.getByRole('button', { name: 'Сделано' }).first().click();
    await text('Сделано 1 из 7').waitFor();
    await page.getByRole('button', { name: 'Включите фильтр сайтов ставок' }).click();
    await text('nextdns.io').waitFor();
    await text('olimpbet.kz').waitFor();
  });

  await check('главная: 1 день, 1 000 сом, цель', async () => {
    await page.getByRole('link', { name: 'Главная' }).click();
    await text('день без ставок').waitFor();
    await text('1 000 сом').waitFor();
    await text('Цель: Закрыть кредит').waitFor();
    await shot('02-home');
  });

  await check('SOS: таймер, дыхание, кнопка «Написать», итог', async () => {
    await page.getByRole('link', { name: 'Тянет поставить' }).click();
    await page.getByRole('button', { name: 'Переждать 10 минут' }).click();
    await text('Осталось 9:5').waitFor();
    await text('Закрыть долги').waitFor();
    const wa = await page.getByRole('link', { name: /Написать: Азамат/ }).getAttribute('href');
    assert.match(wa, /^https:\/\/wa\.me\/996555123456\?text=/);
    await shot('03-sos');
    await page.getByRole('button', { name: 'Мне лучше' }).click();
    await page.getByRole('button', { name: 'Скука' }).click();
    await page.getByRole('button', { name: 'Тяга прошла' }).click();
    await text('Вы справились').waitFor();
    await page.getByRole('link', { name: 'На главную' }).click();
    await text('1 раз').waitFor();
  });

  await check('дневник: отметка и графики', async () => {
    await page.getByRole('link', { name: 'Дневник' }).click();
    await page.getByRole('button', { name: 'Плохо', exact: true }).click();
    await page.locator('#checkin-urge').fill('7');
    await page.getByRole('button', { name: 'Матч или турнир' }).click();
    await page.getByRole('button', { name: 'Сохранить отметку' }).click();
    await text('Отметка сохранена').waitFor();
    await page.locator('svg[aria-label="Сила тяги по дням"]').waitFor();
    await text('Что чаще всего провоцирует').waitFor();
    await page.locator('.col-hit').last().focus();
    await page.locator('.chart-tip').waitFor();
    await shot('04-journal');
  });

  await check('правда о ставках: расчёт и симуляция', async () => {
    await page.goto(`${base}/#truth`);
    await text('4,8%').waitFor();
    await text('В среднем это минус').waitFor();
    await page.getByRole('button', { name: 'Экспресс из 3' }).click();
    await text('13,6%').waitFor();
    await page.getByRole('button', { name: 'Прожить год ещё раз' }).click();
    await page.locator('svg[aria-label="Одна из возможных историй за год"]').hover();
    await shot('05-truth');
  });

  await check('ИИ-поддержка: потоковый ответ', async () => {
    await page.goto(`${base}/#coach`);
    await page.getByPlaceholder('Напишите, что происходит…').fill('Очень тянет поставить на матч');
    await page.getByRole('button', { name: 'Отправить' }).click();
    await text('проходит, как волна').waitFor({ timeout: 10000 });
    await text('Бесплатных сообщений сегодня: 4').waitFor();
  });

  await check('подписка: активация кода', async () => {
    const [code] = issueCodes(db, config.appSecret, { days: 30 });
    await page.goto(`${base}/#premium`);
    await text('390').waitFor();
    await page.getByPlaceholder('SS-XXXX-XXXX').fill(code.toLowerCase());
    await page.getByRole('button', { name: 'Активировать' }).click();
    await text('«Плюс» активен до').waitFor();
  });

  await check('язык: кыргызча и обратно', async () => {
    await page.goto(`${base}/#settings`);
    await page.getByRole('button', { name: 'Кыргызча' }).click();
    await page.getByRole('link', { name: 'Башкы бет' }).waitFor();
    await page.getByRole('button', { name: 'Русский' }).click();
    await page.getByRole('link', { name: 'Главная' }).waitFor();
  });

  await check('срыв: счётчик начинается заново', async () => {
    await page.goto(`${base}/#home`);
    await page.getByRole('button', { name: 'Я сорвался' }).click();
    await page.locator('#relapse-lost').fill('3000');
    await page.getByRole('button', { name: 'Начать заново с сегодняшнего дня' }).click();
    await text('Сегодня — первый день').waitFor();
  });

  await check('удаление всех данных', async () => {
    await page.goto(`${base}/#settings`);
    await page.getByRole('button', { name: 'Удалить все данные' }).click();
    await page.getByRole('button', { name: 'Да, удалить' }).click();
    await text('Ставки больше не решают за вас').waitFor();
  });

  await check('тёмная тема отрисовывается', async () => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto(`${base}/#truth`);
    await shot('06-dark');
  });

  assert.deepEqual(problems, [], `ошибки в консоли:\n${problems.join('\n')}`);
  console.log(`\nВсе шаги пройдены: ${step}`);
} catch (err) {
  if (problems.length) console.log('Ошибки в консоли:\n' + problems.join('\n'));
  process.exitCode = 1;
} finally {
  await browser.close();
  server.close();
}
