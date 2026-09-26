// Администрирование из командной строки:
//   npm run codes -- issue --days 30 --count 5 --note "MBank 26.09"
//   npm run codes -- stats --days 30
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { parseArgs } from 'node:util';

import { loadConfig } from './config.js';
import { openDb } from './db.js';
import { issueCodes } from './codes.js';
import { eventStats } from './events.js';

const { positionals, values } = parseArgs({
  allowPositionals: true,
  options: {
    days: { type: 'string', default: '30' },
    count: { type: 'string', default: '1' },
    note: { type: 'string', default: '' },
  },
});

const config = loadConfig();
mkdirSync(config.dataDir, { recursive: true });
const db = openDb(join(config.dataDir, 'stopstavka.db'));
const command = positionals[0];

if (command === 'issue') {
  const codes = issueCodes(db, config.appSecret, { days: Number(values.days), count: Number(values.count), note: values.note });
  console.log(`Коды на ${values.days} дн.:`);
  for (const code of codes) console.log(code);
} else if (command === 'stats') {
  const stats = eventStats(db, { days: Number(values.days) });
  console.log(`События с ${stats.since}:`);
  console.table(stats.totals);
  console.log('По источникам (utm_source):');
  console.table(stats.bySource);
  const redeemed = db.prepare('SELECT COUNT(*) AS n FROM codes WHERE redeemed_at IS NOT NULL').get().n;
  const issued = db.prepare('SELECT COUNT(*) AS n FROM codes').get().n;
  console.log(`Коды: выдано ${issued}, активировано ${redeemed}`);
} else {
  console.log('Команды: issue --days 30 --count 1 --note "..." | stats --days 30');
  process.exitCode = 1;
}
