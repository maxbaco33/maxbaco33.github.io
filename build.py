#!/usr/bin/env python3
"""Générateur statique du site.

Lit data/cv.json et produit index.html, 404.html, sw.js, sitemap.xml et robots.txt.
Usage : python3 build.py            (régénère le site)
        python3 build.py --check    (échoue si les fichiers générés ne sont pas à jour)
"""
import hashlib
import html
import json
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent
DONNEES = json.loads((RACINE / "data" / "cv.json").read_text(encoding="utf-8"))

PAGES = [
    ("synop", "Synop", "Synoptique"),
    ("parcours", "Parcours", "Plan de vol"),
    ("qualifs", "Qualifs", "Qualifications"),
    ("systemes", "Systèmes", "État des systèmes"),
    ("projets", "Projets", "Projets à venir"),
    ("contact", "Contact", "Contact"),
]

ASSETS = [
    "assets/css/cockpit.css",
    "assets/js/cockpit.js",
    "assets/fonts/B612-Regular.woff2",
    "assets/fonts/B612-Bold.woff2",
    "assets/fonts/B612Mono-Regular.woff2",
    "assets/fonts/B612Mono-Bold.woff2",
    "assets/img/favicon.svg",
    "assets/img/icon-192.png",
    "assets/img/icon-512.png",
    "manifest.webmanifest",
]


def e(texte):
    return html.escape(str(texte), quote=True)


# ---------------------------------------------------------------- synoptique

ETATS = {"ok": "OK", "encours": "En cours"}


def noeud(n, x, y, l, h):
    etat = n["etat"]
    return (
        f'<a class="syn-node" href="#{e(n["page"])}" data-page="{e(n["page"])}">'
        f'<rect class="syn-box" x="{x}" y="{y}" width="{l}" height="{h}" rx="6"/>'
        f'<circle class="syn-led {etat}" cx="{x + 20}" cy="{y + 25}" r="6"/>'
        f'<text class="syn-title" x="{x + 36}" y="{y + 30}">{e(n["titre"])}</text>'
        f'<text class="syn-detail" x="{x + 20}" y="{y + 56}">{e(n["detail"])}</text>'
        f'<text class="syn-state {etat}" x="{x + 20}" y="{y + 79}">{e(ETATS[etat])}</text>'
        f'<text class="syn-go" x="{x + l - 22}" y="{y + 79}" text-anchor="middle">›</text>'
        "</a>"
    )


def centre(x, y, l, h, cx):
    ident = DONNEES["identite"]
    return (
        f'<g class="syn-center"><rect class="syn-box" x="{x}" y="{y}" width="{l}" height="{h}" rx="6"/>'
        f'<text class="syn-title" x="{cx}" y="{y + 34}" text-anchor="middle">{e(ident["prenom"])} {e(ident["nom"])}</text>'
        f'<text class="syn-detail" x="{cx}" y="{y + 58}" text-anchor="middle">Technicien avionique</text></g>'
    )


def synoptique():
    noeuds = DONNEES["synoptique"]
    # Disposition large : unité centrale au milieu, sous-systèmes aux quatre coins.
    large = ['<svg class="syn syn-wide" viewBox="0 0 760 400" role="group" aria-label="Synoptique du profil">']
    liaisons = [
        "M250,68 H300 V160", "M510,68 H460 V160",
        "M250,332 H300 V240", "M510,332 H460 V240",
    ]
    for d in liaisons:
        large.append(f'<path class="flow" d="{d}"/>')
    large.append(centre(270, 160, 220, 80, 380))
    for n, (x, y) in zip(noeuds, [(20, 20), (510, 20), (20, 284), (510, 284)]):
        large.append(noeud(n, x, y, 230, 96))
    large.append("</svg>")

    # Disposition haute pour mobile : bus vertical à gauche.
    haut = ['<svg class="syn syn-tall" viewBox="0 0 360 572" role="group" aria-label="Synoptique du profil">']
    ys = [126, 236, 346, 456]
    haut.append(f'<path class="flow" d="M64,54 H22 V{ys[-1] + 48}"/>')
    for y in ys:
        haut.append(f'<path class="flow" d="M22,{y + 48} H44"/>')
    haut.append(centre(64, 14, 252, 80, 190))
    for n, y in zip(noeuds, ys):
        haut.append(noeud(n, 44, y, 300, 96))
    haut.append("</svg>")
    return "".join(large) + "".join(haut)


# ---------------------------------------------------------------- sections

def losange(classe):
    return (
        f'<svg class="wpt-sym {classe}" viewBox="0 0 16 16" aria-hidden="true">'
        '<path d="M8 1 L15 8 L8 15 L1 8 Z"/></svg>'
    )


def section_synop():
    ident = DONNEES["identite"]
    paras = "".join(f"<p>{e(p)}</p>" for p in DONNEES["a_propos"])
    return f"""
<section id="synop" class="page" data-titre="Synoptique" aria-labelledby="h-synop">
  <h2 id="h-synop" class="sr-only">Synoptique</h2>
  <div class="ident">
    <h1>{e(ident["prenom"])} {e(ident["nom"])}</h1>
    <p class="ident-title">{e(ident["titre"])}</p>
    <p class="ident-tag">{e(ident["accroche"])}</p>
    <p class="ident-meta">{e(ident["statut"])}<span class="sep" aria-hidden="true">/</span>{e(ident["localisation"])}</p>
  </div>
  <div class="synoptic">{synoptique()}</div>
  <div class="about">{paras}</div>
</section>"""


def section_parcours():
    legs = []
    for leg in DONNEES["plan_de_vol"]:
        classe = "actif" if leg.get("actif") else ("dest" if leg.get("destination") else "")
        org = e(leg["organisme"]) + (f", {e(leg['lieu'])}" if leg.get("lieu") else "")
        points = "".join(f"<li>{e(p)}</li>" for p in leg["points"])
        etiquette = ""
        if leg.get("actif"):
            etiquette = '<span class="chip actif">Branche active</span>'
        elif leg.get("destination"):
            etiquette = '<span class="chip encours">Destination</span>'
        legs.append(f"""
    <li class="leg {classe}">
      <div class="leg-wpt">{losange(classe)}<span class="leg-code">{e(leg["code"])}</span><span class="leg-dates">{e(leg["dates"])}</span></div>
      <div class="leg-body">
        <h3>{e(leg["intitule"])} {etiquette}</h3>
        <p class="leg-org">{org}</p>
        {f'<ul>{points}</ul>' if points else ''}
      </div>
    </li>""")
    return f"""
<section id="parcours" class="page" data-titre="Plan de vol" aria-labelledby="h-parcours">
  <h2 id="h-parcours">Plan de vol</h2>
  <p class="lede">Mon parcours lu comme un plan de vol, du point de départ à la prochaine étape. La branche active est en magenta, comme sur un calculateur de vol.</p>
  <ol class="fpln">{"".join(legs)}
  </ol>
</section>"""


def section_qualifs():
    q = DONNEES["qualifications"]

    def ligne(item, extra=""):
        precision = f'<span class="row-sub">{e(item["precision"])}</span>' if item.get("precision") else ""
        return f"""
      <li class="row">
        <div><span class="row-title">{e(item["intitule"])}</span>{precision}<span class="row-org">{e(item["organisme"])}{extra}</span></div>
        <span class="chip ok">Validé</span>
      </li>"""

    licences = "".join(ligne(i) for i in q["licences"])
    diplomes = "".join(ligne(i, f", {e(i['annee'])}") for i in q["diplomes"])
    return f"""
<section id="qualifs" class="page" data-titre="Qualifications" aria-labelledby="h-qualifs">
  <h2 id="h-qualifs">Qualifications</h2>
  <h3 class="group">Licences et habilitations</h3>
  <ul class="rows">{licences}
  </ul>
  <h3 class="group">Diplômes</h3>
  <ul class="rows">{diplomes}
  </ul>
</section>"""


def section_systemes():
    groupes = []
    for g in DONNEES["competences"]:
        lignes = "".join(
            f'<li class="row"><span class="row-title">{e(nom)}</span>'
            f'<span class="chip {etat}">{"Acquis" if etat == "ok" else "En cours"}</span></li>'
            for nom, etat in g["items"]
        )
        groupes.append(f'<div class="sys-group"><h3 class="group">{e(g["groupe"])}</h3><ul class="rows">{lignes}</ul></div>')
    return f"""
<section id="systemes" class="page" data-titre="État des systèmes" aria-labelledby="h-systemes">
  <h2 id="h-systemes">État des systèmes</h2>
  <p class="lede">Mes compétences, présentées comme une page d'état des systèmes : en vert ce qui est acquis, en ambre ce qui est en cours d'acquisition.</p>
  <div class="sys-grid">{"".join(groupes)}</div>
</section>"""


def section_projets():
    cartes = []
    for p in DONNEES["projets"]:
        briques = "".join(f'<li class="chip data">{e(b)}</li>' for b in p["briques"])
        cartes.append(f"""
    <article class="card" id="projet-{e(p["id"])}">
      <header class="card-head"><h3>{e(p["titre"])}</h3><span class="chip encours">Bientôt</span></header>
      <p>{e(p["resume"])}</p>
      <p class="card-demo"><span>Ce que ça démontrera</span>{e(p["demontre"])}</p>
      <ul class="chips" aria-label="Briques techniques">{briques}</ul>
    </article>""")
    return f"""
<section id="projets" class="page" data-titre="Projets à venir" aria-labelledby="h-projets">
  <h2 id="h-projets">Projets à venir</h2>
  <p class="lede">{e(DONNEES["note_projets"])}</p>
  <div class="cards">{"".join(cartes)}
  </div>
</section>"""


def section_contact():
    ident = DONNEES["identite"]
    dest = next(l for l in DONNEES["plan_de_vol"] if l.get("destination"))
    return f"""
<section id="contact" class="page" data-titre="Contact" aria-labelledby="h-contact">
  <h2 id="h-contact">Contact</h2>
  <p class="lede">{e(dest["points"][0])} Mobilité en {e(dest["lieu"])}.</p>
  <div class="actions">
    <a class="btn btn-primary" href="{e(ident["linkedin"])}" rel="noopener">Me contacter sur LinkedIn</a>
    <button class="btn js-only" type="button" data-action="imprimer">Imprimer le CV</button>
  </div>
  <h3 class="group">Code couleur de cet écran</h3>
  <dl class="legend">
    <div><dt><span class="sw cyan"></span>Cyan</dt><dd>Données et éléments sélectionnables</dd></div>
    <div><dt><span class="sw magenta"></span>Magenta</dt><dd>Élément actif</dd></div>
    <div><dt><span class="sw green"></span>Vert</dt><dd>Validé, acquis</dd></div>
    <div><dt><span class="sw amber"></span>Ambre</dt><dd>En cours, à venir</dd></div>
  </dl>
  <p class="note">Les mêmes conventions que sur les écrans de cockpit. Raccourcis : touches 1 à 6 pour changer de page, « / » pour saisir une commande.</p>
</section>"""


# ---------------------------------------------------------------- page

def json_ld():
    ident = DONNEES["identite"]
    q = DONNEES["qualifications"]
    donnees = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": f'{ident["prenom"]} {ident["nom"]}',
        "jobTitle": ident["titre"],
        "description": DONNEES["site"]["description"],
        "url": DONNEES["site"]["url"],
        "sameAs": [ident["linkedin"]],
        "address": {"@type": "PostalAddress", "addressRegion": "Nouvelle-Aquitaine", "addressCountry": "FR"},
        "alumniOf": [{"@type": "EducationalOrganization", "name": d["organisme"]} for d in q["diplomes"]],
        "knowsAbout": [nom for g in DONNEES["competences"] for nom, _ in g["items"]],
    }
    return json.dumps(donnees, ensure_ascii=False, indent=1)


def touches():
    gauche = "".join(
        f'<a class="key" href="#{pid}" data-page="{pid}"><span class="key-n">{i}</span><span class="key-l">{e(court)}</span></a>'
        for i, (pid, court, _) in enumerate(PAGES, 1)
    )
    ident = DONNEES["identite"]
    droite = (
        '<button class="key js-only" type="button" data-action="imprimer"><span class="key-l">Imprimer</span></button>'
        f'<a class="key" href="{e(ident["linkedin"])}" rel="noopener"><span class="key-l">LinkedIn</span></a>'
        '<button class="key js-only" type="button" data-action="test"><span class="key-l">Autotest</span></button>'
        '<button class="key js-only" type="button" data-action="aide"><span class="key-l">Aide</span></button>'
    )
    return gauche, droite


def page_index():
    site = DONNEES["site"]
    ident = DONNEES["identite"]
    gauche, droite = touches()
    sections = "".join([
        section_synop(), section_parcours(), section_qualifs(),
        section_systemes(), section_projets(), section_contact(),
    ])
    nom = f'{ident["prenom"]} {ident["nom"]}'
    return f"""<!DOCTYPE html>
<html lang="{site["langue"]}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(site["titre"])}</title>
<meta name="description" content="{e(site["description"])}">
<link rel="canonical" href="{e(site["url"])}">
<meta name="theme-color" content="#0c1116">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(site["titre"])}">
<meta property="og:description" content="{e(site["description"])}">
<meta property="og:url" content="{e(site["url"])}">
<meta property="og:image" content="{e(site["url"])}assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/icon-192.png">
<link rel="preload" href="assets/fonts/B612-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/B612Mono-Bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/cockpit.css">
<script>document.documentElement.className = "js";</script>
<script type="application/ld+json">
{json_ld()}
</script>
</head>
<body>
<a class="skip" href="#main">Aller au contenu</a>
<div class="print-head">
  <p class="ph-name">{e(nom)}</p>
  <p class="ph-title">{e(ident["titre"])}. {e(ident["accroche"])}.</p>
  <p class="ph-links">{e(ident["localisation"])} / {e(ident["linkedin"])} / {e(site["url"])}</p>
</div>
<div class="unit">
  <nav class="keys keys-left" aria-label="Pages">{gauche}</nav>
  <div class="screen">
    <header class="status">
      <span class="st-id">{e(ident["prenom"][0])}. {e(ident["nom"])}</span>
      <span class="st-page" id="st-page">Synoptique</span>
      <span class="st-right"><span class="st-test" id="st-test">Sys OK</span><time class="st-clock" id="st-clock"></time></span>
    </header>
    <main id="main" tabindex="-1">{sections}
    </main>
    <footer class="scratch js-only">
      <p class="scratch-msg" id="msg" role="status" aria-live="polite">Tapez « aide » pour la liste des commandes.</p>
      <form class="scratch-form" id="mcdu" autocomplete="off">
        <label for="cmd" class="sr-only">Commande</label>
        <span class="prompt" aria-hidden="true">›</span>
        <input id="cmd" name="cmd" type="text" placeholder="aide" spellcheck="false" autocapitalize="off" enterkeyhint="go">
        <button class="mini" type="submit">Exécuter</button>
      </form>
    </footer>
  </div>
  <nav class="keys keys-right" aria-label="Actions">{droite}</nav>
</div>
<footer class="credits">
  <p>Conçu avec l'IA comme copilote, en HTML, CSS et JavaScript sans framework. Police B612, dessinée pour les écrans de cockpit Airbus (licence OFL). Consultable hors ligne. Mise à jour : {e(site["mise_a_jour"])}.</p>
</footer>
<script src="assets/js/cockpit.js" defer></script>
</body>
</html>
"""


def page_404():
    return """<!DOCTYPE html>
<html lang="fr" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/cockpit.css">
</head>
<body class="solo">
<main class="screen solo-screen">
  <p class="solo-code">Erreur 404</p>
  <h1>Page introuvable</h1>
  <p class="lede">Cette adresse ne correspond à aucune page du site.</p>
  <p><a class="btn btn-primary" href="/">Retour au synoptique</a></p>
</main>
</body>
</html>
"""


def service_worker():
    empreinte = hashlib.sha256()
    for chemin in ASSETS + ["data/cv.json"]:
        empreinte.update((RACINE / chemin).read_bytes())
    version = empreinte.hexdigest()[:12]
    liste = json.dumps(["./"] + ASSETS, indent=1)
    return f"""// Généré par build.py : ne pas modifier à la main.
const VERSION = "cockpit-{version}";
const FICHIERS = {liste};

self.addEventListener("install", (evt) => {{
  evt.waitUntil(caches.open(VERSION).then((c) => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
}});

self.addEventListener("activate", (evt) => {{
  evt.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (evt) => {{
  const req = evt.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  if (req.mode === "navigate") {{
    evt.respondWith(
      fetch(req)
        .then((rep) => {{ const copie = rep.clone(); caches.open(VERSION).then((c) => c.put("./", copie)); return rep; }})
        .catch(() => caches.match("./"))
    );
    return;
  }}
  evt.respondWith(caches.match(req).then((trouve) => trouve || fetch(req)));
}});
"""


def sitemap():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{DONNEES["site"]["url"]}</loc><lastmod>{date.today().isoformat()}</lastmod></url>
</urlset>
"""


def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {DONNEES['site']['url']}sitemap.xml\n"


SORTIES = {
    "index.html": page_index,
    "404.html": page_404,
    "sw.js": service_worker,
    "robots.txt": robots,
}


def main():
    verifier = "--check" in sys.argv
    perimes = []
    for nom, fabrique in SORTIES.items():
        contenu = fabrique()
        cible = RACINE / nom
        if verifier:
            if not cible.exists() or cible.read_text(encoding="utf-8") != contenu:
                perimes.append(nom)
        else:
            cible.write_text(contenu, encoding="utf-8")
    if not verifier:
        (RACINE / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
        print("Site généré :", ", ".join(list(SORTIES) + ["sitemap.xml"]))
    elif perimes:
        print("Fichiers à régénérer :", ", ".join(perimes))
        sys.exit(1)
    else:
        print("Site à jour.")


if __name__ == "__main__":
    main()
