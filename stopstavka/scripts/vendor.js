// Копирует Preact + htm (один ES-модуль без сборки) в public/js/vendor.
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = join(root, 'node_modules/htm/preact/standalone.module.js');
const dest = join(root, 'public/js/vendor/preact-htm.js');
mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log('vendored', dest);
