# -*- coding: utf-8 -*-
"""Legt die 4-Node-Kette auf die Clips — per Skript statt per Maus.

Eine .drx traegt die komplette Kette: Nodes, Reihenfolge, Beschriftungen, LUT-Zuweisung,
OFX-Plugins mit allen Parametern und die Reglerwerte. Das Uebertragen dauert Sekunden;
dieselbe Kette von Hand nachzubauen dauert je Clip viele Minuten und wird ungenau.

Zwei Varianten:
    (Standard)  gekaufte Werkzeuge — Node 1 Filmemulations-Plugin, Node 3 gekaufte Finish-LUT
    --frei      nur Bordmittel     — Node 1 und 3 als selbst gerechnete LUTs

Aufruf:
    py look_anwenden.py                                   # alle Timelines mit "import"
    py look_anwenden.py --timeline nah --timeline weit
    py look_anwenden.py --frei
    py look_anwenden.py --nur-einstellungen                # nur die Projekt-Farbeinstellungen
    py look_anwenden.py --gruppe "Kino-Look"               # Clips zusaetzlich einer Farbgruppe zuordnen

Vorher einmal `py luts_installieren.py` laufen lassen, sonst findet Resolve die LUTs nicht.
"""
import argparse
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
VORLAGEN = os.path.join(os.path.dirname(HIER), "vorlagen")

# Projekt-Farbeinstellungen. Die Filmemulation in Node 1 erwartet unveraenderte
# Kamerapixel — unter Color Management wuerde Resolve das Bild vorher umrechnen
# und der Look kippt. Deshalb DaVinci YRGB.
EINSTELLUNGEN = {
    "colorScienceMode": "davinciYRGB",
    "colorSpaceTimeline": "Rec.709 (Scene)",
    "colorSpaceOutput": "Rec.709 (Scene)",
    "colorSpaceInput": "Rec.709 Gamma 2.4",
    "inputDRT": "None",
    "outputDRT": "None",
}


def resolve_holen():
    sys.path.append(os.path.join(
        os.environ.get("RESOLVE_SCRIPT_API",
                       r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
        "Modules"))
    import DaVinciResolveScript as dvr
    r = dvr.scriptapp("Resolve")
    if r is None:
        sys.exit("Resolve nicht erreichbar — laeuft es, und ist die Skript-Schnittstelle an?")
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--drx", default=None)
    p.add_argument("--frei", action="store_true",
                   help="Variante ohne gekaufte Werkzeuge")
    p.add_argument("--timeline", action="append", default=[],
                   help="Namensfragment; mehrfach moeglich (Standard: alle mit 'import')")
    p.add_argument("--gruppe", default=None, help="Clips dieser Farbgruppe zuordnen")
    p.add_argument("--nur-einstellungen", action="store_true")
    a = p.parse_args()

    drx = a.drx or os.path.join(
        VORLAGEN, "kino_look_4nodes_frei_v1.drx" if a.frei else "kino_look_4nodes_v1.drx")
    if not os.path.exists(drx):
        sys.exit(f"Vorlage fehlt: {drx}")

    resolve = resolve_holen()
    projekt = resolve.GetProjectManager().GetCurrentProject()
    resolve.OpenPage("color")

    for schluessel, wert in EINSTELLUNGEN.items():
        ok = projekt.SetSetting(schluessel, wert)
        print(f"  {schluessel:22} = {wert:22} {'ok' if ok else 'FEHLER'}")
    projekt.RefreshLUTList()
    if a.nur_einstellungen:
        print("\nNur Einstellungen gesetzt. LUT-Interpolation auf 'Tetraedrisch' bitte "
              "einmal von Hand — das geht nicht ueber die Schnittstelle.")
        return

    fragmente = [f.lower() for f in a.timeline] or ["import"]
    gruppe = None
    if a.gruppe:
        gruppe = next((g for g in projekt.GetColorGroupsList()
                       if g.GetName() == a.gruppe), None) or projekt.AddColorGroup(a.gruppe)

    gesamt = 0
    for i in range(1, projekt.GetTimelineCount() + 1):
        tl = projekt.GetTimelineByIndex(i)
        name = tl.GetName()
        if not any(f in name.lower() for f in fragmente):
            continue
        clips = tl.GetItemListInTrack("video", 1) or []
        gut = 0
        for clip in clips:
            if clip.GetNodeGraph().ApplyGradeFromDRX(os.path.abspath(drx), 0):
                gut += 1
            if gruppe:
                clip.AssignToColorGroup(gruppe)
        gesamt += gut
        print(f"  {name}: {gut}/{len(clips)} Clips")

    print(f"\nFertig — {gesamt} Clips. Vorlage: {os.path.basename(drx)}")
    print("Offen bleibt (nicht ueber die Schnittstelle moeglich):")
    print("  * LUT-Interpolation auf 'Tetraedrisch' stellen")
    print("  * Node 1, 3 und 4 zu echten geteilten Nodes verknuepfen")
    print("  * Node 2 einmessen — Weissabgleich und Helligkeit gehoeren zum Motiv")


if __name__ == "__main__":
    main()
