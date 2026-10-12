# Ponyta & Goupix

Suivi de collection des cartes Pokémon Ponyta, Galopa, Goupix et Feunard (formes de Galar et d'Alola comprises), en français, japonais et chinois simplifié, plus les cartes où Ponyta apparaît en caméo. Plus de 700 cartes, toutes variantes sauf jumbo.

**App : https://guillaumecazelles.github.io/ponyta-galopa/**

- Toucher une carte l'ajoute à la collection ; la toucher encore la retire. Maintenir appuyé l'agrandit.
- Sous chaque carte : le sigle de l'extension et le numéro (ex. `DRI 029/182`). Sigle plein : imprimé en bas à gauche de la carte. Sigle en pointillés : sigle officiel, mais la carte n'a qu'un symbole (cartes d'avant Écarlate et Violet).
- Filtres par langue (double-toucher une langue pour n'afficher qu'elle), par Pokémon, formes régionales, caméos, cartes manquantes.
- Onglet Prix : prix moyen Cardmarket sur 30 jours des cartes françaises.
- La collection est enregistrée dans le navigateur de chaque appareil ; sauvegarde et restauration depuis le menu ☰.
- Sur iPhone : Safari → Partager → « Sur l'écran d'accueil ».

## Mettre à jour les données

Tout est dans `build/`. L'app est un seul fichier, `index.html`, généré par :

```bash
cd build
python asian.py   # normalise les listes japonaise et chinoise
python build.py   # télécharge le guide des prix Cardmarket et régénère ../index.html
```

`build.py --offline` réutilise le guide des prix déjà téléchargé.

| Fichier | Contenu |
|---|---|
| `build/template.html` | l'app (HTML, CSS, JS) |
| `build/src/tcgdex_raw.json` | cartes de l'API TCGdex (les cartes anglaises servent seulement de squelette : regroupement, images, prix) |
| `build/src/sets.json` | extensions TCGdex : noms, dates, sigles |
| `build/src/extra_enfr.json` | corrections françaises (cartes jamais sorties en français, promos, decks, tampons, variantes manquantes) |
| `build/src/ja_*_raw.json`, `zh_*_raw.json` | listes japonaise et chinoise (Ponyta/Galopa et Goupix/Feunard) |
| `build/src/*_printed_codes.json` | sigles imprimés sur les cartes japonaises et chinoises |
| `build/src/cameos_raw.json` | cartes avec Ponyta en caméo (`cameos_import.py` → `cameos.json`) |
| `build/src/icon.png` | icône de l'écran d'accueil |

## Sources

TCGdex, Bulbapedia, Poképédia, base officielle pokemon-card.com, wiki 52poke, pikaqian.com, staiz.io (caméos) ; prix : guide des prix public Cardmarket et API TCGdex. Projet de fan non officiel ; Pokémon et les illustrations des cartes appartiennent à Nintendo, Creatures et GAME FREAK.
