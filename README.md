# Ponyta & Galopa

Suivi de collection du master set Ponyta / Galopa du JCC Pokémon, en français, anglais, japonais et chinois simplifié (400 cartes, toutes variantes sauf jumbo).

**App : https://guillaumecazelles.github.io/ponyta-galopa/**

- Toucher une carte l'ajoute à la collection ; la toucher encore la retire. Maintenir appuyé l'agrandit.
- Filtres par langue (double-toucher une langue pour n'afficher qu'elle), par Pokémon, cartes manquantes.
- Onglet Prix : prix moyen Cardmarket sur 30 jours des cartes françaises.
- La collection est enregistrée dans le navigateur de chaque appareil ; sauvegarde et restauration depuis le menu ☰.
- Sur iPhone : Safari → Partager → « Sur l'écran d'accueil ».

## Mettre à jour les données

Tout est dans `build/`. L'app est un seul fichier, `index.html`, généré par :

```bash
cd build
python asian.py   # normalise les listes japonaise et chinoise (src/ja_cards_raw.json, src/zh_cards_raw.json)
python build.py   # télécharge le guide des prix Cardmarket et régénère ../index.html
```

`build.py --offline` réutilise le guide des prix déjà téléchargé.

| Fichier | Contenu |
|---|---|
| `build/template.html` | l'app (HTML, CSS, JS) |
| `build/src/tcgdex_raw.json` | cartes FR / EN / JP de l'API TCGdex |
| `build/src/extra_enfr.json` | corrections FR / EN (cartes jamais sorties en français, promos, variantes manquantes) |
| `build/src/ja_cards_raw.json`, `zh_cards_raw.json` | listes japonaise et chinoise |
| `build/src/icon.png` | icône de l'écran d'accueil |

## Sources

TCGdex, Bulbapedia, Poképédia, base officielle pokemon-card.com, wiki 52poke, pikaqian.com ; prix : guide des prix public Cardmarket et API TCGdex. Projet de fan non officiel ; Pokémon et les illustrations des cartes appartiennent à Nintendo, Creatures et GAME FREAK.
