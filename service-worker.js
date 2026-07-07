// Dispatch service worker.
// IMPORTANT: app code (HTML) is network-first so updates ALWAYS load.
// Only static icons are cached. Feed/proxy requests are never cached.
const CACHE = 'dispatch-v3';
const STATIC = ['./manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);

  // Never touch cross-origin requests or the local feed proxy.
  if (url.origin !== location.origin) return;
  if (url.pathname === '/proxy' || url.pathname.startsWith('/proxy')) return;

  const isAppCode =
    req.mode === 'navigate' ||
    url.pathname.endsWith('/') ||
    url.pathname.endsWith('index.html');

  if (isAppCode) {
    // Network-first: always try to load the latest app, fall back to cache offline.
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put('./index.html', copy));
          return res;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  // Static assets: cache-first.
  e.respondWith(caches.match(req).then((hit) => hit || fetch(req)));
});
