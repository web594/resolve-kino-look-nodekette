# -*- coding: utf-8 -*-
"""Stellt einer .drx-Grade-Vorlage eine Kopie eines vorhandenen Nodes voran.

Wozu: Resolves Skript-Schnittstelle kann keine Nodes anlegen und keine OFX-Plugins
setzen. Wer eine Kette ohne ein gekauftes Plugin bauen will, braucht deshalb einen
Weg, einen zusaetzlichen LUT-Node an den Anfang zu bekommen — ohne Maus. Dieses
Werkzeug kopiert einen bestehenden Node (am besten einen einfachen LUT-Node) und
haengt die Kopie vor den ersten Node. Die LUT selbst wird danach in Resolve gesetzt
(`rctl.py lut 1 <datei.cube>`).

Aufruf:
    py drx_node_voranstellen.py <ein.drx> <aus.drx> --vorlage-id 4
    py drx_node_voranstellen.py <ein.drx> --liste

Aufbau der .drx siehe drx_node_entfernen.py.
"""
import copy
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

from drxlib import pb_parse, pb_ser, Drx, PbField        # noqa: E402
from drx_node_entfernen import _feld, nodes_auflisten, _quelle_setzen   # noqa: E402


def erster_node(top):
    """Der Node, in den der Quell-Anschluss (Feld 9) laeuft."""
    for f in top.sub:
        if f.fn == 9:
            inner = _feld(f, 3)
            baum = pb_parse(inner.val if inner.sub is None else pb_ser(inner.sub))
            for g in baum:
                if g.fn == 4:
                    return g.val
    ids = [n for n, _ in nodes_auflisten(top)]
    return min(ids) if ids else None


def voranstellen(top, vorlage_id, label=None):
    quelle = next((f for f in top.sub if f.fn == 7 and _feld(f, 1)
                   and _feld(f, 1).val == vorlage_id), None)
    if quelle is None:
        raise SystemExit(f"Node {vorlage_id} nicht gefunden.")

    neue_id = max(n for n, _ in nodes_auflisten(top)) + 1
    kopie = PbField(7, 2, None, pb_parse(pb_ser(quelle.sub)))
    _feld(kopie, 1).val = neue_id
    zwei = _feld(kopie, 2)
    if zwei is not None:
        zwei.val = 0                                   # ganz vorne in der Reihenfolge
    vier = _feld(kopie, 4)
    if vier is not None:
        vier.val = max(0, vier.val - 328)              # etwas nach links im Node-Fenster
    if label is not None:
        sechs = _feld(kopie, 6)
        if sechs is None:
            kopie.sub.append(PbField(6, 2, label.encode("utf-8")))
        else:
            sechs.val = label.encode("utf-8")

    alt_erster = erster_node(top)

    # Node-Container direkt vor den bisherigen ersten Node schreiben
    stelle = min(i for i, f in enumerate(top.sub) if f.fn == 7)
    top.sub.insert(stelle, kopie)

    # Quell-Anschluss auf die Kopie umbiegen und Kopie -> bisheriger erster Node
    for f in top.sub:
        if f.fn == 9:
            _quelle_setzen(f, neue_id)
    muster = next(f for f in top.sub if f.fn == 8 and f.sub)
    neue_verbindung = PbField(8, 2, None, pb_parse(pb_ser(muster.sub)))
    _feld(neue_verbindung, 1).val = neue_id
    _feld(neue_verbindung, 3).val = alt_erster
    top.sub.insert(top.sub.index(muster), neue_verbindung)

    for nr, f in enumerate([f for f in top.sub if f.fn == 8 and f.sub], start=1):
        sieben = _feld(f, 7)
        if sieben is not None:
            sieben.val = nr
    return neue_id


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = Drx(sys.argv[1])
    if "--liste" in sys.argv:
        for i, (_, data) in enumerate(d.bodies):
            if data:
                print(f"Body {i}:", nodes_auflisten(pb_parse(data)[0]))
        return

    aus = sys.argv[2]
    vid = int(sys.argv[sys.argv.index("--vorlage-id") + 1])
    label = (sys.argv[sys.argv.index("--label") + 1]
             if "--label" in sys.argv else None)

    for i, (_, data) in enumerate(d.bodies):
        if not data:
            continue
        top = pb_parse(data)[0]
        if not any(n == vid for n, _ in nodes_auflisten(top)):
            print(f"Body {i}: Vorlage-Node nicht vorhanden — unveraendert.")
            continue
        neu = voranstellen(top, vid, label)
        d.bodies[i][1] = pb_ser([top])
        print(f"Body {i}: Node {neu} vorangestellt, "
              f"Kette: {[n for n, _ in nodes_auflisten(top)]}")
    d.save(aus)
    print("geschrieben:", aus)


if __name__ == "__main__":
    main()
