# -*- coding: utf-8 -*-
"""Schreibt die vollstaendige Parametertabelle des Film-Look-Erzeugers (Node 4).

Warum das noetig ist: in einer .drx stehen **nur Nicht-Standardwerte**. Wer die Kette
nachbauen will, sieht dort also nur einen Teil und weiss nicht, worauf der Rest steht.
Dieses Werkzeug fuegt beides zusammen:

  * die im Grade gesetzten Werte — aus der .drx gelesen
  * alle uebrigen Parameter mit ihrem Plugin-Standard — direkt aus dem OFX-Beschreiber

Den Beschreiber liefert Resolve selbst: das Plugin wird als Fusion-Werkzeug
(`ofx.com.blackmagicdesign.resolvefx.FilmLook`) in einer leeren Komposition angelegt und
seine Eingaenge werden ausgelesen. Dabei kommen auch die deutschen Beschriftungen mit,
sodass die Tabelle zu dem passt, was im Bedienfeld steht. Resolve muss dafuer laufen;
die Komposition wird sofort wieder geschlossen und beruehrt kein Projekt.

Aufruf:
    py flc_tabelle_erzeugen.py --drx ../vorlagen/kino_look_4nodes_v1.drx \
                               --out ../referenzen/film-look-erzeuger.md
    py flc_tabelle_erzeugen.py --drx ... --beschreiber flc.json --out ...   # ohne Resolve
"""
import argparse
import json
import os
import sys

_HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HIER)
for _k in (os.path.join(_HIER, "..", "lib"),
           os.environ.get("RESOLVE_CTL") or ""):
    _k = os.path.abspath(_k)
    if os.path.exists(os.path.join(_k, "drxlib.py")):
        sys.path.insert(0, _k)
        break

from drxlib import Drx, pb_parse            # noqa: E402
from drx_werte import ofx                   # noqa: E402

PLUGIN = "com.blackmagicdesign.resolvefx.filmlook"
WERKZEUG_ID = "ofx.com.blackmagicdesign.resolvefx.FilmLook"

# Nur die Parameter des Plugins selbst — Fusion haengt jedem Werkzeug noch
# Maske, Bewegungsunschaerfe, Ebenen und Renderskripte an, die es auf der
# Farbseite gar nicht gibt.
VON, BIS = "globalPreset", "resolvefxVersion"

GRUPPEN = [
    ("globalPreset", "Grundeinstellung"),
    ("filmLookGroup", "Film-Look"),
    ("colorGroup", "Farbeinstellungen"),
    ("splitGroup", "Teiltonung"),
    ("vignetteGroup", "Vignette"),
    ("halationGroup", "Lichthof"),
    ("bloomGroup", "Bloom"),
    ("grainGroup", "Filmkorn"),
    ("flickerGroup", "Flimmern"),
    ("gateWeaveGroup", "Bildfenster-Weave"),
    ("filmGateGroup", "Bildfenster"),
    ("flPreSat", "Innere Werte des Kern-Looks (kein Bedienfeld)"),
]


def beschreiber_aus_resolve():
    sys.path.append(os.path.join(
        os.environ.get("RESOLVE_SCRIPT_API",
                       r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
        "Modules"))
    import DaVinciResolveScript as dvr
    fusion = dvr.scriptapp("Resolve").Fusion()
    comp = fusion.NewComp()
    werkzeug = comp.AddTool(WERKZEUG_ID)
    if not werkzeug:
        comp.Close()
        raise SystemExit("Film-Look-Erzeuger nicht gefunden — Resolve Studio noetig?")
    liste = werkzeug.GetInputList()
    raus = []
    for i in sorted(liste.keys()):
        a = liste[i].GetAttrs()
        pid = a.get("INPS_ID")
        raus.append({"id": pid, "name": a.get("INPS_Name"),
                     "typ": a.get("INPS_DataType"),
                     "default": werkzeug.GetInput(pid)})
    comp.Close()
    return raus


def _zahl(x):
    if isinstance(x, float):
        return f"{x:.4g}"
    return str(x)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--drx", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--beschreiber", default=None,
                   help="JSON statt Resolve (Feld id/name/typ/default)")
    a = p.parse_args()

    baum = pb_parse(Drx(a.drx).bodies[0][1])
    plugins = ofx(baum)
    if PLUGIN not in plugins:
        raise SystemExit(f"{PLUGIN} ist in {a.drx} nicht enthalten.")
    gesetzt = {}
    for name, werte in plugins[PLUGIN]:
        gesetzt[name] = werte[0][1] if werte else None

    if a.beschreiber:
        beschr = json.load(open(a.beschreiber, encoding="utf-8"))
    else:
        beschr = beschreiber_aus_resolve()

    ids = [e["id"] for e in beschr]
    anfang, ende = ids.index(VON), ids.index(BIS)
    relevant = beschr[anfang:ende + 1]
    nach_id = {e["id"]: e for e in relevant}

    gruppen_start = {gid: titel for gid, titel in GRUPPEN}
    zeilen = ["# Node 4 — Film-Look-Erzeuger, alle Einstellungen", "",
              "Der Film-Look-Erzeuger (ResolveFX Film Look Creator) ist in DaVinci Resolve",
              "enthalten und kostet nichts extra. Er macht in dieser Kette den letzten Schliff:",
              "Lichthof um helle Kanten, Vignette, Teiltonung und die Saettigungskurven.", "",
              "**Wie diese Tabelle entstanden ist:** Werte in der Spalte *gesetzt* stehen so im",
              "Grade; alle uebrigen Parameter stehen auf Plugin-Standard, der direkt aus dem",
              "OFX-Beschreiber ausgelesen wurde. Neu erzeugen mit",
              "`py werkzeuge/flc_tabelle_erzeugen.py --drx <vorlage.drx> --out <datei.md>`.", "",
              f"Gesetzte Parameter: **{len([k for k in gesetzt if k in nach_id])}** von "
              f"**{len(relevant)}**.", ""]

    offen = None
    for e in relevant:
        if e["id"] in gruppen_start:
            if offen:
                zeilen.append("")
            zeilen.append(f"## {gruppen_start[e['id']]}")
            zeilen.append("")
            zeilen.append("| Parameter | Bedienfeld | Wert | Quelle |")
            zeilen.append("|---|---|---|---|")
            offen = True
        if offen is None:
            continue
        wert = gesetzt.get(e["id"], e["default"])
        quelle = "**gesetzt**" if e["id"] in gesetzt else "Standard"
        name = (e["name"] or "").strip()
        zeilen.append(f"| `{e['id']}` | {name} | {_zahl(wert)} | {quelle} |")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(zeilen) + "\n")
    print("geschrieben:", a.out)


if __name__ == "__main__":
    main()
