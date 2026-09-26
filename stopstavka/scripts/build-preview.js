// Собирает демо-версию в одну HTML-страницу (без сервера: ИИ и оплата выключены).
// Запуск: node scripts/build-preview.js [путь-к-файлу]  (по умолчанию dist/preview.html)
import { build } from 'esbuild';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = process.argv[2] || join(root, 'dist/preview.html');

const result = await build({
  entryPoints: [join(root, 'public/js/main.js')],
  bundle: true,
  format: 'esm',
  minify: true,
  target: 'es2020',
  write: false,
  legalComments: 'none',
});
const js = `globalThis.__STOPSTAVKA_DEMO__=true;\n${result.outputFiles[0].text}`.replace(/<\/script/gi, '<\\/script');
const css = readFileSync(join(root, 'public/css/app.css'), 'utf8');

const html = `<title>Стоп-ставка</title>
<meta name="description" content="Демо веб-приложения, которое помогает бросить ставки">
<style>
${css}
</style>
<div id="app"></div>
<script type="module">
${js}
</script>
`;
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, html);
console.log(`preview: ${out} (${Math.round(html.length / 1024)} КБ)`);
