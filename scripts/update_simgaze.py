"""Lit le profil SimGaze de Kalyann Mey et écrit simgaze.json.

Autorisé par le propriétaire de SimGaze. Si la page change de forme et
qu'une valeur n'est pas trouvée, le script s'arrête sans rien écrire :
le site garde alors les derniers chiffres connus.
"""
import json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://simgaze.com/leaderboard/pro-drivers/kalyann-mey/"
OUT = Path(__file__).resolve().parent.parent / "simgaze.json"


def num(txt):
    return int(re.sub(r"[^\d]", "", txt))


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "kalyannmey.fr stats bot (autorisé par SimGaze)"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    row = None
    for tr in re.findall(r"<tr\b.*?</tr>", html, re.S):
        if "sg-cat-sports-car" in tr and "iracing-ir-val" in tr:
            row = re.search(r"</th>(.*)", tr, re.S)
            break
    if not row:
        sys.exit("ligne Sports Car introuvable")
    cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row.group(1), re.S)]
    if len(cells) < 5:
        sys.exit("colonnes manquantes: %r" % cells)
    data = {
        "source": URL,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sports_car": {
            "irating": num(cells[0]),
            "world_rank": num(cells[1]),
            "france_rank": num(cells[2]),
            "starts": num(cells[3]),
            "wins": num(cells[4]),
        },
    }
    sc = data["sports_car"]
    if not (1000 < sc["irating"] < 15000 and 0 < sc["france_rank"] <= sc["world_rank"] and sc["wins"] <= sc["starts"]):
        sys.exit("valeurs incohérentes: %r" % sc)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
