# -*- coding: utf-8 -*-
"""drxlib — DRX-Grade-Dateien lesen/patchen/schreiben.

Eine .drx ist XML mit <Body>-Hexbloecken: 0x81-Prefix + zstd-komprimiertes Protobuf.
Im Protobuf (pClipFullVer-Body) liegen Grading-Parameter als Eintraege:
  1a <len> 08 <param_id varint> 12 05 0d <float32 LE>
param_id-Namespace um 0x06000000 (varint '.. 80 80 30').
"""
import re, struct
try:                                  # Python 3.14+
    from compression import zstd
except ImportError:                    # aeltere Python: gleichwertiges Paket
    import zstandard as _zstd

    class zstd:                        # nur die zwei benutzten Funktionen
        @staticmethod
        def decompress(daten):
            return _zstd.ZstdDecompressor().decompress(daten)

        @staticmethod
        def compress(daten, stufe=19):
            return _zstd.ZstdCompressor(level=stufe).compress(daten)

BODY_RE = re.compile(r"(<Body>)([0-9a-f]+)(</Body>)")
# Eintrag: 1a <len> 08 <varint id> 12 05 0d <4B float>  (len 0x0c/0x0d je nach id-Groesse)
ENTRY_RE = re.compile(rb"\x1a([\x0a-\x0f])\x08((?:[\x80-\xff]{0,4}[\x00-\x7f]))\x12\x05\x0d(.{4})", re.S)


def varint_decode(b: bytes) -> int:
    v = 0
    for i, byte in enumerate(b):
        v |= (byte & 0x7F) << (7 * i)
    return v


def varint_encode(v: int) -> bytes:
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


# ---------- minimaler Protobuf-Baum (ohne Schema) ----------

class PbField:
    __slots__ = ("fn", "wt", "val", "sub")
    def __init__(self, fn, wt, val, sub=None):
        self.fn, self.wt, self.val, self.sub = fn, wt, val, sub


def pb_parse(buf):
    """Parst buf als Protobuf-Message; None wenn nicht parsebar."""
    fields = []
    i = 0
    n = len(buf)
    while i < n:
        # tag varint
        v = 0; shift = 0; start = i
        while True:
            if i >= n:
                return None
            b = buf[i]; i += 1
            v |= (b & 0x7F) << shift; shift += 7
            if not b & 0x80:
                break
            if shift > 35:
                return None
        fn, wt = v >> 3, v & 7
        if fn == 0:
            return None
        if wt == 0:
            v2 = 0; shift = 0
            while True:
                if i >= n:
                    return None
                b = buf[i]; i += 1
                v2 |= (b & 0x7F) << shift; shift += 7
                if not b & 0x80:
                    break
                if shift > 70:
                    return None
            fields.append(PbField(fn, wt, v2))
        elif wt == 5:
            if i + 4 > n:
                return None
            fields.append(PbField(fn, wt, buf[i:i + 4])); i += 4
        elif wt == 1:
            if i + 8 > n:
                return None
            fields.append(PbField(fn, wt, buf[i:i + 8])); i += 8
        elif wt == 2:
            ln = 0; shift = 0
            while True:
                if i >= n:
                    return None
                b = buf[i]; i += 1
                ln |= (b & 0x7F) << shift; shift += 7
                if not b & 0x80:
                    break
                if shift > 35:
                    return None
            if i + ln > n:
                return None
            payload = buf[i:i + ln]; i += ln
            fields.append(PbField(fn, wt, payload, pb_parse(payload) if ln else []))
        else:
            return None
    return fields


def pb_ser(fields):
    out = bytearray()
    for f in fields:
        out += varint_encode((f.fn << 3) | f.wt)
        if f.wt == 0:
            out += varint_encode(f.val)
        elif f.wt in (1, 5):
            out += f.val
        elif f.wt == 2:
            payload = pb_ser(f.sub) if f.sub is not None else f.val
            out += varint_encode(len(payload)) + payload
    return bytes(out)


def make_entry(pid, value):
    """Feld 3 (0x1a): { 1: pid, 2: { 1: float32 } }"""
    inner = b"\x0d" + struct.pack("<f", float(value))
    body = b"\x08" + varint_encode(pid) + b"\x12" + varint_encode(len(inner)) + inner
    return PbField(3, 2, body, pb_parse(body))


def _find_entry_containers(fields, path=None, out=None):
    """Findet Messages, die Param-Eintraege (Feld 3 mit {1:id, 2:{1:f32}}) enthalten."""
    if out is None:
        out = []
    for f in fields:
        if f.wt == 2 and f.sub:
            kinder3 = [c for c in f.sub if c.fn == 3 and c.wt == 2 and c.sub
                       and any(g.fn == 1 and g.wt == 0 for g in c.sub)
                       and any(g.fn == 2 and g.wt == 2 for g in c.sub)]
            if kinder3:
                out.append(f)
            _find_entry_containers(f.sub, out=out)
    return out


class Drx:
    def __init__(self, path):
        self.path = path
        self.xml = open(path, "r", encoding="utf-8").read()
        self.bodies = []  # list of (hex, decompressed bytes | None)
        for m in BODY_RE.finditer(self.xml):
            hexs = m.group(2)
            raw = bytes.fromhex(hexs)
            try:
                data = zstd.decompress(raw[1:]) if raw[:1] == b"\x81" else None
            except Exception:
                data = None
            self.bodies.append([hexs, data])

    def params(self, body_idx=0):
        """Alle (param_id, float)-Eintraege des Bodies."""
        d = self.bodies[body_idx][1]
        out = []
        for m in ENTRY_RE.finditer(d):
            pid = varint_decode(m.group(2))
            val = struct.unpack("<f", m.group(3))[0]
            out.append((pid, val, m.start(3)))
        return out

    def set_param(self, pid, value, body_idx=0, add_if_missing=True):
        """Setzt param pid auf value (float32). Fuegt Eintrag hinzu, wenn nicht vorhanden."""
        d = self.bodies[body_idx][1]
        f = struct.pack("<f", float(value))
        for m in ENTRY_RE.finditer(d):
            if varint_decode(m.group(2)) == pid:
                d = d[: m.start(3)] + f + d[m.end(3):]
                self.bodies[body_idx][1] = d
                return "patched"
        if not add_if_missing:
            return "missing"
        # Eintrag ueber Protobuf-Baum korrekt einfuegen (alle Containerlaengen werden neu berechnet)
        tree = pb_parse(d)
        if tree is None:
            return "missing"
        containers = _find_entry_containers(tree)
        if not containers:
            return "missing"
        cont = containers[0]
        # hinter dem letzten Eintrag (Feld 3) einfuegen
        idx = max(i for i, c in enumerate(cont.sub) if c.fn == 3)
        cont.sub.insert(idx + 1, make_entry(pid, value))
        neu = pb_ser(tree)
        # Sicherheits-Check: Roundtrip ohne Einfuegung muss identisch sein
        self.bodies[body_idx][1] = neu
        return "added"

    def save(self, out_path):
        xml = self.xml
        # Bodies in Reihenfolge neu einsetzen
        it = iter(self.bodies)

        def repl(m):
            hexs, data = next(it)
            if data is None:
                return m.group(0)
            comp = zstd.compress(data, 19)
            return m.group(1) + (b"\x81" + comp).hex() + m.group(3)

        xml = BODY_RE.sub(repl, xml)
        open(out_path, "w", encoding="utf-8", newline="\n").write(xml)
        return out_path


if __name__ == "__main__":
    import sys
    d = Drx(sys.argv[1])
    for i, (h, data) in enumerate(d.bodies):
        print(f"Body {i}: {len(data) if data else '?'} B entpackt")
        if data:
            for pid, val, off in d.params(i):
                print(f"  id={pid:#010x}  wert={val:+.6f}")
