# -*- coding: utf-8 -*-
"""Liest einen fertigen Grade aus einer .drx aus — ohne dass Resolve laufen muss.

Zeigt pro Node die Reglerwerte in ANZEIGE-Skala (wie im Primaries-Panel) und danach
alle OFX-Plugins mit ihren Parametern im Klartext.

Aufruf:
    py drx_werte.py <datei.drx>
    py drx_werte.py <datei.drx> --roh      # zusaetzlich unbekannte Param-IDs

Hintergrund: eine .drx ist XML mit <Body>-Hexbloecken (0x81-Prefix + zstd + Protobuf).
Reglerwerte stehen als (param_id -> float32), IDs und Skalen in calibration_map.json.
OFX-Parameter stehen mit Klartextnamen als f5={f1:"Name", f2:{...}}.
⚠️ Im Body stehen NUR Nicht-Default-Werte — ein fehlender Parameter ist auf Plugin-Standard.
"""
import sys
import os
import json
import struct

# drxlib.py + calibration_map.json: erst neben dem Skript (mitgeliefertes lib/),
# sonst der Werkzeugkasten (Pfad ueber Umgebungsvariable RESOLVE_CTL ueberschreibbar).
_HIER = os.path.dirname(os.path.abspath(__file__))
for _kandidat in (os.path.join(_HIER, "..", "lib"),
                  os.environ.get("RESOLVE_CTL") or ""):
    _kandidat = os.path.abspath(_kandidat)
    if os.path.exists(os.path.join(_kandidat, "drxlib.py")):
        LIB = _kandidat
        break
else:
    sys.exit("drxlib.py nicht gefunden — lib/ mitliefern oder RESOLVE_CTL setzen.")

sys.path.insert(0, LIB)
from drxlib import Drx, pb_parse                      # noqa: E402

MAP = json.load(open(os.path.join(LIB, "calibration_map.json"), encoding="utf-8"))
BY_ID = {int(v["id"], 16): (k, v) for k, v in MAP.items() if isinstance(v, dict)}


# ---------------------------------------------------------------- Reglerwerte
def _eintraege(felder, acc):
    """Sammelt (param_id, float) rekursiv."""
    for c in felder:
        if c.fn == 3 and c.wt == 2 and c.sub:
            pid = val = None
            for g in c.sub:
                if g.fn == 1 and g.wt == 0:
                    pid = g.val
                if g.fn == 2 and g.wt == 2 and g.sub:
                    for h in g.sub:
                        if h.fn == 1 and h.wt == 5:
                            val = struct.unpack("<f", h.val)[0]
            if pid is not None and val is not None:
                acc.append((pid, val))
        elif c.wt == 2 and c.sub:
            _eintraege(c.sub, acc)


def nodes(baum, roh=False):
    """Gibt [(node_id, label, [(regler, anzeigewert)], [(hex_id, wert)])] zurueck."""
    out = []

    def lauf(felder):
        for f in felder:
            if f.wt != 2 or not f.sub:
                continue
            if f.fn == 7:                                   # Node-Container
                g = {c.fn: c for c in f.sub}
                nid = g[1].val if 1 in g and g[1].wt == 0 else "?"
                aktiv = g[7].val if 7 in g and g[7].wt == 0 else "?"
                lab = (g[6].val.decode("utf-8", "ignore")
                       if 6 in g and g[6].wt == 2 else "")
                acc = []
                _eintraege(f.sub, acc)
                bekannt, unbekannt = [], []
                for pid, v in acc:
                    if pid in BY_ID:
                        name, cfg = BY_ID[pid]
                        anzeige = v / cfg["faktor"] + cfg["basis"] if cfg["faktor"] else v
                        if abs(anzeige - cfg["neutral"]) > 1e-4:
                            bekannt.append((name, anzeige, cfg["neutral"]))
                    else:
                        unbekannt.append((hex(pid), round(v, 4)))
                if nid != "?":
                    out.append((nid, lab, aktiv, bekannt, unbekannt))
            lauf(f.sub)

    lauf(baum)
    return out


# ------------------------------------------------------------------ OFX-Werte
def _wert(f):
    teile = []
    for c in f.sub or []:
        if c.wt == 0:                        # Ganzzahl/Bool, egal an welcher Feldnummer
            teile.append(("int", c.val))
        elif c.fn == 2 and c.wt == 1:
            teile.append(("dbl", round(struct.unpack("<d", c.val)[0], 5)))
        elif c.fn == 4 and c.sub:
            for g in c.sub:
                if g.wt == 0:
                    teile.append(("auswahl", g.val))
        elif c.fn == 5 and c.wt == 2:
            try:
                teile.append(("txt", c.val.decode("utf-8")))
            except Exception:
                pass
        elif c.fn == 3 and c.sub:
            for g in c.sub:
                if g.wt == 1:
                    teile.append(("dbl", round(struct.unpack("<d", g.val)[0], 5)))
                elif g.wt == 5:
                    teile.append(("f32", round(struct.unpack("<f", g.val)[0], 5)))
    return teile


def ofx(baum):
    res = {}

    def lauf(felder, plugin):
        for f in felder:
            if f.wt != 2 or not f.sub:
                continue
            namen = [c.val.decode("utf-8", "ignore") for c in f.sub
                     if c.fn == 2 and c.wt == 2 and b"com." in c.val
                     and c.val.startswith(b"com.")]
            if namen:
                plugin = namen[0]
                res.setdefault(plugin, [])
            if f.fn == 5 and plugin:
                nm = vv = None
                for c in f.sub:
                    if c.fn == 1 and c.wt == 2:
                        try:
                            nm = c.val.decode("utf-8")
                        except Exception:
                            nm = None
                    if c.fn == 2 and c.wt == 2:
                        vv = c
                if nm and vv is not None:
                    w = _wert(vv)
                    if w:
                        res[plugin].append((nm, w))
            lauf(f.sub, plugin)

    lauf(baum, None)
    return {k: v for k, v in res.items() if v}


# ----------------------------------------------------------------------- main
def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pfad = sys.argv[1]
    roh = "--roh" in sys.argv
    d = Drx(pfad)
    baum = pb_parse(d.bodies[0][1])

    print(f"=== {os.path.basename(pfad)} ===\n")
    print("--- Nodes und Reglerwerte (Anzeige-Skala) ---")
    for nid, lab, aktiv, bekannt, unbekannt in nodes(baum):
        status = "" if aktiv == 1 else f"  [AUSGESCHALTET aktiv={aktiv}]"
        print(f"\nNode {nid}  {lab or '(ohne Label)'}{status}")
        for name, wert, neutral in bekannt:
            print(f"    {name:12} = {wert:+9.4f}   (neutral {neutral})")
        if not bekannt:
            print("    (keine Reglerabweichung — LUT- oder OFX-Node)")
        if roh and unbekannt:
            print(f"    unbekannte IDs: {unbekannt}")

    print("\n--- OFX-Plugins ---")
    for plug, params in ofx(baum).items():
        print(f"\n{plug}  ({len(params)} Parameter)")
        for nm, w in params:
            print(f"    {nm:30} " + ", ".join(f"{k}={x}" for k, x in w))

    # LUT-Pfade stehen als Klartext im Body
    import re
    luts = sorted(set(re.findall(rb"[A-Za-z][\x20-\x7e]{3,}\.cube", d.bodies[0][1])))
    if luts:
        print("\n--- LUTs ---")
        for lut in luts:
            print("   ", lut.decode("ascii", "replace"))


if __name__ == "__main__":
    main()
