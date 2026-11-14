/* Met en évidence la section en cours dans le sommaire latéral. */
(function () {
  "use strict";

  var liens = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if ("IntersectionObserver" in window && liens.length) {
    var parId = {};
    liens.forEach(function (a) { parId[a.getAttribute("href").slice(1)] = a; });
    var visibles = {};
    var observateur = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (en) { visibles[en.target.id] = en.isIntersecting; });
      var actif = null;
      liens.some(function (a) {
        var id = a.getAttribute("href").slice(1);
        if (visibles[id]) { actif = id; return true; }
        return false;
      });
      if (!actif) return;
      liens.forEach(function (a) {
        if (a === parId[actif]) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
    }, { rootMargin: "-20% 0px -60% 0px" });
    Object.keys(parId).forEach(function (id) {
      var sec = document.getElementById(id);
      if (sec) observateur.observe(sec);
    });
  }

  /* Nettoie le service worker installé par l'ancienne version du site. */
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(function (regs) {
      regs.forEach(function (r) { r.unregister(); });
    }).catch(function () {});
  }
})();
