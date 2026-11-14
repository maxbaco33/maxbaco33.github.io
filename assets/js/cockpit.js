/* Logique de l'afficheur : navigation par pages, touches, bloc-notes de commandes, autotest, horloge. */
(function () {
  "use strict";

  var PAGES = ["synop", "parcours", "qualifs", "systemes", "projets", "contact"];
  var LINKEDIN = "https://www.linkedin.com/in/maxence-baconnet-1a10a3246";
  var reduit = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var stPage = document.getElementById("st-page");
  var stTest = document.getElementById("st-test");
  var horloge = document.getElementById("st-clock");
  var msg = document.getElementById("msg");
  var form = document.getElementById("mcdu");
  var champ = document.getElementById("cmd");
  var main = document.getElementById("main");
  var titreBase = document.title;
  var minuteries = [];

  /* ---------------------------------------------------------- pages */
  function afficher(id, focus) {
    if (PAGES.indexOf(id) === -1) id = "synop";
    var titre = "";
    PAGES.forEach(function (p) {
      var sec = document.getElementById(p);
      var actif = p === id;
      sec.classList.toggle("is-active", actif);
      if (actif) titre = sec.getAttribute("data-titre");
    });
    document.querySelectorAll(".keys-left .key").forEach(function (k) {
      if (k.getAttribute("data-page") === id) k.setAttribute("aria-current", "page");
      else k.removeAttribute("aria-current");
    });
    stPage.textContent = titre;
    document.title = id === "synop" ? titreBase : titre + " | " + titreBase;
    window.scrollTo(0, 0);
    if (focus) main.focus({ preventScroll: true });
  }

  function aller(id) {
    if (location.hash === "#" + id) afficher(id, true);
    else location.hash = id;
  }

  window.addEventListener("hashchange", function () {
    afficher(location.hash.slice(1), true);
  });

  /* ---------------------------------------------------------- messages */
  function annulerSequences() {
    minuteries.forEach(clearTimeout);
    minuteries = [];
  }

  function dire(texte) {
    annulerSequences();
    msg.textContent = texte;
  }

  function sequence(lignes, fin) {
    annulerSequences();
    if (reduit) {
      msg.textContent = lignes.join("\n");
      if (fin) fin();
      return;
    }
    msg.textContent = "";
    lignes.forEach(function (ligne, i) {
      minuteries.push(setTimeout(function () {
        msg.textContent = (msg.textContent ? msg.textContent + "\n" : "") + ligne;
        if (i === lignes.length - 1 && fin) fin();
      }, 320 * (i + 1)));
    });
  }

  /* ---------------------------------------------------------- autotest */
  function autotest() {
    stTest.textContent = "Autotest";
    stTest.classList.add("busy");
    function ligne(nom, etat) { return nom + " " + ".".repeat(28 - nom.length) + " " + etat; }
    sequence([
      "Autotest en cours…",
      ligne("Avionique Rafale", "OK"),
      ligne("Qualifications", "OK"),
      ligne("Électronique et systèmes", "OK"),
      ligne("IA et web", "EN COURS"),
      "Autotest terminé."
    ], function () {
      stTest.textContent = "Sys OK";
      stTest.classList.remove("busy");
    });
  }

  function autotestDemarrage() {
    var deja = false;
    try { deja = sessionStorage.getItem("autotest") === "1"; sessionStorage.setItem("autotest", "1"); } catch (err) { deja = true; }
    if (deja || reduit) return;
    stTest.textContent = "Autotest";
    stTest.classList.add("busy");
    setTimeout(function () {
      stTest.textContent = "Sys OK";
      stTest.classList.remove("busy");
    }, 1400);
  }

  /* ---------------------------------------------------------- commandes */
  var AIDE = [
    "Commandes : synop, parcours, qualifs, systemes, projets, contact",
    "imprimer, linkedin, test, effacer. Touches 1 à 6 : pages. « / » : saisie."
  ];

  var COMMANDES = {
    aide: function () { sequence(AIDE); },
    help: function () { sequence(AIDE); },
    synop: function () { aller("synop"); dire("Page synoptique."); },
    accueil: function () { aller("synop"); dire("Page synoptique."); },
    parcours: function () { aller("parcours"); dire("Plan de vol affiché."); },
    plan: function () { aller("parcours"); dire("Plan de vol affiché."); },
    qualifs: function () { aller("qualifs"); dire("Qualifications affichées."); },
    certifs: function () { aller("qualifs"); dire("Qualifications affichées."); },
    systemes: function () { aller("systemes"); dire("État des systèmes affiché."); },
    competences: function () { aller("systemes"); dire("État des systèmes affiché."); },
    projets: function () { aller("projets"); dire("Projets à venir affichés."); },
    contact: function () { aller("contact"); dire("Page contact."); },
    imprimer: function () { dire("Impression du CV."); window.print(); },
    pdf: function () { dire("Impression du CV : choisissez « Enregistrer en PDF »."); window.print(); },
    linkedin: function () { dire("Ouverture du profil LinkedIn."); window.location.href = LINKEDIN; },
    test: autotest,
    autotest: autotest,
    effacer: function () { dire(""); },
    clr: function () { dire(""); }
  };

  function normaliser(texte) {
    return texte.trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  function executer(brut) {
    var cmd = normaliser(brut);
    if (!cmd) return;
    if (/^[1-6]$/.test(cmd)) { aller(PAGES[Number(cmd) - 1]); dire(""); return; }
    var action = COMMANDES[cmd];
    if (action) action();
    else dire("Commande inconnue : « " + brut.trim() + " ». Tapez « aide ».");
  }

  if (form) {
    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      executer(champ.value);
      champ.value = "";
    });
  }

  document.querySelectorAll("[data-action]").forEach(function (b) {
    b.addEventListener("click", function () {
      var action = b.getAttribute("data-action");
      if (action === "imprimer") COMMANDES.imprimer();
      if (action === "test") autotest();
      if (action === "aide") COMMANDES.aide();
    });
  });

  /* ---------------------------------------------------------- clavier */
  document.addEventListener("keydown", function (evt) {
    var cible = evt.target;
    var saisie = cible && (cible.tagName === "INPUT" || cible.tagName === "TEXTAREA" || cible.isContentEditable);
    if (saisie || evt.ctrlKey || evt.metaKey || evt.altKey) return;
    if (/^[1-6]$/.test(evt.key)) { evt.preventDefault(); aller(PAGES[Number(evt.key) - 1]); }
    else if (evt.key === "/") { evt.preventDefault(); champ.focus(); }
  });

  /* ---------------------------------------------------------- horloge */
  function tic() {
    var d = new Date();
    horloge.textContent = [d.getHours(), d.getMinutes(), d.getSeconds()]
      .map(function (n) { return String(n).padStart(2, "0"); }).join(":");
    horloge.setAttribute("datetime", d.toISOString());
  }

  /* ---------------------------------------------------------- démarrage */
  afficher(location.hash.slice(1), false);
  tic();
  setInterval(tic, 1000);
  autotestDemarrage();

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").catch(function () {});
    });
  }
})();
