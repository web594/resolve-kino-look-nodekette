# -*- coding: utf-8 -*-
"""Vergleicht die freie Kette mit einer gekauften — in Zahlen statt nach Gefuehl.

Ablauf:
  1. `messtafel_erzeugen.py` legt eine synthetische Log-Messtafel an (keine Aufnahmen).
  2. Die Tafel wird in DaVinci Resolve mit der GEKAUFTEN Kette (Node 1 + Node 3)
     gegradet und als Standbild exportiert — das macht der Mensch bzw. ein Skript,
     dieses Werkzeug bekommt nur die fertige PNG.
  3. Die FREIE Kette wird hier direkt gerechnet (dieselben LUT-Formeln, die auch die
     .cube-Dateien erzeugen), inklusive Key-Ausgabe-Gain des Finish-Nodes.
  4. Ausgabe: Feld fuer Feld beide Ergebnisse und die Abweichung in Prozentpunkten.

Aufruf:
  py vergleich_messen.py --gekauft gekauft.png --felder messtafel_slog3_felder.json
  py vergleich_messen.py ... --markdown messwerte_tabelle.md
"""
import argparse
import json

import numpy as np
from PIL import Image

from lut_filmemulation_log_zu_rec709 import film, M_SGAMUT3CINE_ZU_709
from lut_finish_kinofarben import finish
from messtafel_erzeugen import linear_zu_slog3

M_709_ZU_SGAMUT3CINE = np.linalg.inv(M_SGAMUT3CINE_ZU_709)

KEY_GAIN_FINISH = 0.40      # Dosierung des Finish-Nodes, wie in der Kette empfohlen


def freie_kette(linear709):
    """Szenenlicht -> Node 1 (Filmemulation) -> Node 3 (Finish, gedrosselt)."""
    code = linear_zu_slog3(np.asarray(linear709) @ M_709_ZU_SGAMUT3CINE.T)
    return finish(film(code, "slog3"), KEY_GAIN_FINISH)


def messen(bild, lage, kachel_rand=10):
    hoehe, breite = bild.shape[:2]
    werte = {}
    for name, (x, y) in lage.items():
        px = int(round(x * breite / 720.0))
        py = int(round(y * hoehe / 360.0))
        blk = bild[py - kachel_rand:py + kachel_rand,
                   px - kachel_rand:px + kachel_rand].reshape(-1, 3)
        werte[name] = blk.mean(0)
    return werte


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gekauft", required=True, help="Standbild der gekauften Kette (PNG)")
    p.add_argument("--felder", required=True, help="JSON aus messtafel_erzeugen.py")
    p.add_argument("--markdown", default=None)
    a = p.parse_args()

    daten = json.load(open(a.felder, encoding="utf-8"))
    bild = np.asarray(Image.open(a.gekauft).convert("RGB"), dtype=np.float64) / 255.0
    gekauft = messen(bild, daten["lage"])

    zeilen = []
    abweichungen = []
    for name, lin in daten["szene_linear"].items():
        g = gekauft[name]
        f = freie_kette(np.array([lin]))[0]
        d = (f - g) * 100.0
        abweichungen.append(np.abs(d))
        zeilen.append((name, g, f, d))

    kopf = f"| Feld | gekauft (R/G/B) | frei (R/G/B) | Abweichung in Prozentpunkten |"
    trenn = "|---|---|---|---|"
    text = [kopf, trenn]
    for name, g, f, d in zeilen:
        text.append(f"| {name} | {g[0]:.3f} / {g[1]:.3f} / {g[2]:.3f} "
                    f"| {f[0]:.3f} / {f[1]:.3f} / {f[2]:.3f} "
                    f"| {d[0]:+.1f} / {d[1]:+.1f} / {d[2]:+.1f} |")
    alle = np.array(abweichungen)
    text.append("")
    text.append(f"Mittlere absolute Abweichung: **{alle.mean():.1f} Prozentpunkte**, "
                f"groesste Einzelabweichung: **{alle.max():.1f}**.")
    ausgabe = "\n".join(text)
    print(ausgabe)
    if a.markdown:
        open(a.markdown, "w", encoding="utf-8").write(ausgabe + "\n")
        print("\ngeschrieben:", a.markdown)


if __name__ == "__main__":
    main()
