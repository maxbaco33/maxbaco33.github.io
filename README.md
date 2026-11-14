# maxbaco33.github.io

CV interactif de Maxence Baconnet, technicien avionique Rafale.
Site en ligne : https://maxbaco33.github.io/

Le site reprend l'interface d'un afficheur multifonction de cockpit : touches latérales pour changer de page, bandeau d'état avec autotest et horloge, bloc-notes de commandes en bas d'écran, et code couleur avionique (cyan pour les données, magenta pour l'élément actif, vert pour ce qui est validé, ambre pour ce qui est en cours).

## Architecture

```
data/cv.json          Contenu du CV (seul fichier à modifier pour mettre le site à jour)
build.py              Générateur statique : cv.json vers index.html, 404.html, sw.js, sitemap.xml, robots.txt
assets/css/cockpit.css  Styles écran, mobile et impression (le CV s'imprime en version papier propre)
assets/js/cockpit.js    Navigation par pages, touches, commandes, autotest, horloge
assets/fonts/         Police B612, conçue pour les écrans de cockpit Airbus (licence OFL, hébergée localement)
assets/img/           Icônes et image de partage
manifest.webmanifest  Installation comme application (PWA)
sw.js                 Service worker généré : le site reste consultable hors ligne
```

Principes :

- **Contenu séparé de la présentation** : tout le texte vit dans `data/cv.json`.
- **HTML complet dès le chargement** : le contenu est généré à l'avance, il reste lisible sans JavaScript et par les moteurs de recherche (données structurées schema.org incluses).
- **Aucune dépendance externe** : pas de framework, pas de police chargée chez un tiers, aucun traceur.
- **Accessibilité** : navigation au clavier (touches 1 à 6, « / » pour saisir une commande), respect du réglage « réduire les animations ».

## Mettre à jour le site

1. Modifier `data/cv.json`.
2. Lancer `python3 build.py`.
3. Valider et pousser les changements : GitHub Pages republie le site automatiquement.

`python3 build.py --check` indique si les fichiers générés sont à jour.

## Confidentialité

Les projets présentés sont menés sur temps libre, uniquement à partir de matériel, de données et de documents publics.

## Licences

Police B612 : SIL Open Font License 1.1 (voir `assets/fonts/OFL.txt`). Contenu du CV : tous droits réservés.
