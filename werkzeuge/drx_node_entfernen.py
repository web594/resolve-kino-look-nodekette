# -*- coding: utf-8 -*-
"""Entfernt einen Node aus einer .drx-Grade-Vorlage und verbindet die Kette wieder.

Damit laesst sich aus einem fertigen Grade eine allgemein verwendbare Vorlage machen —
z. B. einen motivabhaengigen Sekundaer-Node (Fenster/Qualifizierer) herausnehmen, der in
einem anderen Projekt sowieso falsch saesse.

Aufruf:
    py drx_node_entfernen.py <ein.drx> <aus.drx> --id 5
    py drx_node_entfernen.py <ein.drx> <aus.drx> --label "Gesicht"     # Teiltreffer reicht
    py drx_node_entfernen.py <ein.drx> --liste                          # nur anzeigen

Aufbau einer .drx (reverse engineered): XML mit <Body>-Hexbloecken
(0x81-Prefix + zstd + Protobuf). Im Body:
    Feld 7 = Node-Container   {1: Node-Id, 2: Reihenfolge, 4/5: Position, 6: Label, 7: aktiv}
    Feld 8 = Verbindung       {1: von-Node, 3: nach-Node, 7: laufende Nummer}
    Feld 9 = Quell-Anschluss  {3: {4: erster Node}}
    Feld 10 = Ausgangs-Anschluss {3: {4: letzter Node}}
Beim Entfernen wird der Container geloescht, die eingehende Verbindung auf das Ziel der
ausgehenden umgebogen und die laufenden Nummern neu vergeben.
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

from drxlib import Drx, pb_parse, pb_ser          # noqa: E402


def _feld(container, fn):
    for c in container.sub:
        if c.fn == fn:
            return c
    return None


def nodes_auflisten(top):
    out = []
    for f in top.sub:
        if f.fn == 7 and f.sub:
            nid = _feld(f, 1)
            lab = _feld(f, 6)
            out.append((nid.val if nid else None,
                        lab.val.decode("utf-8", "ignore") if lab else ""))
    return out


def node_entfernen(top, node_id):
    """Loescht Node-Container node_id und schliesst die Luecke in den Verbindungen."""
    vorher = [f for f in top.sub if f.fn == 7 and _feld(f, 1) and _feld(f, 1).val == node_id]
    if not vorher:
        raise SystemExit(f"Node {node_id} nicht gefunden.")

    verb = [f for f in top.sub if f.fn == 8 and f.sub]
    rein = [f for f in verb if _feld(f, 3) and _feld(f, 3).val == node_id]   # x -> node
    raus = [f for f in verb if _feld(f, 1) and _feld(f, 1).val == node_id]   # node -> y

    weg = set()
    if rein and raus:                       # mittendrin: umbiegen, eine Verbindung faellt weg
        _feld(rein[0], 3).val = _feld(raus[0], 3).val
        weg.add(id(raus[0]))
    elif raus:                              # erster Node: Quell-Anschluss nachziehen
        neu = _feld(raus[0], 3).val
        for f in top.sub:
            if f.fn == 9:
                _quelle_setzen(f, neu)
        weg.add(id(raus[0]))
    elif rein:                              # letzter Node: Ausgang nachziehen
        neu = _feld(rein[0], 1).val
        for f in top.sub:
            if f.fn == 10:
                _quelle_setzen(f, neu)
        weg.add(id(rein[0]))

    top.sub = [f for f in top.sub
               if not (f.fn == 7 and _feld(f, 1) and _feld(f, 1).val == node_id)
               and id(f) not in weg]

    # laufende Nummern der Verbindungen neu vergeben
    for nr, f in enumerate([f for f in top.sub if f.fn == 8 and f.sub], start=1):
        sieben = _feld(f, 7)
        if sieben is not None:
            sieben.val = nr
    return len(weg)


def _quelle_setzen(anschluss, node_id):
    """Feld 3 eines Anschlusses ist ein eingebetteter Protobuf mit {4: Node}."""
    inner = _feld(anschluss, 3)
    if inner is None or inner.wt != 2:
        return
    baum = pb_parse(inner.val if inner.sub is None else pb_ser(inner.sub))
    for g in baum:
        if g.fn == 4:
            g.val = node_id
    inner.sub = baum
    inner.val = pb_ser(baum)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ein = sys.argv[1]
    d = Drx(ein)

    if "--liste" in sys.argv:
        for i, (_, data) in enumerate(d.bodies):
            if not data:
                continue
            top = pb_parse(data)[0]
            print(f"Body {i}:")
            for nid, lab in nodes_auflisten(top):
                print(f"   Node {nid}  {lab or '(ohne Label)'}")
        return

    aus = sys.argv[2]
    if "--id" in sys.argv:
        ziel_id, ziel_label = int(sys.argv[sys.argv.index("--id") + 1]), None
    elif "--label" in sys.argv:
        ziel_id, ziel_label = None, sys.argv[sys.argv.index("--label") + 1].lower()
    else:
        sys.exit("--id oder --label angeben.")

    for i, (_, data) in enumerate(d.bodies):
        if not data:
            continue
        top = pb_parse(data)[0]
        vorhanden = dict(nodes_auflisten(top))
        treffer = ziel_id if ziel_id in vorhanden else None
        if treffer is None and ziel_label:
            for nid, lab in vorhanden.items():
                if ziel_label in lab.lower():
                    treffer = nid
                    break
        if treffer is None:
            print(f"Body {i}: kein Treffer — unveraendert.")
            continue
        node_entfernen(top, treffer)
        d.bodies[i][1] = pb_ser([top])
        print(f"Body {i}: Node {treffer} entfernt, "
              f"Kette: {[n for n, _ in nodes_auflisten(top)]}")

    d.save(aus)
    print("geschrieben:", aus)


if __name__ == "__main__":
    main()
