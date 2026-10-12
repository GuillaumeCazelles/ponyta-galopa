"""Converts src/cameos_raw.json (Ponyta cameo research) into src/cameos.json.
Usage: python cameos_import.py src/cameos_raw.json src/cameos.json"""
import json, re, sys, urllib.request
src, dest = sys.argv[1], sys.argv[2]
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ptk"}), timeout=30))
TD = {"CRZ-GG10": "swsh12.5gg-GG10", "SCR-152": "sv07-152", "BKT-96": "xy8-96"}
CODE = {"CRZ-GG10": ("CRZ", 0), "SCR-152": ("SCR", 1), "BKT-96": ("BKT", 0)}
WHERE = {
    "CRZ-GG10": "Ponyta de Galar à gauche, dans la clairière où dort Mew",
    "SCR-152": "Bonbon violet en forme de Ponyta de Galar dans le grand bocal à droite (stylisé, à confirmer)",
    "BKT-96": "Fresque murale derrière Archéodong : un cheval à crinière de feu qui ressemble à Ponyta (à confirmer)",
}
out = []
for e in json.load(open(src, encoding="utf-8")):
    v = {"Normal": "Normale", "Illustration rare": "Illustration rare"}.get(e["variant"], e["variant"])
    key = re.sub(r"[^a-z0-9]+", "-", v.lower()).strip("-")
    d = dict(e, id=f"{e['lang']}:cameo:{e['group_key']}:{key}", v=v, where_in_art=WHERE[e["group_key"]])
    if d.get("image"): d["image"] = re.sub(r"/(high|low)\.(png|webp|jpg)$", "", d["image"])
    if e["lang"] == "fr":
        td = TD[e["group_key"]]; card = get(f"https://api.tcgdex.net/v2/fr/cards/{td}")
        cm = ((card.get("pricing") or {}).get("cardmarket") or {}).get("idProduct")
        d["td"] = td
        if cm: d["cm"] = cm; d["h"] = 1 if v == "Reverse" else 0
        d["code"], cp = CODE[e["group_key"]]
        d["printed_code"] = d["code"] if cp else None
    if d.get("rarity") == "(none printed)": d["rarity"] = None
    out.append(d)
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), [ (d["id"], d.get("cm")) for d in out if d["lang"] == "fr"])
