# -*- coding: utf-8 -*-
"""Erzeugt alle LUTs der freien Variante auf einen Schlag und legt sie in ./luts ab.

Es entstehen:
  Filmemulation_SLog3_zu_Rec709.cube    (Node 1, freier Ersatz fuer das gekaufte Filmwerkzeug)
  Filmemulation_Rec709_zu_Rec709.cube   (dasselbe fuer Kameras ohne Log-Profil)
  Finish_Kinofarben_Rec709.cube         (Node 3, freier Ersatz fuer die gekaufte Finish-LUT)

Node 2 (Weissabgleich/Helligkeit) und Node 4 (Film-Look-Erzeuger) brauchen keine LUT —
Node 2 sind Reglerwerte, Node 4 ist in DaVinci Resolve bereits enthalten.

Aufruf:  py luts_erzeugen.py [--out-dir <ordner>] [--size 33]
"""
import argparse
import os
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
STANDARD_ZIEL = os.path.join(os.path.dirname(HIER), "luts")


def lauf(skript, argumente):
    befehl = [sys.executable, os.path.join(HIER, skript)] + argumente
    print("\n>", " ".join(befehl))
    if subprocess.call(befehl) != 0:
        sys.exit(f"Abgebrochen bei {skript}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=STANDARD_ZIEL)
    p.add_argument("--size", type=int, default=33)
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    lauf("lut_filmemulation_log_zu_rec709.py", ["--size", str(a.size), "--out-dir", a.out_dir])
    lauf("lut_finish_kinofarben.py", ["--size", str(a.size), "--out-dir", a.out_dir])

    print("\nFertig. LUTs liegen in:", a.out_dir)
    print("Weiter mit:  py luts_installieren.py")


if __name__ == "__main__":
    main()
