#!/usr/bin/env python3
"""Générateur statique du site.

Lit data/cv.json et produit index.html, 404.html, sw.js, sitemap.xml et robots.txt.
Usage : python3 build.py            (régénère le site)
        python3 build.py --check    (échoue si les fichiers générés ne sont pas à jour)
"""
import html
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
D = json.loads((RACINE / "data" / "cv.json").read_text(encoding="utf-8"))

SECTIONS = [
    ("profil", "Profil"),
    ("experience", "Expérience"),
    ("competences", "Compétences"),
    ("qualifications", "Qualifications"),
    ("projets", "Projet personnel"),
    ("contact", "Contact"),
]


def court(url):
    """Adresse lisible pour le papier : sans protocole, sans www, sans barre finale."""
    return url.replace("https://", "").replace("www.", "").rstrip("/")


def e(texte):
    return html.escape(str(texte), quote=True)


ICONE_LIEU = (
    '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 15s5-4.6 5-8.5A5 5 0 0 0 3 6.5C3 10.4 8 15 8 15Z" '
    'fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="8" cy="6.5" r="1.8" fill="currentColor"/></svg>'
)
ICONE_LINKEDIN = (
    '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M1.5 5.5h2.8V14H1.5zM2.9 1.5a1.6 1.6 0 1 1 0 3.2 1.6 1.6 0 0 1 0-3.2ZM6 5.5h2.7v1.2c.4-.7 1.3-1.4 2.7-1.4 2.9 0 3.4 1.9 3.4 4.3V14h-2.8v-4c0-1 0-2.2-1.4-2.2s-1.6 1-1.6 2.1V14H6z"/></svg>'
)
ICONE_PDF = (
    '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v8m0 0 3.2-3.2M8 10 4.8 6.8M2.5 12.5v1h11v-1" '
    'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def boutons(classe="", linkedin=True):
    ident = D["identite"]
    lien = (f'<a class="btn btn-primary" href="{e(ident["linkedin"])}" rel="noopener">{ICONE_LINKEDIN}Me contacter sur LinkedIn</a>'
            if linkedin else "")
    pdf_classe = "btn" if linkedin else "btn btn-primary"
    return (
        f'<div class="actions {classe}">{lien}'
        f'<a class="{pdf_classe}" href="{e(D["site"]["pdf"])}" download>{ICONE_PDF}Télécharger le CV (PDF)</a>'
        "</div>"
    )


# ---------------------------------------------------------------- sections

def s_profil():
    paras = "".join(f"<p>{e(p)}</p>" for p in D["profil"])
    fiche = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in D.get("en_bref", []))
    bloc_fiche = f'\n  <dl class="datasheet" aria-label="En bref">{fiche}</dl>' if fiche else ""
    return f"""
<section id="profil" class="section" aria-labelledby="t-profil">
  <h2 id="t-profil">Profil</h2>
  <div class="prose">{paras}</div>{bloc_fiche}
  <div class="objectif"><p class="objectif-titre">Objectif professionnel</p><p>{e(D["objectif"])}</p></div>
</section>"""


def s_experience():
    postes = []
    for x in D["experiences"]:
        badge = '<span class="badge badge-current">Poste actuel</span>' if x.get("actuel") else ""
        lieu = f'<p class="meta-place">{e(x["lieu"])}</p>' if x.get("lieu") else ""
        missions = "".join(f"<li><strong>{e(t)} :</strong> {e(d)}</li>" for t, d in x["missions"])
        postes.append(f"""
  <article class="entry{' is-current' if x.get('actuel') else ''}">
    <div class="entry-meta"><p class="meta-dates">{e(x["dates"])}</p>{lieu}</div>
    <div class="entry-body">
      <h3>{e(x["poste"])}{badge}</h3>
      <p class="entry-org">{e(x["organisme"])}</p>
      <ul class="missions">{missions}</ul>
    </div>
  </article>""")
    return f"""
<section id="experience" class="section" aria-labelledby="t-experience">
  <h2 id="t-experience">Expérience</h2>
  <div class="timeline">{"".join(postes)}
  </div>
</section>"""


def s_competences():
    groupes = "".join(
        f'<div class="skill-group"><h3>{e(g["groupe"])}</h3><ul>'
        + "".join(f"<li>{e(i)}</li>" for i in g["items"])
        + "</ul></div>"
        for g in D["competences"]
    )
    langues = "".join(
        f"""
    <li class="lang">
      <p class="lang-name">{e(l["langue"])}</p>
      <p class="lang-level">{e(l["niveau"])}</p>
      <span class="gauge" role="img" aria-label="Niveau {l["note"]} sur 5">"""
        + "".join('<i class="on"></i>' if n < l["note"] else "<i></i>" for n in range(5))
        + "</span>\n    </li>"
        for l in D.get("langues", [])
    )
    bloc_langues = (f'\n  <h3 class="subhead">Langues</h3>\n  <ul class="langs">{langues}\n  </ul>'
                    if langues else "")
    return f"""
<section id="competences" class="section" aria-labelledby="t-competences">
  <h2 id="t-competences">Compétences</h2>
  <div class="skills">{groupes}</div>{bloc_langues}
</section>"""


def s_qualifications():
    certifs = "".join(
        f"""
    <li class="cert">
      <p class="cert-title">{e(c["intitule"])}</p>
      <p class="cert-detail">{e(c["precision"])}</p>
      <p class="cert-org">{e(c["organisme"])}</p>
    </li>"""
        for c in D["certifications"]
    )
    formations = "".join(
        f"""
  <article class="entry">
    <div class="entry-meta"><p class="meta-dates">{e(f["dates"])}</p></div>
    <div class="entry-body">
      <h3>{e(f["diplome"])}</h3>
      {f'<p class="entry-sub">{e(f["option"])}</p>' if f["option"] else ""}
      <p class="entry-org">{e(f["etablissement"])}</p>
    </div>
  </article>"""
        for f in D["formation"]
    )
    return f"""
<section id="qualifications" class="section" aria-labelledby="t-qualifications">
  <h2 id="t-qualifications">Qualifications</h2>
  <h3 class="subhead">Licences et habilitations</h3>
  <ul class="certs">{certifs}
  </ul>
  <h3 class="subhead">Formation</h3>
  <div class="timeline compact">{formations}
  </div>
</section>"""


def s_projets():
    cartes = "".join(
        f"""
    <article class="project">
      <div class="project-head"><h3>{e(p["titre"])}</h3><span class="badge badge-soon">En préparation</span></div>
      <p>{e(p["resume"])}</p>
      <ul class="tags" aria-label="Compétences mobilisées">{"".join(f"<li>{e(c)}</li>" for c in p["competences"])}</ul>
    </article>"""
        for p in D["projets"]
    )
    return f"""
<section id="projets" class="section" aria-labelledby="t-projets">
  <h2 id="t-projets">Projet personnel</h2>
  <p class="lede">{e(D["projets_intro"])}</p>
  <div class="projects{" single" if len(D["projets"]) == 1 else ""}">{cartes}
  </div>
</section>"""


ICONE_TEL = (
    '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M5.2 1.8 3.4 2.3c-.8.2-1.3 1-1.1 1.8 1 4.2 4.3 7.5 8.5 8.5.8.2 1.6-.3 1.8-1.1l.5-1.8-2.9-1.3-1.2 1.2a8 8 0 0 1-3.3-3.3l1.2-1.2z" '
    'fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>'
)


def s_contact():
    ident = D["identite"]
    tel = ""
    if ident.get("telephone"):
        tel = (f'<p class="contact-tel">{ICONE_TEL}<span>Téléphone :</span> '
               f'<a href="tel:{e(ident["telephone_intl"])}">{e(ident["telephone"])}</a></p>')
    return f"""
<section id="contact" class="section" aria-labelledby="t-contact">
  <h2 id="t-contact">Contact</h2>
  <p class="lede">Pour échanger sur une opportunité, le plus simple est de me contacter sur LinkedIn. Basé dans les Landes, mobile dans toute la Nouvelle-Aquitaine.</p>
  {boutons("actions-row")}
  {tel}
</section>"""


# ---------------------------------------------------------------- page

def json_ld():
    ident = D["identite"]
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": f'{ident["prenom"]} {ident["nom"]}',
        "jobTitle": ident["titre"],
        "description": D["site"]["description"],
        "url": D["site"]["url"],
        "sameAs": [ident["linkedin"]],
        "image": D["site"]["url"] + ident["photo"],
        "address": {"@type": "PostalAddress", "addressRegion": "Nouvelle-Aquitaine", "addressCountry": "FR"},
        "alumniOf": [{"@type": "EducationalOrganization", "name": f["etablissement"]} for f in D["formation"]],
        "hasCredential": [{"@type": "EducationalOccupationalCredential", "name": c["intitule"]} for c in D["certifications"]],
        "knowsAbout": [i for g in D["competences"] for i in g["items"]],
        "knowsLanguage": [l["code"] for l in D.get("langues", [])],
    }, ensure_ascii=False, indent=1)


def page_index():
    site, ident = D["site"], D["identite"]
    nom = f'{ident["prenom"]} {ident["nom"]}'
    toc = "".join(f'<a href="#{sid}">{e(label)}</a>' for sid, label in SECTIONS)
    contenu = "".join([s_profil(), s_experience(), s_competences(), s_qualifications(), s_projets(), s_contact()])
    return f"""<!DOCTYPE html>
<html lang="{site["langue"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(site["titre"])}</title>
<meta name="description" content="{e(site["description"])}">
<meta name="author" content="{e(nom)}">
<link rel="canonical" href="{e(site["url"])}">
<meta name="theme-color" content="#0f2b46">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(site["titre"])}">
<meta property="og:description" content="{e(site["description"])}">
<meta property="og:url" content="{e(site["url"])}">
<meta property="og:image" content="{e(site["url"])}assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/icon-192.png">
<link rel="preload" href="assets/fonts/IBMPlexSans-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/IBMPlexSans-SemiBold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
<script type="application/ld+json">
{json_ld()}
</script>
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<div class="shell">
  <header class="side">
    <div class="side-inner">
      <div class="cover">
        <img class="cover-img" src="{e(ident["banniere"])}" alt="{e(ident["banniere_alt"])}" width="964" height="396">
        <img class="avatar" src="{e(ident["photo"])}" alt="Photo de {e(nom)}" width="480" height="480">
      </div>
      <div class="identity">
        <h1>{e(nom)}</h1>
        <p class="role">{e(ident["titre"])}</p>
        <p class="tagline">{e(ident["accroche"])}</p>
        <p class="place">{ICONE_LIEU}{e(ident["localisation"])}</p>
        <p class="print-only print-links"><span class="print-tel">{e(ident.get("telephone", ""))}</span><br>{e(court(ident["linkedin"]))}<br>{e(court(site["url"]))}</p>
      </div>
      {boutons("actions-side", linkedin=False)}
      <nav class="toc" aria-label="Sections">{toc}</nav>
    </div>
  </header>
  <main id="contenu" class="content">{contenu}
    <footer class="foot">
      <p>© {e(site["annee"])} {e(nom)}. Dernière mise à jour : {e(site["mise_a_jour"])}.</p>
    </footer>
  </main>
</div>
<script src="assets/js/site.js" defer></script>
</body>
</html>
"""


def page_404():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body class="solo">
<main class="solo-box">
  <p class="eyebrow">Erreur 404</p>
  <h1>Page introuvable</h1>
  <p class="lede">Cette adresse ne correspond à aucune page du site.</p>
  <p><a class="btn btn-primary" href="/">Retour à l'accueil</a></p>
</main>
</body>
</html>
"""


def service_worker():
    # L'ancienne version du site installait un service worker : celui-ci le désinstalle proprement.
    return """// Généré par build.py. Désinstalle le service worker de l'ancienne version du site.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (evt) => {
  evt.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.map((k) => caches.delete(k))))
      .then(() => self.registration.unregister())
  );
});
"""


def sitemap():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{D["site"]["url"]}</loc></url>
</urlset>
"""


def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {D['site']['url']}sitemap.xml\n"


SORTIES = {
    "index.html": page_index,
    "404.html": page_404,
    "sw.js": service_worker,
    "sitemap.xml": sitemap,
    "robots.txt": robots,
}


def main():
    verifier = "--check" in sys.argv
    perimes = []
    for nom, fabrique in SORTIES.items():
        contenu, cible = fabrique(), RACINE / nom
        if verifier:
            if not cible.exists() or cible.read_text(encoding="utf-8") != contenu:
                perimes.append(nom)
        else:
            cible.write_text(contenu, encoding="utf-8")
    if verifier and perimes:
        print("Fichiers à régénérer :", ", ".join(perimes))
        sys.exit(1)
    print("Site à jour." if verifier else "Site généré : " + ", ".join(SORTIES))


if __name__ == "__main__":
    main()
