"""Normalises the Japanese / simplified Chinese research lists (src/ja_cards_raw.json, src/zh_cards_raw.json)
into src/ja.json and src/zh.json, the format build.py reads. Run before build.py."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
sys.path.insert(0, HERE)

NAME_FR = {
    "ponyta": "Ponyta", "rapidash": "Galopa", "galar-ponyta": "Ponyta de Galar", "galar-rapidash": "Galopa de Galar",
    "galar-rapidash-v": "Galopa de Galar V", "blaines-ponyta": "Ponyta de Blaine", "blaines-rapidash": "Galopa de Blaine",
    "rapidash-4": "Galopa 4", "dark-rapidash": "Galopa obscur", "karens-rapidash": "Galopa de Marion",
}
# English set name (as written in equivalent_en) -> TCGdex set id
EN_SET = [
    ("EX FireRed & LeafGreen", "ex6"), ("FireRed & LeafGreen", "ex6"), ("EX Delta Species", "ex11"), ("Delta Species", "ex11"),
    ("Expedition Base Set", "ecard1"), ("Expedition", "ecard1"), ("Wizards Black Star Promo", "basep"),
    ("SWSH Black Star Promo", "swshp"), ("Shining Fates", "swsh4.5sv"), ("Base Set", "base1"), ("Jungle", "base2"),
    ("Team Rocket", "base5"), ("Gym Heroes", "gym1"), ("Gym Challenge", "gym2"), ("Aquapolis", "ecard2"),
    ("Diamond & Pearl", "dp1"), ("Stormfront", "dp7"), ("Rising Rivals", "pl2"), ("Arceus", "pl4"),
    ("Triumphant", "hgss4"), ("Flashfire", "xy2"), ("Generations", "g1"), ("Steam Siege", "xy11"),
    ("Evolutions", "xy12"), ("Team Up", "sm9"), ("Cosmic Eclipse", "sm12"), ("Sword & Shield", "swsh1"),
    ("Chilling Reign", "swsh6"), ("Astral Radiance", "swsh10"), ("Silver Tempest", "swsh12"), ("151", "sv03.5"),
    ("Temporal Forces", "sv05"), ("Stellar Crown", "sv07"), ("Destined Rivals", "sv10"), ("Obsidian Flames", "sv03"),
]

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
        if eq.startswith(name + " ") or eq.startswith(name + " SV") :
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
}

# cards Bulbapedia lists under an international card although they have no English print themselves
GROUP_OVERRIDE = {("S-P", "310"): "swsh12-021", ("S-P", "188"): "swsh12-021"}

def norm_num(n):
    n = n or ""
    if n.startswith("No.0"): return n.split(" ")[0]
    return n

def convert(lang, raw, set_fr):
    out, seen = [], {}
    for e in raw:
        slug = e["pokemon"]
        poke = "ponyta" if "ponyta" in slug else "rapidash"
        galar = slug.startswith("galar")
        g = GROUP_OVERRIDE.get((e.get("set_code"), (e.get("number") or "").split("/")[0])) or group_for(e.get("equivalent_en"))
        if not g and "Classic" in (e.get("set_name_en") or ""):
            g = f"classic-{poke}"
        tr = set_fr.get(e.get("set_name_en")) or (e.get("set_name_en"), f"Boosters {e.get('set_name_en')}")
        num = norm_num(e.get("number"))
        base = re.sub(r"[^a-z0-9]+", "-", f"{e.get('set_code') or e.get('set_name_en')}-{num}-{e.get('variant')}".lower()).strip("-")
        cid = f"{lang}:{base}"
        if cid in seen: seen[cid] += 1; cid += f"-{seen[cid]}"
        else: seen[cid] = 0
        name_fr = NAME_FR.get(slug, slug)
        item = {
            "id": cid, "g": g, "poke": poke, "galar": galar, "y": e["year"],
            "gt": f"{name_fr} · {tr[0]}", "gs": f"Exclusivité {'japonaise' if lang == 'ja' else 'chinoise'} · {e.get('set_name_local') or ''}",
            "n": e.get("name_local") or name_fr, "s": e.get("set_name_local") or tr[0], "sf": tr[0],
            "number": num, "r": None if e.get("rarity") in (None, "None") else e.get("rarity"),
            "v": variant_fr(e.get("variant")), "b": tr[1], "img": e.get("image"), "en": e.get("equivalent_en"),
            "u": bool(e.get("uncertain")), "set_code": e.get("set_code") or "x",
        }
        if e.get("notes") and len(e["notes"]) < 220: item["note"] = e["notes"]
        out.append(item)
    return out

def main():
    ja = json.load(open(os.path.join(SRC, "ja_cards_raw.json"), encoding="utf-8"))
    res = convert("ja", ja, JA_SET_FR)
    json.dump(res, open(os.path.join(SRC, "ja.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    miss = [r for r in res if not r["g"]]
    print("ja", len(res), "grouped", len(res) - len(miss), "jp-only", len(miss))
    zp = os.path.join(SRC, "zh_cards_raw.json")
    if os.path.exists(zp):
        from zh_sets import ZH_SET_FR
        zh = json.load(open(zp, encoding="utf-8"))
        res = convert("zh", zh, ZH_SET_FR)
        json.dump(res, open(os.path.join(SRC, "zh.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("zh", len(res), "grouped", sum(1 for r in res if r["g"]))

if __name__ == "__main__":
    main()
