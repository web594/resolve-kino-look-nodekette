# -*- coding: utf-8 -*-
"""Erzeugt die LUT fuer Node 1 der Kette — die freie Filmemulation.

Node 1 macht zwei Dinge in einem Schritt: er dekodiert das Log-Signal der Kamera und
gibt ihm zugleich die Kennlinie eines Kinofilms. Ein gekauftes Werkzeug erledigt das
mit gemessenen Kameraprofilen und gescannten Filmemulsionen. Dieses Skript rechnet
denselben Weg aus dem Modell nach — ohne fremde Messdaten:

  Kamera-Log  ->  Szenenlicht (linear)
              ->  NEGATIV: Dichtekurve je Schicht (Fuss, gerader Teil, Schulter)
              ->  Kopplung zwischen den Schichten (Farbcharakter des Materials)
              ->  KOPIERFILM: zweite, steilere Dichtekurve
              ->  Durchlaessigkeit  ->  Rec.709

Daraus ergibt sich von selbst, was einen Film-Look ausmacht: Schwarz laeuft nie ganz
zu (Fuss der Kurve), Lichter brennen nicht hart aus (Schulter), der Kontrast entsteht
im Kopierfilm, und die Farben verschieben sich in den Extremen leicht gegeneinander.

Eingangsformate:
    slog3     Sony S-Log3 / S-Gamut3.Cine   (Log-Kameras)
    rec709    Rec.709 Gamma 2.4             (Kameras ohne Log-Profil)

Kein Nachbau eines bestimmten kommerziellen Produkts: die Kurven stammen aus dem
Modell, nicht aus fremden LUT- oder Scandaten.

Voraussetzung:  py -m pip install numpy colour-science
Aufruf:         py lut_filmemulation_log_zu_rec709.py [--out-dir <ordner>] [--size 33]
                py lut_filmemulation_log_zu_rec709.py --kontrolle
"""
import argparse
import os

import numpy as np
import colour


# ---------------------------------------------------------------- Eingangsseite
def slog3_zu_linear(x):
    """Sony S-Log3 (0..1 Code) -> Szenenlicht relativ (18-%-Grau = 0,18)."""
    x = np.asarray(x, dtype=np.float64)
    grenze = 171.2102946929 / 1023.0
    hoch = (10.0 ** ((x * 1023.0 - 420.0) / 261.5)) * (0.18 + 0.01) - 0.01
    tief = (x * 1023.0 - 95.0) * 0.01125000 / (171.2102946929 - 95.0)
    return np.where(x >= grenze, hoch, tief)


# S-Gamut3.Cine -> Rec.709 (beide D65, Bradford-Anpassung).
# Zeilensummen sind exakt 1 — Grau bleibt Grau.
M_SGAMUT3CINE_ZU_709 = np.array([
    [1.62694741, -0.54013854, -0.08680887],
    [-0.17851553, 1.41794093, -0.23942540],
    [-0.04443611, -0.19591997, 1.24035608],
])

# Rec.709-Eingang: Anzeigesignal zurueck ins Szenenlicht. Unterhalb Mittelgrau
# reicht Gamma 2,4; oberhalb wird exponentiell auf rund 4 Blenden ueber Grau
# geoeffnet, damit auch Rec.709-Material die Schulter des Films erreicht.
# Ohne diese Streckung endet Weiss bei etwa 0,58 statt 0,93.
_A = 4.8            # aus der Steigung bei 0,5 (stetig differenzierbar)
_B = 7.04           # so gewaehlt, dass 1,0 -> 64-fach Grau (6 Blenden);
#                     ergibt Weiss bei 0,88 — bei 4 Blenden waeren es nur 0,75


def rec709_zu_linear(x):
    """Rec.709 Gamma 2.4 (Anzeige) -> Szenenlicht, 18-%-Grau bleibt 0,18."""
    x = np.clip(np.asarray(x, dtype=np.float64), 0, 1)
    unten = 0.18 * (np.clip(x, 1e-6, None) / 0.5) ** 2.4
    d = x - 0.5
    oben = 0.18 * np.exp(_A * d + _B * d * d)
    return np.where(x <= 0.5, unten, oben)


EINGAENGE = {
    "slog3": lambda rgb: np.clip(slog3_zu_linear(rgb) @ M_SGAMUT3CINE_ZU_709.T, 1e-6, None),
    "rec709": lambda rgb: np.clip(rec709_zu_linear(rgb), 1e-6, None),
}


# ------------------------------------------------------------------- Filmmodell
def weich_ab(u, weichheit):
    """Weiche untere Begrenzung bei 0 (Fuss der Kurve) — Softplus."""
    return weichheit * np.logaddexp(0.0, u / weichheit)


def weich_auf(u, grenze, weichheit):
    """Weiche obere Begrenzung bei 'grenze' (Schulter der Kurve)."""
    return grenze - weich_ab(grenze - u, weichheit)


# Negativ: Steilheit je Schicht leicht unterschiedlich — daher der typische
# Farbversatz zwischen Schatten und Lichtern, an dem man Film erkennt.
GAMMA_NEG = 0.7387 * np.array([0.98, 1.00, 1.02])
DICHTE_MAX = 2.3756 * np.array([0.99, 1.00, 1.01])
FUSS = 0.6943
SCHULTER = 0.7334

# Kopplung/Maskierung zwischen den Schichten. Zeilen = Ergebnis, Spalten = Quelle.
KOPPLUNG = np.array([
    [1.000, -0.055, -0.015],
    [-0.045, 1.000, -0.040],
    [-0.010, -0.060, 1.000],
])

# Kopierfilm
GAMMA_PRINT = 4.95              # Steilheit des Kopierfilms
DICHTE_PRINT_MAX = 3.6445
FUSS_PRINT = 0.85
SCHULTER_PRINT = 0.2553
DICHTE_BEZUG = 1.1928           # Belichtung der Kopie (Kopierlicht)

# Kinokopien laufen in den Lichtern leicht ins Warme. 0 = neutral.
WAERME_LICHTER = 0.015

# Belichtungsvorhalt in Blenden. Das reine Kopierfilm-Modell legt 18-%-Grau auf 0,30 —
# das ist der Dichtewert einer Kinokopie, im Video-Rec.709 aber deutlich zu dunkel.
# 1,75 Blenden heben 18-%-Grau auf rund 0,49 — der Wert, den auch gaengige
# Kameraprofile ausgeben, und er passt zum Ziel "hell und freundlich".
# Wer es dunkler und kontrastreicher mag, geht auf 1,0 bis 1,2.
#
# BELICHTUNG_BLENDEN, GAMMA_PRINT und FUSS_PRINT sind gemeinsam per Rasterabgleich
# auf einen Standard-Graukeil eingestellt (Zielwerte fuer einen Rec.709-Filmlook:
# -3 Blenden 0,10 | 18-%-Grau 0,48 | +1 Blende 0,67 | 90-%-Weiss 0,85 | +3 Blenden 0,91).
# Restabweichung 0,4 Prozentpunkte im Mittel.
BELICHTUNG_BLENDEN = 1.75


def _roh(linear):
    """Reiner Filmprozess ohne Neutral-Abgleich. Eingang: Szenenlicht."""
    log_e = np.log10(np.clip(linear * 2.0 ** BELICHTUNG_BLENDEN, 1e-6, None))

    dichte = weich_auf(weich_ab(GAMMA_NEG * (log_e + 2.0), FUSS), DICHTE_MAX, SCHULTER)
    dichte = dichte @ KOPPLUNG.T

    v = GAMMA_PRINT * (DICHTE_BEZUG - dichte)
    dichte_print = weich_auf(weich_ab(v, FUSS_PRINT), DICHTE_PRINT_MAX, SCHULTER_PRINT)

    weiss = 10.0 ** (-weich_ab(GAMMA_PRINT * (DICHTE_BEZUG - DICHTE_MAX.mean()), FUSS_PRINT))
    rgb = np.clip(10.0 ** (-dichte_print) / weiss, 0, 1)
    return np.clip(colour.models.eotf_inverse_BT1886(rgb, L_B=0.0, L_W=1.0), 0, 1)


# Neutral-Abgleich ("Kopierlicht"): unterschiedliche Steilheit der Schichten wuerde
# einen grauen Keil einfaerben. Der Abgleich zieht Rot und Blau auf den Gruenkanal —
# Grau bleibt Grau, farbige Bildstellen behalten ihren Filmcharakter.
_STUETZ = np.linspace(-4.0, 2.6, 513)   # deckt den ganzen Belichtungsumfang ab
_GRAU_LIN = 0.18 * 10.0 ** _STUETZ
_GRAU = _roh(np.stack([_GRAU_LIN] * 3, 1))


def film(rgb, eingang="slog3"):
    """Kamerasignal (0..1) -> Rec.709 (0..1) ueber Negativ + Kopierfilm."""
    aus = _roh(EINGAENGE[eingang](np.asarray(rgb, dtype=np.float64)))
    ergebnis = aus.copy()
    for k in (0, 2):
        x, y = _GRAU[:, k], _GRAU[:, 1]
        reihe = np.argsort(x)
        ergebnis[..., k] = np.interp(aus[..., k], x[reihe], y[reihe])
    if WAERME_LICHTER:
        luma = (0.2126 * ergebnis[..., 0] + 0.7152 * ergebnis[..., 1]
                + 0.0722 * ergebnis[..., 2])
        oben = np.clip((luma - 0.45) / 0.55, 0, 1) ** 2
        ergebnis[..., 0] += WAERME_LICHTER * oben
        ergebnis[..., 2] -= WAERME_LICHTER * oben
    return np.clip(ergebnis, 0, 1)


# ----------------------------------------------------------------- .cube-Ausgabe
def cube_schreiben(pfad, funktion, titel, n, quelle):
    g = np.linspace(0, 1, n)
    R, G, B = np.meshgrid(g, g, g, indexing="ij")
    # .cube-Schreibreihenfolge: Rot variiert am schnellsten
    gitter = np.stack([R, G, B], -1).transpose(2, 1, 0, 3).reshape(-1, 3).astype(np.float64)
    werte = np.clip(funktion(gitter), 0, 1)
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(f"# {titel}\n# Erzeugt von {quelle}\nLUT_3D_SIZE {n}\n")
        for v in werte:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    print("geschrieben:", pfad)


def kontrolle():
    """Kennwerte ausgeben — zum Nachpruefen nach Parameteraenderungen."""
    for eingang, grau in (("slog3", 0.4128), ("rec709", 0.5)):
        g = np.linspace(0, 1, 11)
        aus = film(np.stack([g, g, g], 1), eingang)
        print(f"\n--- {eingang} ---")
        print(" ein  | Rec.709 aus (R/G/B)")
        for k in range(11):
            print(f"  {g[k]:.2f}   {aus[k,0]:.4f} {aus[k,1]:.4f} {aus[k,2]:.4f}")
        m = film(np.array([[grau] * 3]), eingang)
        print(f"18-%-Grau ({grau}) -> {m[0,1]:.4f}   (Zielbereich 0,46-0,50)")
        print(f"Schwarz -> {aus[0,1]:.4f}  (Filmschwarz, soll nicht 0 sein)")
        print(f"Weiss   -> {aus[-1,1]:.4f}  (soll unter 1,0 bleiben)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=".")
    p.add_argument("--size", type=int, default=33)
    p.add_argument("--kontrolle", action="store_true")
    a = p.parse_args()
    if a.kontrolle:
        kontrolle()
        return
    os.makedirs(a.out_dir, exist_ok=True)
    for eingang, name in (("slog3", "Filmemulation_SLog3_zu_Rec709"),
                          ("rec709", "Filmemulation_Rec709_zu_Rec709")):
        cube_schreiben(
            os.path.join(a.out_dir, name + ".cube"),
            lambda rgb, e=eingang: film(rgb, e),
            f"Filmemulation Negativ + Kopierfilm ({eingang} -> Rec.709), frei gerechnet",
            a.size, os.path.basename(__file__))


if __name__ == "__main__":
    main()
