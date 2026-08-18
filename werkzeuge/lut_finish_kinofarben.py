# -*- coding: utf-8 -*-
"""Erzeugt die LUT fuer Node 3 der Kette — den kreativen Finish.

Node 3 sitzt hinter der Filmemulation und macht aus einem korrekten Bild ein
gestaltetes. Ein gekaufter Finish-LUT-Satz liefert dafuer einen Katalog von
Handschriften. Dieses Skript rechnet eine davon aus dem Modell nach — die
zurueckhaltende, warme Kinohandschrift, die fuer Interviews und Vortraege passt:

  1. weiche Kontraktkurve um Mittelgrau, Lichter laufen weich aus
  2. Schwarz leicht angehoben (kein zulaufendes Schwarz)
  3. Gruen- und Cyantoene entsaettigt — Hintergrund, Pflanzen und Wandfarben
     werden ruhig, statt vom Gesicht abzulenken
  4. Rot leicht Richtung Orange gedreht und angehoben — Hauttoene bekommen Waerme
  5. Lichter warm, tiefe Schatten leicht kuehl (klassischer Kinofarbkontrast)
  6. Gesamtsaettigung leicht zurueck, damit der Farbkontrast nicht bunt wirkt

Kein Nachbau eines gekauften LUT-Satzes: es werden keine fremden LUT-Daten gelesen,
angepasst oder angenaehert. Die Kurven kommen aus den Parametern unten.

In der Kette wird die LUT bewusst NICHT voll aufgetragen — 35–45 % Key-Ausgabe-Gain
sind der bewaehrte Bereich. Wer lieber die volle LUT auftraegt, nimmt --staerke 0.4.

Voraussetzung:  py -m pip install numpy colour-science
Aufruf:         py lut_finish_kinofarben.py [--out-dir <ordner>] [--size 33]
                py lut_finish_kinofarben.py --kontrolle
"""
import argparse
import os

import numpy as np
import colour


# --- Tonwerte --------------------------------------------------------------
DREHPUNKT = 0.42          # Mittelgrau nach der Filmemulation
KONTRAST = 1.10           # sanft, die Emulation hat schon Kontrast gemacht
SCHWARZ_ANHEBUNG = 0.012  # Filmschwarz
LICHTER_ROLLOFF = 0.88    # ab hier weiche Schulter

# --- Farbe -----------------------------------------------------------------
# Farbtonbaender in Grad (0 = Rot, 120 = Gruen, 240 = Blau).
# (Mitte, Breite, Saettigungsfaktor, Drehung in Grad)
BAENDER = [
    (0.0,   45.0, 1.06, +8.0),    # Rot  -> Richtung Orange, etwas kraeftiger
    (30.0,  40.0, 1.02, +1.5),    # Orange/Haut -> nur eine Spur waermer
    (120.0, 70.0, 0.62, -6.0),    # Gruen -> deutlich ruhiger
    (180.0, 60.0, 0.75, -4.0),    # Cyan  -> ruhiger
    (240.0, 55.0, 0.92, -8.0),    # Blau  -> Richtung Cyan, leicht ruhiger
]

SAETTIGUNG_GESAMT = 0.96
LICHTER_WARM = np.array([+0.014, +0.002, -0.018])    # Offset in den Lichtern
SCHATTEN_KUEHL = np.array([-0.008, +0.002, +0.012])  # Offset in den Schatten


def weich(x):
    """Smoothstep — weiche 0..1-Ueberblendung ohne harte Kante."""
    return x * x * (3 - 2 * x)


def _tonwerte(rgb):
    x = (rgb - DREHPUNKT) * KONTRAST + DREHPUNKT
    # weiche Schulter statt hartem Abschneiden
    ueber = x > LICHTER_ROLLOFF
    rest = 1.0 - LICHTER_ROLLOFF
    x = np.where(ueber,
                 LICHTER_ROLLOFF + rest * np.tanh(np.clip(x - LICHTER_ROLLOFF, 0, None) / rest),
                 x)
    x = np.clip(x, 0, 1)
    return x * (1 - SCHWARZ_ANHEBUNG) + SCHWARZ_ANHEBUNG


def _band_gewicht(farbton_grad, mitte, breite):
    """Weiche Zugehoerigkeit eines Farbtons zu einem Band (zyklisch)."""
    d = np.abs((farbton_grad - mitte + 180.0) % 360.0 - 180.0)
    return weich(np.clip(1.0 - d / breite, 0, 1))


def finish(rgb, staerke=1.0):
    """Rec.709 -> Rec.709. staerke 0..1 mischt mit dem Eingang."""
    rgb = np.clip(np.asarray(rgb, dtype=np.float64), 0, 1)
    x = _tonwerte(rgb)

    hsv = colour.RGB_to_HSV(x)
    ton = hsv[..., 0] * 360.0
    sat_faktor = np.full(ton.shape, 1.0)
    drehung = np.zeros(ton.shape)
    for mitte, breite, faktor, dreh in BAENDER:
        w = _band_gewicht(ton, mitte, breite)
        sat_faktor = sat_faktor * (1.0 + w * (faktor - 1.0))
        drehung = drehung + w * dreh
    hsv[..., 0] = ((ton + drehung) % 360.0) / 360.0
    hsv[..., 1] = np.clip(hsv[..., 1] * sat_faktor * SAETTIGUNG_GESAMT, 0, 1)
    x = np.clip(colour.HSV_to_RGB(hsv), 0, 1)

    luma = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    # Die Faerbung laeuft an beiden Enden wieder aus: sonst bekaeme reines Schwarz
    # einen Blaustich und reines Weiss wuerde im Rotkanal anstossen.
    lichter = (weich(np.clip((luma - 0.55) / 0.40, 0, 1))
               * (1.0 - weich(np.clip((luma - 0.90) / 0.10, 0, 1))))
    schatten = (weich(np.clip(1.0 - luma / 0.35, 0, 1))
                * weich(np.clip(luma / 0.08, 0, 1)))
    x = np.clip(x + LICHTER_WARM * lichter + SCHATTEN_KUEHL * schatten, 0, 1)

    return np.clip(rgb + (x - rgb) * staerke, 0, 1)


def cube_schreiben(pfad, funktion, titel, n):
    g = np.linspace(0, 1, n)
    R, G, B = np.meshgrid(g, g, g, indexing="ij")
    # .cube-Schreibreihenfolge: Rot variiert am schnellsten
    gitter = np.stack([R, G, B], -1).transpose(2, 1, 0, 3).reshape(-1, 3).astype(np.float64)
    werte = np.clip(funktion(gitter), 0, 1)
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(f"# {titel}\n# Erzeugt von {os.path.basename(__file__)}\nLUT_3D_SIZE {n}\n")
        for v in werte:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    print("geschrieben:", pfad)


def kontrolle():
    g = np.linspace(0, 1, 11)
    aus = finish(np.stack([g, g, g], 1))
    print(" ein |  R      G      B")
    for i in range(11):
        print(f" {g[i]:.1f}  {aus[i,0]:.4f} {aus[i,1]:.4f} {aus[i,2]:.4f}")
    proben = np.array([[0.7, 0.2, 0.2], [0.2, 0.7, 0.2], [0.2, 0.2, 0.7], [0.6, 0.45, 0.35]])
    namen = ["Rot", "Gruen", "Blau", "Hautton"]
    for name, ein, raus in zip(namen, proben, finish(proben)):
        a, b = colour.RGB_to_HSV(ein), colour.RGB_to_HSV(raus)
        print(f"{name:8} Saettigung {a[1]:.3f}->{b[1]:.3f}   "
              f"Farbton {a[0]*360:5.1f}->{b[0]*360:5.1f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=".")
    p.add_argument("--size", type=int, default=33)
    p.add_argument("--staerke", type=float, default=1.0,
                   help="1.0 = volle LUT (Standard, Dosierung dann per Key-Gain im Node)")
    p.add_argument("--kontrolle", action="store_true")
    a = p.parse_args()
    if a.kontrolle:
        kontrolle()
        return
    os.makedirs(a.out_dir, exist_ok=True)
    zusatz = "" if a.staerke == 1.0 else f"_{int(a.staerke*100)}prozent"
    cube_schreiben(os.path.join(a.out_dir, f"Finish_Kinofarben_Rec709{zusatz}.cube"),
                   lambda rgb: finish(rgb, a.staerke),
                   "Finish: warme Hauttoene, ruhige Gruentoene, weiche Lichter "
                   "(Rec.709 -> Rec.709), frei gerechnet", a.size)


if __name__ == "__main__":
    main()
