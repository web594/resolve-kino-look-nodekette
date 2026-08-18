# -*- coding: utf-8 -*-
"""Entfernt Herkunftsspuren aus einer .drx, bevor sie weitergegeben wird.

Eine Grade-Vorlage aus Resolve führt im XML-Kopf mehr mit, als man erwartet: den Namen
der Timeline, aus der sie gesichert wurde, den Pfad der Galerie auf dem eigenen Rechner,
Zeitcodes und Erstellungszeitpunkt. Für den Look ist davon nichts nötig — für eine
Veröffentlichung ist es alles zu viel.

Ersetzt/leert diese Felder und lässt den eigentlichen Grade (die `<Body>`-Blöcke)
unangetastet.

Aufruf:
    py drx_anonymisieren.py <datei.drx> [weitere.drx ...] [--hinweis "Kino-Look Vorlage"]
    py drx_anonymisieren.py <datei.drx> --pruefen        # nur anzeigen, nichts ändern
"""
import argparse
import glob
import re

# Feld -> neuer Inhalt (None = Feld leeren)
FELDER = {
    "SrcHint": "Vorlage",
    "GalleryPath": "",
    "RecTC": "00:00:00:00",
    "SrcTC": "00:00:00:00",
    "CreateTime": "",
}

# Kennungen, die auf den Ursprungsrechner zurückführen könnten
KENNUNGEN = ["DbId"]


def anonymisieren(text, hinweis):
    felder = dict(FELDER, SrcHint=hinweis)
    for feld, wert in felder.items():
        text = re.sub(rf"<{feld}>.*?</{feld}>", f"<{feld}>{wert}</{feld}>", text, flags=re.S)
        text = re.sub(rf"<{feld}/>", f"<{feld}>{wert}</{feld}>", text)
    return text


def fundstellen(text):
    treffer = []
    for feld in FELDER:
        for m in re.finditer(rf"<{feld}>(.*?)</{feld}>", text, re.S):
            if m.group(1).strip():
                treffer.append((feld, m.group(1).strip()))
    for kennung in KENNUNGEN:
        treffer += [(kennung, m) for m in re.findall(rf'{kennung}="([^"]+)"', text)]
    return treffer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dateien", nargs="+")
    p.add_argument("--hinweis", default="Vorlage")
    p.add_argument("--pruefen", action="store_true")
    a = p.parse_args()

    for muster in a.dateien:
        for pfad in sorted(glob.glob(muster)) or [muster]:
            text = open(pfad, encoding="utf-8", errors="ignore").read()
            if a.pruefen:
                print(f"\n{pfad}")
                for feld, wert in fundstellen(text):
                    print(f"   {feld}: {wert[:70]}")
                continue
            neu = anonymisieren(text, a.hinweis)
            open(pfad, "w", encoding="utf-8", newline="\n").write(neu)
            print("bereinigt:", pfad)
    if not a.pruefen:
        print("\nHinweis: die zufälligen DbId-Kennungen bleiben stehen — sie sind je "
              "Standbild neu gewürfelt und führen zu keinem Projekt zurück.")


if __name__ == "__main__":
    main()
