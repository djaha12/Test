import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, relative } from 'node:path';

const PUBLIC = new URL('../public/', import.meta.url).pathname;

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

test('service worker кэширует каждый JS-модуль и все файлы из списка существуют', () => {
  const sw = readFileSync(join(PUBLIC, 'sw.js'), 'utf8');
  const shell = [...sw.matchAll(/'([^']+)'/g)].map((m) => m[1]).filter((p) => p !== './' && !p.startsWith('stopstavka-') && !p.startsWith('/'));
  for (const file of walk(join(PUBLIC, 'js'))) {
    const rel = relative(PUBLIC, file);
    assert.ok(shell.includes(rel), `нет в SHELL: ${rel}`);
  }
  for (const rel of shell.filter((p) => p.includes('.'))) {
    assert.ok(existsSync(join(PUBLIC, rel)), `нет файла: ${rel}`);
  }
});

test('манифест: иконки существуют, есть maskable', () => {
  const manifest = JSON.parse(readFileSync(join(PUBLIC, 'manifest.webmanifest'), 'utf8'));
  assert.equal(manifest.display, 'standalone');
  assert.ok(manifest.icons.some((i) => i.purpose === 'maskable'));
  for (const icon of manifest.icons) assert.ok(existsSync(join(PUBLIC, icon.src)), icon.src);
});

test('все модули импортируют только существующие файлы', () => {
  for (const file of walk(join(PUBLIC, 'js'))) {
    const source = readFileSync(file, 'utf8');
    for (const [, spec] of source.matchAll(/from\s+'(\.[^']+)'/g)) {
      const target = new URL(spec, `file://${file}`).pathname;
      assert.ok(existsSync(target), `${relative(PUBLIC, file)} → ${spec}`);
    }
  }
});
