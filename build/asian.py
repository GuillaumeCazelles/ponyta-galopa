"""Normalises the Japanese / simplified Chinese research lists (src/ja_cards_raw.json, src/zh_cards_raw.json)
into src/ja.json and src/zh.json, the format build.py reads. Run before build.py."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
sys.path.insert(0, HERE)

NAME_FR = {
    "ponyta": "Ponyta", "rapidash": "Galopa", "galar-ponyta": "Ponyta de Galar", "galar-rapidash": "Galopa de Galar",
    "galar-rapidash-v": "Galopa de Galar V", "blaines-ponyta": "Ponyta d'Auguste", "blaines-rapidash": "Galopa d'Auguste",
    "rapidash-4": "Galopa 4", "dark-rapidash": "Galopa obscur", "karens-rapidash": "Galopa de Marion",
    "vulpix": "Goupix", "ninetales": "Feunard", "alola-vulpix": "Goupix d'Alola", "alola-ninetales": "Feunard d'Alola",
    "ninetales-ex": "Feunard-ex", "ninetales-v": "Feunard V", "ninetales-gx": "Feunard-GX", "ninetales-break": "Feunard TURBO",
    "alola-ninetales-gx": "Feunard d'Alola-GX", "alola-vulpix-v": "Goupix d'Alola V", "alola-vulpix-vstar": "Goupix d'Alola VSTAR",
    "blaines-vulpix": "Goupix d'Auguste", "blaines-ninetales": "Feunard d'Auguste", "brocks-vulpix": "Goupix de Pierre",
    "brocks-ninetales": "Feunard de Pierre", "light-ninetales": "Feunard lumineux", "vulpix-delta": "Goupix δ", "ninetales-delta": "Feunard δ",
}
def name_fr(slug):
    if slug in NAME_FR: return NAME_FR[slug]
    base = "Goupix" if "vulpix" in slug else "Feunard" if "ninetales" in slug else "Ponyta" if "ponyta" in slug else "Galopa"
    reg = " d'Alola" if "alola" in slug else " de Galar" if "galar" in slug else ""
    suf = next((" " + t.upper() for t in ("vmax", "vstar", "gx", "ex", "v", "break", "lv-x", "prime") if slug.endswith("-" + t)), "")
    return base + reg + suf.replace("BREAK", "TURBO").replace(" EX", "-ex" if "ex" in slug else " EX")

def species(slug):
    for k in ("ponyta", "rapidash", "vulpix", "ninetales"):
        if k in slug: return k
    return "cameo"

# English set name (as written in equivalent_en) -> TCGdex set id: every set TCGdex knows, plus aliases
_SETS = json.load(open(os.path.join(SRC, "sets.json"), encoding="utf-8"))
EN_SET = [((v.get("en") or {}).get("name"), sid) for sid, v in _SETS.items() if (v.get("en") or {}).get("name")]
EN_SET += [("EX " + n, sid) for n, sid in list(EN_SET) if sid.startswith("ex")]
EN_SET += [("Wizards Black Star Promo", "basep"), ("SWSH Black Star Promo", "swshp"), ("SM Black Star Promo", "smp"),
           ("BW Black Star Promo", "bwp"), ("Hidden Fates", "sma"), ("Shining Fates", "swsh4.5sv"), ("Expedition", "ecard1"),
           ("Platinum Arceus", "pl4"), ("HeartGold & SoulSilver", "hgss1"), ("Pokémon 151", "sv03.5"), ("Scarlet & Violet 151", "sv03.5")]
EN_SET.sort(key=lambda x: -len(x[0]))

def tcgdex_ids():
    raw = json.load(open(os.path.join(SRC, "tcgdex_raw.json"), encoding="utf-8"))
    return {c["id"] for c in raw["en"] if "id" in c}
IDS = tcgdex_ids()

def num_key(s):
    s = s.upper()
    m = re.match(r"(SV|SH|SWSH)?0*(\d+)", s)
    return (m.group(1) or "", int(m.group(2))) if m else None

def group_for(eq):
    """'Silver Tempest 021/195 (…)' -> 'swsh12-021' when that TCGdex card exists."""
    if not eq: return None
    eq = eq.strip()
    if eq.startswith("Pokémon TCG Classic"):
        return None
    for name, sid in EN_SET:
        if eq.startswith(name + " "):
            rest = eq[len(name):].strip()
            m = re.match(r"([A-Z]*\d+)", rest)
            if not m: continue
            want = num_key(m.group(1))
            for cid in IDS:
                if cid.startswith(sid + "-") and num_key(cid[len(sid) + 1:]) == want:
                    return cid
    return None

VARIANT_FR = [
    (r"^Holo - type/energy", "Holo motif énergie"),
    (r"^Holo - Poké Ball", "Holo Poké Ball"),
    (r"star pattern", "Holo étoiles"),
    (r"flower pattern", "Holo fleurs"),
    (r"^Holo - Master Ball", "Holo Master Ball"),
    (r"gold-foil", "Holo logo doré"),
    (r"^Art Rare / illustration", "Illustration rare (art exclusif)"),
    (r"^Holo promo - Poké Ball", "Promo Poké Ball"),
    (r"^Holo promo - Master Ball", "Promo Master Ball"),
    (r"^Holo promo", "Promo holo"),
    (r"^Reverse - Poké Ball", "Reverse Poké Ball"),
    (r"^Reverse - Master Ball", "Reverse Master Ball"),
    (r"^Holo \(shiny rare", "Chromatique (secrète)"),
    (r"^No Rarity Symbol", "Sans symbole de rareté"),
    (r"^Normal \(glossy\)", "Normale (brillante)"),
    (r"^Non-glossy deck", "Version deck (mate)"),
    (r"^Deck print", "Version deck"),
    (r"^Holo \(Shiny.*1st", "Holo chromatique · 1re éd."),
    (r"^Holo \(Shiny.*Unlimited", "Holo chromatique · illimitée"),
    (r"^Reverse Holo, 1st", "Reverse · 1re éd."),
    (r"^Reverse Holo, Unlimited", "Reverse · illimitée"),
    (r"^Holo, 1st", "Holo · 1re éd."),
    (r"^Holo, Unlimited", "Holo · illimitée"),
    (r"^1st Edition", "1re édition"),
    (r"^Unlimited", "Illimitée"),
    (r"^Promo", "Promo"),
    (r"Pokémon Card Gym", "Tampon Pokémon Card Gym"),
    (r"^Shiny \(secret\)", "Chromatique (secrète)"),
    (r"^Full Art", "Full Art (secrète)"),
    (r"^Special Full Art", "Full Art alternative (secrète)"),
    (r"^Poké Ball Mirror", "Reverse Poké Ball"),
    (r"^Master Ball Mirror", "Reverse Master Ball"),
    (r"Sprigatito", "Tampon deck Poussacha"),
    (r"^Art Rare", "Art Rare (AR)"),
    (r"^Reverse Mirror", "Reverse"),
    (r"^Reverse", "Reverse"),
    (r"^Mirror", "Reverse"),
    (r"^Holo", "Holo"),
    (r"^Normal", "Normale"),
]
def variant_fr(v):
    for pat, lab in VARIANT_FR:
        if re.search(pat, v or "", re.I): return lab
    return v or "Normale"

# Japanese product -> (French set translation, where to find it)
JA_SET_FR = {
    "Expansion Pack (Base Set)": ("Expansion Pack (Set de Base japonais)", "Boosters Expansion Pack (1996)"),
    "Pokémon Jungle": ("Pokémon Jungle", "Boosters Pokémon Jungle"),
    "Rocket Gang (Team Rocket)": ("Rocket Gang (Team Rocket)", "Boosters Rocket Gang"),
    "Expansion Sheet 1 (Vending Machine Series 1, Blue)": ("Planche distributeur n°1 (bleue)", "Planches de cartes vendues en distributeur automatique, série 1"),
    "Expansion Sheet 3 (Vending Machine Series 3, Green)": ("Planche distributeur n°3 (verte)", "Planches de cartes vendues en distributeur automatique, série 3"),
    "Quick Starter Gift Set - Green Deck": ("Quick Starter Gift Set · deck vert", "Coffret Quick Starter Gift Set (deck vert)"),
    "Guren Town Gym (Blaine) theme deck": ("Arène de Cramois'Île (deck Auguste)", "Deck préconstruit de l'arène de Cramois'Île, uniquement"),
    "Challenge from the Darkness (Gym Booster 2)": ("Challenge from the Darkness (Gym Challenge japonais)", "Boosters Challenge from the Darkness"),
    "Pokémon VS": ("Pokémon VS", "Boosters Pokémon VS (exclusivité japonaise)"),
    "Base Expansion Pack (e-Card)": ("Base Expansion Pack (Expedition japonais)", "Boosters Base Expansion Pack"),
    "P Promotional cards (e-Card era)": ("Promo P", "Encart du magazine CoroCoro Comic (janvier 2002)"),
    "Wind from the Sea (e-Card)": ("Wind from the Sea (Aquapolis japonais)", "Boosters Wind from the Sea"),
    "Flight of Legends": ("Flight of Legends (Rouge Feu & Vert Feuille japonais)", "Boosters Flight of Legends"),
    "Venusaur & Blastoise Random Constructed Starter Decks": ("Decks Random Constructed Florizarre / Tortank", "Decks de démarrage aléatoires Florizarre ou Tortank"),
    "Holon Research Tower - Fire Quarter Deck": ("Holon Research Tower · quart de deck Feu", "Coffret Holon Research Tower (quart de deck Feu)"),
    "Space-Time Creation (Diamond / Pearl Collection)": ("Space-Time Creation (Diamant & Perle japonais)", "Boosters Diamond Collection ou Pearl Collection"),
    "Intense Fight in the Destroyed Sky": ("Intense Fight in the Destroyed Sky (Tempête japonais)", "Boosters Intense Fight in the Destroyed Sky"),
    "Infernape vs Gallade SP Deck Kit (Infernape half deck)": ("Kit SP Simiabraz vs Gallame", "Kit de decks SP Simiabraz vs Gallame (demi-deck Simiabraz)"),
    "Advent of Arceus": ("Advent of Arceus (Arceus japonais)", "Boosters Advent of Arceus"),
    "DPt-P Promotional cards": ("Promo DPt-P", "Lot de participation Pokémon Card Gym Challenge (juin 2009)"),
    "Arceus LV.X Deck: Grass & Fire": ("Deck Arceus LV.X Plante & Feu", "Deck construit Arceus LV.X Plante & Feu"),
    "Clash at the Summit": ("Clash at the Summit (Triomphant japonais)", "Boosters Clash at the Summit"),
    "Wild Blaze": ("Wild Blaze (Étincelles japonais)", "Boosters Wild Blaze"),
    "Starter Pack (XY BREAK, Generations equivalent)": ("Starter Pack 20e anniversaire (Générations japonais)", "Coffret Starter Pack XY BREAK"),
    "Fever-Burst Fighter": ("Fever-Burst Fighter (Offensive Vapeur japonais)", "Boosters Fever-Burst Fighter"),
    "Expansion Pack 20th Anniversary": ("Expansion Pack 20th Anniversary (Évolutions japonais)", "Boosters Expansion Pack 20th Anniversary"),
    "Tag Bolt": ("Tag Bolt (Duo de Choc japonais)", "Boosters Tag Bolt"),
    "Remix Bout": ("Remix Bout (Éclipse Cosmique japonais)", "Boosters Remix Bout"),
    "Shield": ("Shield (Épée et Bouclier japonais)", "Boosters Shield"),
    "S-P Promotional cards": ("Promo S-P", "Pack promo Pokémon Card Gym"),
    "V Starter Deck - Fire Incineroar V": ("Deck de démarrage V Feu · Félinferno V", "Deck de démarrage V Feu (Félinferno V)"),
    "Shiny Star V": ("Shiny Star V (Destinées Radieuses japonais)", "High-class packs Shiny Star V"),
    "Silver Lance": ("Silver Lance (Règne de Glace japonais)", "Boosters Silver Lance"),
    "Start Deck 100": ("Start Deck 100", "Start Deck 100 (certains decks numérotés)"),
    "Space Juggler": ("Space Juggler (Astres Radieux japonais)", "Boosters Space Juggler"),
    "Paradigm Trigger": ("Paradigm Trigger (Tempête Argentée japonais)", "Boosters Paradigm Trigger"),
    "Pokémon Card 151": ("Pokémon Card 151 (151 japonais)", "Boosters Pokémon Card 151"),
    "Pokémon Card Game Classic - Charizard & Ho-Oh ex Deck": ("Pokémon Card Game Classic · deck Dracaufeu & Ho-Oh ex", "Coffret Pokémon Card Game Classic"),
    "Ancient Koraidon ex Starter Deck & Build Set": ("Starter Deck & Build Set Koraidon ex Ancien", "Coffret Starter Deck & Build Set Koraidon ex"),
    "Pokémon Card Game Battle Academy": ("Battle Academy (Écarlate et Violet)", "Coffret Battle Academy (deck Poussacha ex)"),
    "Hot Wind Arena": ("Hot Wind Arena (Rivalités Destinées japonais)", "Boosters Hot Wind Arena"),
    "Start Deck 100 Battle Collection": ("Start Deck 100 Battle Collection", "Start Deck 100 Battle Collection (certains decks numérotés)"),
    # Vulpix / Ninetales
    'Expansion Sheet 3 (Vending Machine cards)': ('Planche distributeur n°3 (verte)', 'Planches de cartes vendues en distributeur automatique, série 3'),
    'Quick Starter Gift Set (Green Deck)': ('Quick Starter Gift Set · deck vert', 'Coffret Quick Starter Gift Set (deck vert)'),
    "Leaders' Stadium": ("Leaders' Stadium (Gym Heroes japonais)", "Boosters Leaders' Stadium"),
    'Nivi City Gym (theme deck)': ("Arène d'Argenta (deck Pierre)", "Deck préconstruit de l'arène d'Argenta"),
    'Challenge from the Darkness': ('Challenge from the Darkness (Gym Challenge japonais)', 'Boosters Challenge from the Darkness'),
    'Guren Town Gym (theme deck)': ("Arène de Cramois'Île (deck Auguste)", "Deck préconstruit de l'arène de Cramois'Île"),
    'Darkness, and to Light...': ('Darkness, and to Light... (Neo Destiny japonais)', 'Boosters Darkness, and to Light...'),
    'Pokémon Card VS': ('Pokémon VS', 'Boosters Pokémon VS (exclusivité japonaise)'),
    'Pokémon Web': ('Pokémon Web', 'Pack Pokémon Web (exclusivité japonaise)'),
    'Base Expansion Pack': ('Base Expansion Pack (Expedition japonais)', 'Boosters Base Expansion Pack'),
    "McDonald's Pokémon-e Minimum Pack": ("Mini-pack McDonald's Pokémon-e", "Happy Meal McDonald's Japon"),
    'Wind from the Sea': ('Wind from the Sea (Aquapolis japonais)', 'Boosters Wind from the Sea'),
    'Undone Seal': ('Undone Seal (Légendes Oubliées japonais)', 'Boosters Undone Seal'),
    'Fire Quick Construction Pack': ('Quick Construction Pack Feu', 'Quick Construction Pack Feu'),
    'Offense and Defense of the Furthest Ends': ('Furthest Ends (Île des Dragons japonais)', 'Boosters Offense and Defense of the Furthest Ends'),
    'World Champions Pack': ('World Champions Pack (Gardiens du Pouvoir japonais)', 'World Champions Pack'),
    'Secret of the Lakes': ('Secret of the Lakes (Trésors Mystérieux japonais)', 'Boosters Secret of the Lakes'),
    "Galactic's Conquest": ("Galactic's Conquest (Platine japonais)", "Boosters Galactic's Conquest"),
    'Melee! Pokémon Scramble': ('Melee! Pokémon Scramble', 'Collection Pokémon Scramble × JCC'),
    'SoulSilver Collection': ('SoulSilver Collection (HeartGold SoulSilver japonais)', 'Boosters SoulSilver Collection'),
    'Magmortar Battle Starter Deck': ('Deck Battle Starter Maganon', 'Deck Battle Starter Maganon'),
    'Dragon Blast': ('Dragon Blast (Dragons Exaltés japonais)', 'Boosters Dragon Blast'),
    'BW-P Promotional cards': ('Promo BW-P', "Promo d'achat d'un display Dragon Blast / Dragon Blade"),
    'EX Battle Boost': ('EX Battle Boost (Trésors Légendaires japonais)', 'Boosters EX Battle Boost'),
    'Gaia Volcano': ('Gaia Volcano (Primo-Choc japonais)', 'Boosters Gaia Volcano'),
    'XY-P Promotional cards': ('Promo XY-P', 'Pack promo Pokémon Card Gym'),
    'SM-P Promotional cards': ('Promo SM-P', 'Promo'),
    'Islands Await You': ('Islands Await You (Gardiens Ascendants japonais)', 'Boosters Islands Await You'),
    'Facing a New Trial': ('Facing a New Trial', 'Boosters renforcés Facing a New Trial'),
    'GX Battle Boost': ('GX Battle Boost', 'High-class pack GX Battle Boost'),
    'Fairy Rise': ('Fairy Rise (Tonnerre Perdu japonais)', 'Boosters Fairy Rise'),
    'GX Ultra Shiny': ('GX Ultra Shiny (Destinées Occultes japonais)', 'High-class pack GX Ultra Shiny'),
    'Alter Genesis': ('Alter Genesis (Éclipse Cosmique japonais)', 'Boosters Alter Genesis'),
    'Tag All Stars': ('Tag All Stars', 'High-class pack Tag All Stars'),
    'V Starter Set Fire': ('Starter Set V Feu', 'Starter Set V Feu'),
    'VMAX Rising': ('VMAX Rising (Clash des Rebelles japonais)', 'Boosters VMAX Rising'),
    'Rebellion Crash': ('Rebellion Crash (Clash des Rebelles japonais)', 'Boosters Rebellion Crash'),
    'V Starter Deck Fire (Incineroar)': ('Deck de démarrage V Feu · Félinferno V', 'Deck de démarrage V Feu (Félinferno V)'),
    'Sword & Shield Family Pokémon Card Game': ('Coffret familial Épée et Bouclier', 'Coffret Family Pokémon Card Game'),
    'Blue Sky Stream': ('Blue Sky Stream (Évolution Céleste japonais)', 'Boosters Blue Sky Stream'),
    'Lost Abyss': ('Lost Abyss (Origine Perdue japonais)', 'Boosters Lost Abyss'),
    'Incandescent Arcana': ('Incandescent Arcana (Tempête Argentée japonais)', 'Boosters Incandescent Arcana'),
    'Charizard VSTAR vs Rayquaza VMAX Special Deck Set': ('Special Deck Set Dracaufeu VSTAR vs Rayquaza VMAX', 'Coffret Special Deck Set Dracaufeu VSTAR vs Rayquaza VMAX'),
    'Ruler of the Black Flame': ('Ruler of the Black Flame (Flammes Obsidiennes japonais)', 'Boosters Ruler of the Black Flame'),
    'Crimson Haze': ('Crimson Haze (Mascarade Crépusculaire japonais)', 'Boosters Crimson Haze'),
    'Stellar Tera Type Starter Set Ceruledge ex': ('Starter Set Stellaire Malvalame ex', 'Starter Set Téracristal Stellaire Malvalame ex'),
    'Mega Brave': ('Mega Brave (Méga-Évolution japonais)', 'Boosters Mega Brave'),
    'Ninja Spinner': ('Ninja Spinner (Chaos Ascendant japonais)', 'Boosters Ninja Spinner'),
    '30th Celebration Premium Deck Set Espeon & Umbreon': ('Premium Deck Set 30e anniversaire Mentali & Noctali', 'Coffret Premium Deck Set 30e anniversaire Mentali & Noctali'),
}

# cards Bulbapedia lists under an international card although they have no English print themselves
GROUP_OVERRIDE = {("S-P", "310"): "swsh12-021", ("S-P", "188"): "swsh12-021"}

def norm_num(n):
    n = n or ""
    if n.startswith("No.0"): return n.split(" ")[0]
    return n

def convert(lang, raw, set_fr, printed):
    out, seen = [], {}
    for e in raw:
        slug = e["pokemon"]
        poke = species(slug)
        galar = "galar" in slug or "alola" in slug
        g = GROUP_OVERRIDE.get((e.get("set_code"), (e.get("number") or "").split("/")[0])) or group_for(e.get("equivalent_en"))
        if not g and "Classic" in (e.get("set_name_en") or ""):
            g = f"classic-{poke}"
        tr = set_fr.get(e.get("set_name_en")) or (e.get("set_name_en"), f"Boosters {e.get('set_name_en')}")
        num = norm_num(e.get("number"))
        base = re.sub(r"[^a-z0-9]+", "-", f"{e.get('set_code') or e.get('set_name_en')}-{num}-{e.get('variant')}".lower()).strip("-")
        cid = f"{lang}:{base}"
        if cid in seen: seen[cid] += 1; cid += f"-{seen[cid]}"
        else: seen[cid] = 0
        nfr = name_fr(slug)
        # set abbreviation: printed code if the card has one, else the set code (shown as "not printed")
        sc = e.get("set_code")
        pc = e.get("printed_code") if "printed_code" in e else printed.get(sc)
        code = pc or (sc if sc and re.fullmatch(r"[A-Za-z0-9.-]{2,8}", sc) else None)
        item = {
            "id": cid, "g": g, "poke": poke, "galar": galar, "y": e["year"],
            "gt": f"{nfr} · {tr[0]}", "gs": f"Exclusivité {'japonaise' if lang == 'ja' else 'chinoise'} · {e.get('set_name_local') or ''}",
            "n": e.get("name_local") or nfr, "code": code, "cp": bool(pc), "s": e.get("set_name_local") or tr[0], "sf": tr[0],
            "number": num, "r": None if e.get("rarity") in (None, "None") else e.get("rarity"),
            "v": variant_fr(e.get("variant")), "b": e.get("product_fr") or (f"Promo · {e.get('product')}" if re.fullmatch(r"(\w+-)?P", sc or "") and e.get("product") else tr[1]), "img": e.get("image"), "en": e.get("equivalent_en"),
            "u": bool(e.get("uncertain")), "set_code": e.get("set_code") or "x",
        }
        if e.get("notes") and len(e["notes"]) < 220: item["note"] = e["notes"]
        out.append(item)
    return out

def load_list(*names):
    out = []
    for n in names:
        p = os.path.join(SRC, n)
        if os.path.exists(p): out += json.load(open(p, encoding="utf-8"))
    return out

def main():
    from zh_sets import ZH_SET_FR
    for lang, files, set_fr, codes in (
        ("ja", ("ja_cards_raw.json", "ja_vulpix_raw.json"), JA_SET_FR, "ja_printed_codes.json"),
        ("zh", ("zh_cards_raw.json", "zh_vulpix_raw.json"), ZH_SET_FR, "zh_printed_codes.json"),
    ):
        printed = json.load(open(os.path.join(SRC, codes), encoding="utf-8")) if os.path.exists(os.path.join(SRC, codes)) else {}
        res = convert(lang, load_list(*files), set_fr, printed)
        json.dump(res, open(os.path.join(SRC, f"{lang}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(lang, len(res), "grouped", sum(1 for r in res if r["g"]))

if __name__ == "__main__":
    main()
