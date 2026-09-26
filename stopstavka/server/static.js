import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
};

export const SECURITY_HEADERS = {
  'content-security-policy': [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self'",
    "img-src 'self' data:",
    "connect-src 'self'",
    "manifest-src 'self'",
    "worker-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ].join('; '),
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'no-referrer',
  'permissions-policy': 'camera=(), microphone=(), geolocation=(), payment=()',
  'cross-origin-opener-policy': 'same-origin',
};

// Без кэша — то, что должно обновляться сразу после выкладки новой версии.
const NO_CACHE = new Set(['/index.html', '/sw.js', '/manifest.webmanifest']);

export function createStaticHandler(root) {
  const base = normalize(root + sep);
  return async function serveStatic(req, res, pathname) {
    let path;
    try {
      path = decodeURIComponent(pathname);
    } catch {
      return false;
    }
    if (path === '/' || path === '') path = '/index.html';
    const file = normalize(join(base, path));
    if (!file.startsWith(base) || path.includes('\0')) return false;
    let info;
    try {
      info = await stat(file);
    } catch {
      return false;
    }
    if (!info.isFile()) return false;
    const type = TYPES[extname(file)] || 'application/octet-stream';
    res.writeHead(200, {
      ...SECURITY_HEADERS,
      'content-type': type,
      'content-length': info.size,
      'cache-control': NO_CACHE.has(path) ? 'no-cache' : 'public, max-age=3600',
    });
    if (req.method === 'HEAD') {
      res.end();
      return true;
    }
    createReadStream(file).pipe(res);
    return true;
  };
}
