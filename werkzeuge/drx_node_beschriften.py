# -*- coding: utf-8 -*-
"""Beschriftet die Nodes einer .drx-Grade-Vorlage.

Resolves Skript-Schnittstelle kennt kein `SetNodeLabel` — Node-Beschriftungen gingen
bisher nur per Doppelklick in der Oberflaeche. In der .drx stehen sie aber als
Klartext (Feld 6 des Node-Containers), und von dort kommen sie beim Anwenden der
Vorlage in jedes Projekt mit. Eine beschriftete Kette ist kein Luxus: sie sagt beim
spaeteren Oeffnen sofort, welcher Node wofuer da ist.

Aufruf:
    py drx_node_beschriften.py <ein.drx> <aus.drx> "Erster" "Zweiter" "Dritter" ...
        (der Reihe nach, ein Text je Node — leerer Text laesst den Node unveraendert)
    py drx_node_beschriften.py <ein.drx> --liste
"""
import os
import sys

_HIER = os.path.dirname(os.path.abspath(__file__))
for _k in (os.path.join(_HIER, "..", "lib"),
           os.environ.get("RESOLVE_CTL") or ""):
    _k = os.path.abspath(_k)
    if os.path.exists(os.path.join(_k, "drxlib.py")):
        sys.path.insert(0, _k)
        break
else:
    sys.exit("drxlib.py nicht gefunden — lib/ mitliefern oder RESOLVE_CTL setzen.")

from drxlib import Drx, pb_parse, pb_ser, PbField        # noqa: E402
from drx_node_entfernen import _feld, nodes_auflisten     # noqa: E402


def beschriften(top, texte):
    knoten = [f for f in top.sub if f.fn == 7 and f.sub]
    for f, text in zip(knoten, texte):
        if not text:
            continue
        sechs = _feld(f, 6)
        if sechs is None:
            stelle = max((i for i, c in enumerate(f.sub) if c.fn < 6), default=0) + 1
            f.sub.insert(stelle, PbField(6, 2, text.encode("utf-8")))
        else:
            sechs.val = text.encode("utf-8")
            sechs.sub = None
    return len(knoten)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = Drx(sys.argv[1])
    if "--liste" in sys.argv:
        for i, (_, data) in enumerate(d.bodies):
            if data:
                print(f"Body {i}:", nodes_auflisten(pb_parse(data)[0]))
        return

    aus, texte = sys.argv[2], sys.argv[3:]
    for i, (_, data) in enumerate(d.bodies):
        if not data:
            continue
        top = pb_parse(data)[0]
        if not any(f.fn == 7 for f in top.sub):
            continue
        beschriften(top, texte)
        d.bodies[i][1] = pb_ser([top])
        print(f"Body {i}:", nodes_auflisten(top))
    d.save(aus)
    print("geschrieben:", aus)


if __name__ == "__main__":
    main()
