# -*- coding: utf-8 -*-
"""Sucht vor dem Veröffentlichen nach Projekt-, Kunden- und Rechnerdaten.

Durchsucht alle Dateien des Repos — auch Binärdateien wie `.drx`, `.cube` und den
Textinhalt der PDF-Folien — nach Mustern, die nichts in einem öffentlichen Repo zu
suchen haben: Datumscodes von Drehs, lokale Pfade, Laufwerksbuchstaben, Benutzernamen,
E-Mail-Adressen und frei angebbare Namen.

Aufruf:
    py veroeffentlichung_pruefen.py [--wurzel <ordner>] [--name "Nachname" ...]
"""
import argparse
import os
import re
import sys
import zlib

MUSTER = [
    # Datumscode wie 260806 — aber nicht mitten in einer Kommazahl (LUT-Dateien) und
    # nicht in den Hex-Blöcken einer .drx; deshalb dürfen ringsum keine Hexziffern stehen.
    (r"(?<![0-9a-f.])2[0-9]{5}(?![0-9a-f.])", "Datumscode eines Drehs (JJMMTT)"),
    (r"[A-Za-z]:[\\/](?:Users|Vid|claude|Program Files)", "lokaler Pfad"),
    (r"\\Users\\[A-Za-z0-9_.-]+", "Benutzerordner"),
    (r"[A-Za-z0-9._%+-]+@(?!wunder-media\.de)[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "fremde E-Mail"),
    (r"\b(?:E|F|G|H):\\", "Laufwerk mit Rohdaten"),
]

# Kein Fehler, nur zum Durchsehen: Produktnamen duerfen genannt werden (sie stehen
# in der Beschreibung der Kette und als Suchwort im Skill), Produktdaten nicht.
HINWEISE = [
    (r"VisionColor|OSIRIS|PRISMO|FilmConvert|Nitrate", "Name eines gekauften Produkts"),
]

UEBERSPRINGEN = {".git", "__pycache__", ".venv"}


def text_aus_pdf(pfad):
    """Grobe Textextraktion: alle Stream-Objekte entpacken und Klartext einsammeln."""
    roh = open(pfad, "rb").read()
    stuecke = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", roh, re.S):
        d = m.group(1)
        try:
            d = zlib.decompress(d)
        except Exception:
            pass
        stuecke.append(d)
    alles = b"\n".join(stuecke)
    # Text in PDF-Operatoren steht in runden Klammern vor Tj/TJ
    return b" ".join(re.findall(rb"\((?:[^()\\]|\\.)*\)", alles)).decode("latin-1")


def inhalt(pfad):
    if pfad.lower().endswith(".pdf"):
        return text_aus_pdf(pfad)
    roh = open(pfad, "rb").read()
    return roh.decode("utf-8", "ignore") + "\n" + roh.decode("latin-1", "ignore")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--wurzel", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    p.add_argument("--name", action="append", default=[],
                   help="zusätzlicher Eigenname, der nicht vorkommen darf")
    a = p.parse_args()

    muster = [(re.compile(r, re.I), t, True) for r, t in MUSTER]
    muster += [(re.compile(re.escape(n), re.I), "Eigenname", True) for n in a.name]
    muster += [(re.compile(r, re.I), t, False) for r, t in HINWEISE]

    treffer = 0
    geprueft = 0
    for ordner, unter, dateien in os.walk(a.wurzel):
        unter[:] = [u for u in unter if u not in UEBERSPRINGEN]
        for d in sorted(dateien):
            pfad = os.path.join(ordner, d)
            rel = os.path.relpath(pfad, a.wurzel)
            if os.path.basename(__file__) == d:
                continue
            geprueft += 1
            try:
                text = inhalt(pfad)
            except Exception as e:
                print(f"  ? {rel}: nicht lesbar ({e})")
                continue
            gesehen = set()
            for regex, was, ist_fehler in muster:
                for m in regex.finditer(text):
                    if (was, m.group(0)) in gesehen:
                        continue
                    gesehen.add((was, m.group(0)))
                    umfeld = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
                    print(f"  {'!' if ist_fehler else 'i'} {rel}: {was} — …{umfeld}…")
                    treffer += 1 if ist_fehler else 0

    print(f"\n{geprueft} Dateien geprüft, {treffer} Fundstellen.")
    print("Sauber." if not treffer else "Bitte einzeln durchsehen.")
    return 1 if treffer else 0


if __name__ == "__main__":
    sys.exit(main())
