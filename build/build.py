"""Builds ../index.html from template.html + data sources in src/.

src/tcgdex_raw.json  TCGdex card details (en, fr, ja) for dexId 77, 78 (Ponyta, Rapidash) and 37, 38 (Vulpix, Ninetales).
                     English cards are only used as the binder skeleton (grouping, images, prices): the app shows FR, JP and CN.
src/sets.json        TCGdex set names and release dates
src/pg.json, src/ps.json   Cardmarket public price guide and product list (Pokémon), downloaded on each run (not committed)
src/ja.json, src/zh.json   Japanese / simplified Chinese card lists (normalised, see asian.py)
src/extra_enfr.json  English/French cards and variants missing from TCGdex
src/icon.png         home-screen icon, 180×180
"""
import json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
PRICE_GUIDE_URL = "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json"
PRODUCTS_URL = "https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_6.json"
def jload(name, default=None):
    p = os.path.join(SRC, name)
    if not os.path.exists(p): return default
    with open(p, encoding="utf-8") as f: return json.load(f)

for url, name in ((PRICE_GUIDE_URL, "pg.json"), (PRODUCTS_URL, "ps.json")):
    if "--offline" not in sys.argv or not os.path.exists(os.path.join(SRC, name)):
        print("Téléchargement", name, "(Cardmarket)…")
        urllib.request.urlretrieve(url, os.path.join(SRC, name))

raw = jload("tcgdex_raw.json")
SETS = jload("sets.json")
PG = {p["idProduct"]: p for p in jload("pg.json")["priceGuides"]}
PRODUCTS = jload("ps.json")["products"]
PROD = {p["idProduct"]: p for p in PRODUCTS}

def is_pocket(c):  # TCG Pocket (digital) sets A1, A1a, B1… and promo P-A
    sid = c["set"]["id"]
    return bool(re.match(r"^(A|B)\d", sid)) or sid.startswith("P-")

EN = [c for c in raw["en"] if "id" in c and not is_pocket(c)]
SET_EXP = {}
for _c in EN:
    _cm = ((_c.get("pricing") or {}).get("cardmarket") or {}).get("idProduct")
    if _cm in PROD: SET_EXP.setdefault(_c["set"]["id"], PROD[_cm]["idExpansion"])
FR = {c["id"]: c for c in raw["fr"] if "id" in c and not is_pocket(c)}

NAME_FR = {
    "Ponyta": "Ponyta", "Rapidash": "Galopa", "Galarian Ponyta": "Ponyta de Galar",
    "Galarian Rapidash": "Galopa de Galar", "Galarian Rapidash V": "Galopa de Galar V",
    "Dark Rapidash": "Galopa obscur", "Blaine's Ponyta": "Ponyta d'Auguste",
    "Blaine's Rapidash": "Galopa d'Auguste", "Rapidash E4": "Galopa 4", "Karen's Rapidash": "Galopa de Marion",
    "Vulpix": "Goupix", "Ninetales": "Feunard", "Alolan Vulpix": "Goupix d'Alola", "Alolan Ninetales": "Feunard d'Alola",
    "Blaine's Vulpix": "Goupix d'Auguste", "Blaine's Ninetales": "Feunard d'Auguste", "Brock's Vulpix": "Goupix de Pierre",
    "Brock's Ninetales": "Feunard de Pierre", "Light Ninetales": "Feunard lumineux",
}
RARITY_FR = {
    "Common": "Commune", "Uncommon": "Peu commune", "Rare": "Rare", "Holo Rare": "Rare holo", "Rare Holo": "Rare holo",
    "Ultra Rare": "Ultra rare", "Shiny rare": "Chromatique (Shiny)", "Illustration rare": "Illustration rare",
    "Promo": "Promo", "None": "—", "Double rare": "Double rare", "Secret Rare": "Secrète", "Holo Rare V": "Rare holo V",
    "Holo Rare VSTAR": "Rare holo VSTAR", "Special illustration rare": "Illustration spéciale rare",
}
# French set names for sets TCGdex has no French data for (released in French: see extra_enfr.json notes)
SET_FR_FALLBACK = {"gym1": "Gym Heroes", "gym2": "Gym Challenge", "pl4": "Arceus", "lc": "Legendary Collection"}
# English-only sets (no French print)
EN_ONLY_SETS = {"basep"}
# Cardmarket idProduct for cards where TCGdex has none or a wrong one (matched by name + attacks + expansion in products_singles_6.json)
CM_FIX = {
    "xy2-14": 281497, "xy2-15": 281498, "g1-14": 288454, "g1-15": 288455, "xy11-16": 291523, "xy11-17": 291524,
    "xy12-19": 293375, "sm9-17": 368949, "sm9-18": 368950, "sm12-23": 407764, "sm12-24": 407769,
    "swsh1-81": 427206, "swsh1-82": 436534, "dp1-94": 277593, "dp1-59": 277558, "dp7-71": 278369, "dp7-22": 278320,
    "ex11-78": 276841, "ex11-52": 276815, "pl4-46": 278918, "pl4-72": 278944, "pl4-SH11": 278869, "pl4-28": 278900,
    "pl4-47": 278919, "pl2-47": 278621, "gym1-63": 274199, "gym2-64": 274332, "gym2-33": 274301, "lc-87": 274852,
    "lc-60": 274825, "base5-64": 274117, "base5-44": 274097, "base2-44": 273841, "ecard1-26": 274901,
    "ecard1-62": 274937, "ecard1-126": 275001, "ecard2-102": 275177, "ecard2-31": 275103, "basep-51": 275470,
    "ex6-13": 276189, "ex6-76": 276252, "hgss4-8": 279538, "hgss4-72": 279602,
    # TCGdex points the holo and non-holo Ninetales of Expedition / Aquapolis to the same product
    "ecard1-21": 274896, "ecard1-57": 274932, "ecard2-25": 275097, "ecard2-H19": 275042,
}
BOOSTER_NOTE = {
    "g1": "Boosters Générations (vendus en coffrets et blisters)",
    "sv03.5": "Boosters 151 (coffrets dresseur d'élite, collections, blisters)",
    "swsh4.5sv": "Boosters Destinées Radieuses (cartes du Coffre Étincelant)",
    "basep": "Promo Wizards Black Star",
    "swshp": "Promo",
}
BOOSTER_NOTE_EN = {
    "g1": "Boosters Generations (vendus en coffrets et blisters)",
    "sv03.5": "Boosters 151 (coffrets dresseur d'élite, collections, blisters)",
    "swsh4.5sv": "Boosters Shining Fates (cartes du Shiny Vault)",
    "basep": "Promo Wizards Black Star",
    "swshp": "Promo",
}

def year(sid):
    d = (SETS.get(sid, {}).get("en") or {}).get("date") or "2000"
    return int(d[:4]), d

def poke_of(name_en):
    """(species key, regional form?) from an English card name."""
    n = name_en.lower()
    for k in ("ponyta", "rapidash", "vulpix", "ninetales"):
        if k in n: return k, ("galarian" in n or "alolan" in n)
    return "cameo", False

def set_code(sid):
    """Official set abbreviation and whether it is printed on the card (since Scarlet & Violet)."""
    s = SETS.get(sid, {})
    ab = ((s.get("fr") or {}).get("abbr") or (s.get("en") or {}).get("abbr") or {}).get("official")
    printed = bool(re.match(r"^(sv|me|30th)", sid))
    return ab, printed

# Cardmarket expansion of each TCGdex set, learned from cards whose product id TCGdex knows
def cm_auto(c):
    """Find the Cardmarket single for an English TCGdex card by name + attacks inside the set's expansion."""
    exp = SET_EXP.get(c["set"]["id"])
    if not exp: return None
    moves = [a["name"] for a in c.get("abilities", [])] + [a["name"] for a in c.get("attacks", [])]
    want = (c["name"] + (" [" + " | ".join(moves) + "]" if moves else "")).lower()
    hits = [p for p in PRODUCTS if p["idExpansion"] == exp and re.sub(r" \(V\.\d+\)", "", p["name"]).lower() == want]
    return hits[0]["idProduct"] if len(hits) == 1 else None

def variant_label(v, card, lang):
    """Return (key, label FR, uses reverse/holo price column, price note)."""
    t = (v.get("type") or "normal").lower()
    stamps = [s.lower() for s in (v.get("stamp") or [])]
    sub = (v.get("subtype") or "").lower()
    foil = (v.get("foil") or "").lower()
    rar = (card.get("rarity") or "").lower()
    setid = card["set"]["id"]
    if "1st-edition" in stamps or "1re édition" in stamps or "1re édition" in stamps:
        return "1st", "1re édition", False, "Cardmarket ne sépare pas la 1re édition"
    if sub == "shadowless": return "shadowless", "Shadowless", False, None
    if sub == "1999-2000-copyright": return "1999", "Impression 1999-2000", False, None
    if "pokemon-center-ny" in stamps: return "pcny", "Tampon Pokémon Center NY", False, "Pas de prix séparé"
    if "player-rewards-program" in stamps: return "prp", "Tampon Play! Pokémon", False, None
    if "staff" in stamps or t == "staff": return "staff", "Tampon Staff", False, "Pas de prix séparé"
    if "set-logo" in stamps or "logo de la série" in stamps:
        if setid.startswith("ex"): return "rev", "Reverse (logo)", True, None
        return "logo", "Tampon logo d'extension", False, None
    if t == "reverse": return "rev", "Reverse", True, None
    if t == "holo":
        if foil == "cosmos": return "cosmos", "Holo cosmos", False, None
        if foil == "snowflake": return "snow", "Holo tampon flocon", False, None
        return "holo", "Holo", False, None
    if any(k in rar for k in ("holo", "ultra", "secret", "shiny", "double", "illustration")): return "holo", "Holo", False, None
    if sub == "unlimited": return "unl", "Illimitée", False, None
    return "normal", "Normale", False, None

# BW / XY / SM main sets: TCGdex has no variant data, but every regular card (not EX/GX/BREAK, full art or secret)
# also came as a reverse holo in EN and FR (Bulbapedia, Cardmarket)
def needs_reverse(c):
    sid, rar, name = c["set"]["id"], (c.get("rarity") or "").lower(), c["name"]
    if not re.fullmatch(r"(bw|xy|sm)\d+|g1", sid): return False
    if re.search(r"(EX|GX|BREAK)|-GX|-EX", name): return False
    return not any(k in rar for k in ("ultra", "secret", "shiny"))
IMG_FIX = {"swsh4.5sv-SV047": "https://images.pokemontcg.io/swsh45sv/SV047_hires.png",
           "swsh4.5sv-SV048": "https://images.pokemontcg.io/swsh45sv/SV048_hires.png"}

# promo release dates (TCGdex only has the promo set start date)
CARD_DATE = {"basep-51": "2002-11-01", "swshp-SWSH013": "2020-02-07", "swshp-SWSH111": "2021-05-07", "swshp-SWSH270": "2022-11-11"}

VORDER = ["1st", "shadowless", "unl", "normal", "1999", "holo", "cosmos", "rev", "logo", "prp", "pcny", "staff"]

GROUPS, CARDS = [], []
CDATE = {}  # card id -> release date, used to order binder pages by first release in any language
GID = {}

def add_group(gid, poke, galar, y, date, title, sub, order):
    if gid in GID: return GID[gid]
    g = {"id": gid, "poke": poke, "rg": galar, "y": y, "t": title, "s": sub, "o": order}
    GROUPS.append(g); GID[gid] = g
    return g

def num_sort(n):
    m = re.search(r"\d+", str(n)); return int(m.group()) if m else 0

def build_enfr():
    extra = jload("extra_enfr.json", {}) or {}
    fr_absent = set(extra.get("fr_absent", []))       # tcgdex ids with no French print
    fr_force = extra.get("fr_force", {})              # tcgdex id -> {"set": FR set name, "variants": [...] (optional)}
    var_extra = extra.get("variants", [])             # extra variants [{id, lang, key, label, cm, h, b}]
    booster = extra.get("booster", {})                # "tcgdexid" or "tcgdexid:vkey" -> {"fr": "...", "en": "..."}
    labels = extra.get("labels", {})                  # card id -> variant label override
    unc = {(ve["id"], ve["key"]) for ve in var_extra if ve.get("u")}
    for c in EN:
        sid = c["set"]["id"]; y, date = year(sid)
        if c["id"] in CARD_DATE: date = CARD_DATE[c["id"]]; y = int(date[:4])
        poke, galar = poke_of(c["name"])
        f = FR.get(c["id"])
        name_fr = (f or {}).get("name") or NAME_FR.get(c["name"], c["name"])
        set_fr = (f or {}).get("set", {}).get("name") or SET_FR_FALLBACK.get(sid) or c["set"]["name"]
        rar_fr = RARITY_FR.get(c.get("rarity") or "None", c.get("rarity") or "—")
        ill = c.get("illustrator")
        title = f"{name_fr} · {set_fr}"
        sub = " · ".join(x for x in [f"n° {c['localId']}", rar_fr, f"illustration {ill}" if ill else None] if x)
        g = add_group(c["id"], poke, galar, y, date, title, sub, f"{date}-{num_sort(c['localId']):04d}")
        total = (SETS.get(sid, {}).get("en") or {}).get("total")
        lid = c["localId"]
        num = f"{lid}/{total}" if total and str(lid).isdigit() and sid not in ("basep", "swshp") else lid
        base_cm = CM_FIX.get(c["id"]) or ((c.get("pricing") or {}).get("cardmarket") or {}).get("idProduct") or cm_auto(c)
        if c.get("image") and "img" not in g: g["img"] = c["image"]
        code, printed = set_code(sid)

        langs = ["en"]
        if c["id"] not in fr_absent and sid not in EN_ONLY_SETS and (f or c["id"] in fr_force or sid in SET_FR_FALLBACK):
            langs.append("fr")
        for lang in langs:
            src = f if (lang == "fr" and f) else c
            vds = [v for v in (src.get("variants_detailed") or []) if (v.get("size") or "standard").lower() != "jumbo"]
            if lang == "fr" and not f:
                vds = [v for v in (c.get("variants_detailed") or []) if (v.get("size") or "standard").lower() != "jumbo"]
            seen = set(); items = []
            for v in vds:
                key, label, h, np = variant_label(v, src, lang)
                if lang == "fr" and key in ("shadowless", "1999", "pcny"): continue
                if lang == "fr" and sid == "base1" and key == "normal": key, label = "unl", "Illimitée"
                if key in seen: continue
                seen.add(key)
                cm = (v.get("thirdParty") or {}).get("cardmarket") or base_cm
                if sid in CM_FIX and False: pass
                if c["id"] in CM_FIX and key not in ("shadowless", "1st", "cosmos", "prp"): cm = CM_FIX[c["id"]]
                if c["id"] == "base1-60": cm = 660167 if key in ("shadowless", "1st") else 273755
                items.append((key, label, h, np, cm))
            if str(lid).startswith("SH"):
                items = [("holo", "Holo chromatique", False, None, base_cm)]
            if needs_reverse(c) and "rev" not in {i[0] for i in items}:
                items.append(("rev", "Reverse", True, None, base_cm))
            if lang == "fr" and c["id"] in fr_force and fr_force[c["id"]].get("variants"):
                keep = set(fr_force[c["id"]]["variants"]); items = [i for i in items if i[0] in keep]
            for ve in var_extra:
                if ve["id"] == c["id"] and ve["lang"] in (lang, "both") and ve["key"] not in seen:
                    items.append((ve["key"], ve["label"], ve.get("h", False), ve.get("np"), ve.get("cm")))
                    seen.add(ve["key"])
            items.sort(key=lambda i: VORDER.index(i[0]) if i[0] in VORDER else 99)
            for k, (key, label, h, np, cm) in enumerate(items):
                setname = set_fr if lang == "fr" else c["set"]["name"]
                if lang == "fr" and c["id"] in fr_force and fr_force[c["id"]].get("set"): setname = fr_force[c["id"]]["set"]
                bk = booster.get(f"{c['id']}:{key}") or booster.get(c["id"]) or {}
                b = bk.get(lang) or (BOOSTER_NOTE if lang == "fr" else BOOSTER_NOTE_EN).get(sid) or \
                    f"Boosters {setname}"
                img = (src.get("image") if (lang == "en" or f) else None) or (IMG_FIX.get(c["id"]) if lang == "en" else None)
                card = {
                    "id": f"{lang}:{c['id']}:{key}", "g": g["id"], "l": lang,
                    "n": name_fr if lang == "fr" else c["name"], "en": c["name"],
                    "s": setname, "num": num, "r": rar_fr if lang == "fr" else (c.get("rarity") or "—"),
                    "v": labels.get(f"{lang}:{c['id']}:{key}", label), "b": b, "y": y, "img": img, "o": k,
                }
                if cm and cm in PG: card["cm"] = cm; card["h"] = 1 if h else 0
                if np: card["np"] = np
                if lang == "fr" and f and f.get("pricing", {}).get("cardmarket"): card["td"] = f["id"]
                elif lang == "fr" and c.get("pricing", {}).get("cardmarket") and f: card["td"] = f["id"]
                if lang == "fr" and not f: card["u"] = 0 if c["id"] in fr_force else 1
                if code: card["c"] = code; card["cp"] = 1 if printed else 0
                if (c["id"], key) in unc: card["u"] = 1
                CARDS.append(card); CDATE[card["id"]] = date
    # cards absent from TCGdex entirely
    for e in extra.get("cards", []):
        y = e["y"]
        gid = e["g"]
        if gid not in GID:
            add_group(gid, e["poke"], e.get("galar", False), y, str(y), e["gt"], e.get("gs", ""), e.get("go", f"{y}-9999"))
        card = {k: v for k, v in e.items() if k not in ("poke", "galar", "gt", "gs", "go")}
        CDATE[card["id"]] = e.get("go", "")[:10] or f"{y}-07-01"
        if card.get("cm") not in PG: card.pop("cm", None)
        CARDS.append(card)

def build_asian():
    for lang, fname in (("ja", "ja.json"), ("zh", "zh.json")):
        data = jload(fname, []) or []
        for e in data:
            gid = e.get("g")
            if not gid or gid not in GID:
                gid = gid or f"{lang}-{e['set_code']}-{e['number']}"
                if gid not in GID:
                    add_group(gid, e["poke"], e.get("galar", False), e["y"], str(e["y"]), e["gt"], e.get("gs", ""),
                              e.get("go") or f"{e['y']}-{num_sort(e.get('number'))+5000:04d}")
            card = {"id": e["id"], "g": gid, "l": lang, "n": e["n"], "s": e["s"], "sf": e.get("sf"), "num": e.get("number") or "",
                    "r": e.get("r") or "—", "v": e.get("v") or "Normale", "b": e.get("b"), "y": e["y"], "img": e.get("img"),
                    "o": e.get("o", 0), "en": e.get("en")}
            if e.get("u"): card["u"] = 1
            if e.get("note"): card["note"] = e["note"]
            if e.get("code"): card["c"] = e["code"]; card["cp"] = 1 if e.get("cp") else 0
            if e.get("cm") in PG: card["cm"] = e["cm"]; card["h"] = e.get("h", 0)
            CARDS.append({k: v for k, v in card.items() if v not in (None, "")}); CDATE[card["id"]] = f"{e['y']}-07-01"

def build_cameos():
    """Cards where Ponyta appears in the artwork without being the card's Pokémon (src/cameos.json)."""
    for e in jload("cameos.json", []) or []:
        gid = "cameo-" + e["group_key"]
        if gid not in GID:
            add_group(gid, "cameo", False, e["year"], str(e["year"]), f"{e['card_name_fr']} · {e['set_name_fr']}",
                      f"Caméo : {e.get('where_in_art') or 'Ponyta dans l’illustration'}", f"{e['year']}-12-31-{num_sort(e.get('number')):04d}")
        if e.get("image") and "img" not in GID[gid]: GID[gid]["img"] = e["image"]
        card = {"id": e["id"], "g": gid, "l": e["lang"], "n": e["card_name"], "s": e["set_name_local"], "sf": e.get("set_name_fr"),
                "num": e.get("number") or "", "r": e.get("rarity") or "—", "v": e.get("v") or "Normale", "b": e.get("product"),
                "y": e["year"], "img": e.get("image"), "o": e.get("o", 0)}
        if e.get("printed_code") or e.get("code"): card["c"] = e.get("printed_code") or e.get("code"); card["cp"] = 1 if e.get("printed_code") else 0
        if e.get("uncertain"): card["u"] = 1
        if e.get("cm") in PG: card["cm"] = e["cm"]; card["h"] = e.get("h", 0)
        if e.get("td"): card["td"] = e["td"]
        CARDS.append({k: v for k, v in card.items() if v not in (None, "")}); CDATE[card["id"]] = f"{e['year']}-07-01"

def main():
    build_enfr()
    build_asian()
    build_cameos()
    # English prints only shape the binder (grouping, fallback images, prices); they are not shown
    CARDS[:] = [c for c in CARDS if c["l"] != "en"]
    # group year = earliest card year; binder order = earliest release in any language
    for g in GROUPS:
        cs = [c for c in CARDS if c["g"] == g["id"]]
        if not cs: continue
        g["y"] = min(c["y"] for c in cs)
        first = min(CDATE.get(c["id"], f"{c['y']}-07-01") for c in cs)
        g["o"] = first + "|" + g["o"]
    used = [g for g in GROUPS if any(c["g"] == g["id"] for c in CARDS)]
    used.sort(key=lambda g: g["o"])
    for i, g in enumerate(used): g["o"] = i
    ids = [c["id"] for c in CARDS]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: sys.exit(f"duplicate ids: {sorted(dup)[:10]}")
    prices = {}
    for c in CARDS:
        cm = c.get("cm")
        if cm and cm in PG:
            p = PG[cm]
            prices[cm] = [p.get("avg30"), p.get("trend"), p.get("avg30-holo"), p.get("trend-holo")]
    pg_date = jload("pg.json").get("createdAt", "")[:10]
    data = ("const SNAP_DATE = " + json.dumps(pg_date) + ";\n"
            "const GROUPS = " + json.dumps(used, ensure_ascii=False, separators=(",", ":")) + ";\n"
            "const CARDS = " + json.dumps(CARDS, ensure_ascii=False, separators=(",", ":")) + ";\n"
            "const PRICES = " + json.dumps(prices, separators=(",", ":")) + ";")
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f: tpl = f.read()
    import base64  # home-screen icon (src/icon.png, 180×180) embedded so iOS picks it up with no extra file
    with open(os.path.join(SRC, "icon.png"), "rb") as f: icon = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    out = tpl.replace("/*__DATA__*/", data).replace("__ICON__", icon)
    dest = os.path.join(HERE, "..", "index.html")
    with open(dest, "w", encoding="utf-8") as f: f.write(out)
    from collections import Counter
    print("groups", len(used), "cards", len(CARDS), dict(Counter(c["l"] for c in CARDS)), "priced", len(prices))

if __name__ == "__main__":
    main()
