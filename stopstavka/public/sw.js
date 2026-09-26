// Service worker: приложение открывается и работает без интернета (кроме ИИ-поддержки и оплаты).
// При изменении файлов увеличьте VERSION — старый кэш удалится.
const VERSION = 'stopstavka-v0.1.0';

const SHELL = [
  './',
  'index.html',
  'manifest.webmanifest',
  'css/app.css',
  'icons/icon.svg',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/apple-touch-icon.png',
  'js/main.js',
  'js/vendor/preact-htm.js',
  'js/core/api.js',
  'js/core/i18n.js',
  'js/core/state.js',
  'js/core/store.js',
  'js/logic/betting.js',
  'js/logic/dates.js',
  'js/logic/format.js',
  'js/logic/insights.js',
  'js/logic/pgsi.js',
  'js/logic/progress.js',
  'js/content/blocking.js',
  'js/content/contacts.js',
  'js/content/kk.js',
  'js/content/ky.js',
  'js/content/ru.js',
  'js/ui/app.js',
  'js/ui/charts.js',
  'js/ui/components.js',
  'js/ui/screens/coach.js',
  'js/ui/screens/help.js',
  'js/ui/screens/home.js',
  'js/ui/screens/journal.js',
  'js/ui/screens/onboarding.js',
  'js/ui/screens/premium.js',
  'js/ui/screens/protect.js',
  'js/ui/screens/settings.js',
  'js/ui/screens/sos.js',
  'js/ui/screens/truth.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(VERSION).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== VERSION).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;

  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).catch(() => caches.match('index.html')));
    return;
  }

  // Сначала кэш, параллельно обновляем его из сети.
  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(VERSION).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => cached);
      return cached || network;
    }),
  );
});
