# -*- coding: utf-8 -*-
"""Erzeugt eine synthetische Messtafel in Kamera-Log — Grundlage jedes Vergleichs.

Die Tafel enthaelt keine Aufnahmen, sondern gerechnete Farbfelder: einen Graukeil
ueber neun Blenden und typische Motivfarben (Hauttoene, Himmel, Pflanzen, Holz,
Stoff, Bunt). Damit laesst sich jede Look-Kette in Zahlen vergleichen, ohne dass
Bildmaterial aus einer echten Produktion noetig waere.

Die Felder werden als Szenenlicht angegeben (18-%-Grau = 0,18) und in
S-Log3/S-Gamut3.Cine kodiert — also genau das, was eine Log-Kamera liefern wuerde.

Aufruf:  py messtafel_erzeugen.py [--out messtafel_slog3.png] [--felder felder.json]
"""
import argparse
import json
import os

import numpy as np

from lut_filmemulation_log_zu_rec709 import M_SGAMUT3CINE_ZU_709


# Szenenlicht in Rec.709-Primaervalenzen (linear, 18-%-Grau = 0,18).
FELDER = {
    "Grau -3 Blenden": [0.0225, 0.0225, 0.0225],
    "Grau -2 Blenden": [0.045, 0.045, 0.045],
    "Grau -1 Blende": [0.09, 0.09, 0.09],
    "Grau 18 %": [0.18, 0.18, 0.18],
    "Grau +1 Blende": [0.36, 0.36, 0.36],
    "Grau +2 Blenden": [0.72, 0.72, 0.72],
    "Grau +3 Blenden": [1.44, 1.44, 1.44],
    "Weiß 90 %": [0.90, 0.90, 0.90],
    "Haut hell": [0.380, 0.246, 0.190],
    "Haut mittel": [0.240, 0.140, 0.104],
    "Haut dunkel": [0.100, 0.055, 0.040],
    "Lippen": [0.230, 0.070, 0.070],
    "Himmel": [0.110, 0.170, 0.330],
    "Pflanze": [0.055, 0.130, 0.045],
    "Holz warm": [0.200, 0.110, 0.050],
    "Stoff blau": [0.040, 0.060, 0.170],
    "Rot kräftig": [0.320, 0.040, 0.035],
    "Gelb": [0.420, 0.330, 0.060],
}

M_709_ZU_SGAMUT3CINE = np.linalg.inv(M_SGAMUT3CINE_ZU_709)


def linear_zu_slog3(x):
    """Szenenlicht -> S-Log3-Code 0..1 (Umkehrung der Sony-Formel)."""
    x = np.asarray(x, dtype=np.float64)
    grenze = 0.01125000
    hoch = (420.0 + np.log10((np.clip(x, 1e-9, None) + 0.01) / (0.18 + 0.01)) * 261.5) / 1023.0
    tief = (x * (171.2102946929 - 95.0) / 0.01125000 + 95.0) / 1023.0
    return np.clip(np.where(x >= grenze, hoch, tief), 0, 1)


def tafel(felder=None, kachel=120, spalten=6):
    felder = felder or FELDER
    namen = list(felder)
    zeilen = (len(namen) + spalten - 1) // spalten
    bild = np.zeros((zeilen * kachel, spalten * kachel, 3), dtype=np.float64)
    lage = {}
    for i, name in enumerate(namen):
        lin709 = np.array(felder[name], dtype=np.float64)
        code = linear_zu_slog3(lin709 @ M_709_ZU_SGAMUT3CINE.T)
        z, s = divmod(i, spalten)
        bild[z * kachel:(z + 1) * kachel, s * kachel:(s + 1) * kachel] = code
        lage[name] = [s * kachel + kachel // 2, z * kachel + kachel // 2]
    return bild, lage


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="messtafel_slog3.png")
    p.add_argument("--felder", default=None, help="JSON mit den Feldmitten zum Nachmessen")
    p.add_argument("--kachel", type=int, default=120)
    a = p.parse_args()

    from PIL import Image
    bild, lage = tafel(kachel=a.kachel)
    # 8 Bit reicht: die Felder sind grosse einfarbige Flaechen, und der
    # Standbild-Export aus Resolve liefert ohnehin 8 Bit je Kanal.
    Image.fromarray((np.clip(bild, 0, 1) * 255 + 0.5).astype(np.uint8)).save(a.out)
    print("geschrieben:", a.out, bild.shape)

    ziel = a.felder or os.path.splitext(a.out)[0] + "_felder.json"
    json.dump({"lage": lage, "szene_linear": FELDER}, open(ziel, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("geschrieben:", ziel)


if __name__ == "__main__":
    main()
