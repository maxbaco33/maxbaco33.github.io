# maxbaco33.github.io

Site CV de Maxence Baconnet, technicien avionique Rafale.
En ligne : https://maxbaco33.github.io/

## Organisation

```
data/cv.json            Contenu du CV : seul fichier à modifier pour mettre le site à jour
build.py                Générateur statique : produit index.html, 404.html, sitemap.xml, robots.txt
outils/generer_pdf.py   Produit le CV PDF téléchargeable à partir de la version imprimable
assets/css/site.css     Mise en page écran, mobile, thème sombre et impression
assets/js/site.js       Sommaire latéral qui suit la lecture
assets/fonts/           IBM Plex Sans et B612 Mono, hébergées localement (licences OFL)
assets/cv/              CV au format PDF
```

Le site est entièrement statique : aucun framework, aucune police chargée chez un tiers, aucun traceur.
Le contenu est présent dans le HTML dès le chargement, avec des données structurées schema.org.

## Mettre à jour

1. Modifier `data/cv.json`.
2. `python3 build.py`
3. `python3 outils/generer_pdf.py` pour régénérer le PDF.
4. Valider et pousser : GitHub Pages republie le site automatiquement.

## Licences

Polices IBM Plex Sans et B612 Mono : SIL Open Font License 1.1 (voir `assets/fonts/`).
Contenu du CV : tous droits réservés.
