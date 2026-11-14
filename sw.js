// Généré par build.py. Désinstalle le service worker de l'ancienne version du site.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (evt) => {
  evt.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.map((k) => caches.delete(k))))
      .then(() => self.registration.unregister())
  );
});
