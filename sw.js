// Généré par build.py : ne pas modifier à la main.
const VERSION = "cockpit-6ca58bf24378";
const FICHIERS = [
 "./",
 "assets/css/cockpit.css",
 "assets/js/cockpit.js",
 "assets/fonts/B612-Regular.woff2",
 "assets/fonts/B612-Bold.woff2",
 "assets/fonts/B612Mono-Regular.woff2",
 "assets/fonts/B612Mono-Bold.woff2",
 "assets/img/favicon.svg",
 "assets/img/icon-192.png",
 "assets/img/icon-512.png",
 "manifest.webmanifest"
];

self.addEventListener("install", (evt) => {
  evt.waitUntil(caches.open(VERSION).then((c) => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (evt) => {
  evt.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (evt) => {
  const req = evt.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  if (req.mode === "navigate") {
    evt.respondWith(
      fetch(req)
        .then((rep) => { const copie = rep.clone(); caches.open(VERSION).then((c) => c.put("./", copie)); return rep; })
        .catch(() => caches.match("./"))
    );
    return;
  }
  evt.respondWith(caches.match(req).then((trouve) => trouve || fetch(req)));
});
