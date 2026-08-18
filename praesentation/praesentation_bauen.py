# -*- coding: utf-8 -*-
"""Baut praesentation.html — alle Farbfelder und Kurven werden aus den echten
LUT-Formeln gerechnet, nichts ist gemalt.

Aufruf:  py praesentation_bauen.py
Danach:  chrome --headless=new --no-pdf-header-footer \
             --print-to-pdf=Kino-Look-4-Node-Kette.pdf praesentation.html
"""
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)
sys.path.insert(0, os.path.join(WURZEL, "werkzeuge"))

from lut_filmemulation_log_zu_rec709 import film                 # noqa: E402
from lut_finish_kinofarben import finish, BAENDER                # noqa: E402
from messtafel_erzeugen import FELDER, linear_zu_slog3, M_709_ZU_SGAMUT3CINE  # noqa: E402

KEY_GAIN = 0.40


# ------------------------------------------------------------------ Hilfsmittel
def hexfarbe(rgb):
    v = np.clip(np.asarray(rgb, float), 0, 1)
    return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in v)


def slog3_von_szene(lin709):
    return linear_zu_slog3(np.asarray(lin709, float) @ M_709_ZU_SGAMUT3CINE.T)


def kette(lin709, mit_finish=True):
    code = slog3_von_szene(lin709)
    aus = film(code, "slog3")
    return finish(aus, KEY_GAIN) if mit_finish else aus


def pfad(punkte):
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in punkte)


# ------------------------------------------------------------------- Diagramme
def diagramm_kennlinie():
    """Was Node 1 mit den Tonwerten macht — Fuss, gerader Teil, Schulter."""
    b, h, r = 900, 420, 56
    x = np.linspace(0, 1, 256)
    aus = film(np.stack([x] * 3, 1), "slog3")

    def px(v):
        return r + v * (b - 2 * r)

    def py(v):
        return h - r - v * (h - 2 * r)

    teile = [f'<svg viewBox="0 0 {b} {h}" class="dia">']
    for i in range(0, 11):
        teile.append(f'<line x1="{px(i/10):.0f}" y1="{py(0):.0f}" x2="{px(i/10):.0f}" '
                     f'y2="{py(1):.0f}" class="raster"/>')
        teile.append(f'<line x1="{px(0):.0f}" y1="{py(i/10):.0f}" x2="{px(1):.0f}" '
                     f'y2="{py(i/10):.0f}" class="raster"/>')
    # Diagonale = ungewandelt
    teile.append(f'<line x1="{px(0):.0f}" y1="{py(0):.0f}" x2="{px(1):.0f}" '
                 f'y2="{py(1):.0f}" class="hilfe"/>')
    for k, farbe in enumerate(("#d4574a", "#4aa564", "#5b8ac6")):
        teile.append(f'<path d="{pfad([(px(a), py(v)) for a, v in zip(x, aus[:, k])])}" '
                     f'fill="none" stroke="{farbe}" stroke-width="3"/>')

    grau = film(np.array([[0.4128] * 3]), "slog3")[0, 1]
    teile.append(f'<circle cx="{px(0.4128):.0f}" cy="{py(grau):.0f}" r="7" class="punkt"/>')
    teile.append(f'<text x="{px(0.4128)+14:.0f}" y="{py(grau)-12:.0f}" class="mark">'
                 f'18-%-Grau → {grau:.2f}</text>')
    teile.append(f'<text x="{px(0.02):.0f}" y="{py(0.10):.0f}" class="mark">Fuß: '
                 f'Schwarz läuft nicht zu</text>')
    teile.append(f'<text x="{px(0.55):.0f}" y="{py(0.97):.0f}" class="mark">Schulter: '
                 f'Lichter brennen nicht aus</text>')
    teile.append(f'<text x="{b/2:.0f}" y="{h-14:.0f}" class="achse" text-anchor="middle">'
                 f'Kamera-Log (S-Log3), 0 … 1</text>')
    teile.append(f'<text x="16" y="{h/2:.0f}" class="achse" '
                 f'transform="rotate(-90 16 {h/2:.0f})" text-anchor="middle">Rec.709 aus</text>')
    teile.append("</svg>")
    return "".join(teile)


def diagramm_felder(mit_finish=True, ueberschriften=True):
    """Die synthetische Messtafel — links wie sie aus der Kamera kommt, rechts nach der Kette."""
    namen = list(FELDER)
    spalten, kachel, luecke = 6, 128, 8
    zeilen = (len(namen) + spalten - 1) // spalten
    b = spalten * (kachel + luecke)
    h = zeilen * (kachel + luecke + (22 if ueberschriften else 0))
    teile = [f'<svg viewBox="0 0 {b} {h}" class="tafel">']
    for i, name in enumerate(namen):
        lin = np.array([FELDER[name]])
        roh = slog3_von_szene(lin)[0]
        fertig = kette(lin, mit_finish)[0]
        z, s = divmod(i, spalten)
        x = s * (kachel + luecke)
        y = z * (kachel + luecke + (22 if ueberschriften else 0))
        teile.append(f'<rect x="{x}" y="{y}" width="{kachel/2:.0f}" height="{kachel}" '
                     f'fill="{hexfarbe(roh)}"/>')
        teile.append(f'<rect x="{x+kachel/2:.0f}" y="{y}" width="{kachel/2:.0f}" '
                     f'height="{kachel}" fill="{hexfarbe(fertig)}"/>')
        teile.append(f'<line x1="{x+kachel/2:.0f}" y1="{y}" x2="{x+kachel/2:.0f}" '
                     f'y2="{y+kachel}" stroke="#00000033"/>')
        if ueberschriften:
            teile.append(f'<text x="{x+kachel/2:.0f}" y="{y+kachel+16}" class="feld" '
                         f'text-anchor="middle">{name}</text>')
    teile.append("</svg>")
    return "".join(teile)


def diagramm_finish():
    """Was Node 3 mit den Farbtönen macht — Sättigung je Farbtonband."""
    b, h, r = 900, 300, 52
    teile = [f'<svg viewBox="0 0 {b} {h}" class="dia">']

    def px(grad):
        return r + grad / 360.0 * (b - 2 * r)

    def py(f):
        return h - r - (f - 0.4) / 0.9 * (h - 2 * r)

    for f in (0.5, 0.75, 1.0, 1.25):
        teile.append(f'<line x1="{px(0):.0f}" y1="{py(f):.0f}" x2="{px(360):.0f}" '
                     f'y2="{py(f):.0f}" class="raster"/>')
        teile.append(f'<text x="{px(0)-10:.0f}" y="{py(f)+5:.0f}" class="feld" '
                     f'text-anchor="end">{f:.2f}</text>')
    teile.append(f'<line x1="{px(0):.0f}" y1="{py(1.0):.0f}" x2="{px(360):.0f}" '
                 f'y2="{py(1.0):.0f}" class="hilfe"/>')

    # Farbstreifen als Farbtonachse
    for grad in range(0, 360, 3):
        import colour
        c = colour.HSV_to_RGB(np.array([grad / 360.0, 0.75, 0.85]))
        teile.append(f'<rect x="{px(grad):.1f}" y="{h-r+8:.0f}" width="{(b-2*r)/120+1:.1f}" '
                     f'height="14" fill="{hexfarbe(c)}"/>')

    punkte = []
    for grad in range(0, 361, 2):
        faktor = 1.0
        for mitte, breite, f, _ in BAENDER:
            d = abs((grad - mitte + 180) % 360 - 180)
            w = max(0.0, 1 - d / breite)
            w = w * w * (3 - 2 * w)
            faktor *= 1 + w * (f - 1)
        punkte.append((px(grad), py(faktor * 0.96)))
    teile.append(f'<path d="{pfad(punkte)}" fill="none" stroke="#2b6cb0" stroke-width="3"/>')
    for text, grad in (("Rot/Haut: wärmer", 15), ("Grün: ruhig", 120), ("Blau: leicht ruhig", 245)):
        teile.append(f'<text x="{px(grad):.0f}" y="{r-16:.0f}" class="mark" '
                     f'text-anchor="middle">{text}</text>')
    teile.append(f'<text x="{b/2:.0f}" y="{h-6:.0f}" class="achse" text-anchor="middle">'
                 f'Farbton in Grad</text>')
    teile.append("</svg>")
    return "".join(teile)


def diagramm_abweichung():
    """Gemessene Abweichung frei ↔ gekauft, nach Gruppen zusammengefasst."""
    # Mittlere absolute Abweichung je Feldgruppe, gemessen (siehe referenzen/messwerte.md)
    gruppen = [("Graukeil, 8 Stufen", 1.2), ("Hauttöne und Lippen", 4.1),
               ("Himmel, Stoff, Holz, Pflanze", 6.1), ("kräftige Bunttöne", 10.9)]
    b, h, r = 900, 260, 60
    teile = [f'<svg viewBox="0 0 {b} {h}" class="dia">']
    breite = (b - 2 * r) / len(gruppen)
    hoechst = 12.0   # Skalenende
    for i, (name, wert) in enumerate(gruppen):
        x = r + i * breite + breite * 0.18
        bh = (h - 2 * r) * wert / hoechst
        farbe = "#4aa564" if wert < 3 else ("#e0a33e" if wert < 7 else "#d4574a")
        teile.append(f'<rect x="{x:.0f}" y="{h-r-bh:.0f}" width="{breite*0.64:.0f}" '
                     f'height="{bh:.0f}" fill="{farbe}"/>')
        teile.append(f'<text x="{x+breite*0.32:.0f}" y="{h-r-bh-10:.0f}" class="mark" '
                     f'text-anchor="middle">{wert:.1f}</text>')
        teile.append(f'<text x="{x+breite*0.32:.0f}" y="{h-r+22:.0f}" class="feld" '
                     f'text-anchor="middle">{name}</text>')
    teile.append(f'<line x1="{r}" y1="{h-r:.0f}" x2="{b-r}" y2="{h-r:.0f}" class="hilfe"/>')
    teile.append(f'<text x="16" y="{h/2:.0f}" class="achse" '
                 f'transform="rotate(-90 16 {h/2:.0f})" text-anchor="middle">'
                 f'Abweichung in Prozentpunkten</text>')
    teile.append("</svg>")
    return "".join(teile)


def kettenbild(frei=False):
    kaesten = [
        ("1", ["Filmemulation"],
         "LUT (selbst gerechnet)" if frei else "Plugin mit Kameraprofil",
         "Log → Rec.709 mit Filmkennlinie", True),
        ("2", ["Weißabgleich", "+ Helligkeit"], "Primärkorrektur",
         "Belichtung und Farbe des Motivs", False),
        ("3", ["Finish"], "LUT bei 40 %", "die gestalterische Handschrift", True),
        ("4", ["Film-Look-", "Erzeuger"], "in Resolve enthalten",
         "Lichthof und Vignette", True),
    ]
    b, h = 1000, 220
    kb, luecke = 228, 18
    teile = [f'<svg viewBox="0 0 {b} {h}" class="dia">']
    for i, (nr, zeilen, art, zweck, fest) in enumerate(kaesten):
        x = 14 + i * (kb + luecke)
        farbe = "#eef3f8" if fest else "#fff4e2"
        rand = "#2b6cb0" if fest else "#c9821f"
        teile.append(f'<rect x="{x}" y="26" width="{kb}" height="150" rx="12" '
                     f'fill="{farbe}" stroke="{rand}" stroke-width="2"/>')
        teile.append(f'<text x="{x+16}" y="58" class="nr">{nr}</text>')
        for j, zeile in enumerate(zeilen):
            teile.append(f'<text x="{x+46}" y="{58 + j*22}" class="kopf">{zeile}</text>')
        oben = 58 + max(1, len(zeilen)) * 22 + 8
        teile.append(f'<text x="{x+16}" y="{oben}" class="feld">{art}</text>')
        teile.append(f'<text x="{x+16}" y="{oben+22}" class="feld">{zweck}</text>')
        teile.append(f'<text x="{x+16}" y="166" class="marke" fill="{rand}">'
                     f'{"bleibt gleich" if fest else "pro Dreh NEU"}</text>')
        if i < 3:
            xa = x + kb + 1
            teile.append(f'<path d="M {xa},101 L {xa+13},101" stroke="#666" stroke-width="2" '
                         f'marker-end="url(#pfeil)"/>')
    teile.append('<defs><marker id="pfeil" markerWidth="8" markerHeight="8" refX="6" refY="3" '
                 'orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#666"/></marker></defs>')
    teile.append("</svg>")
    return "".join(teile)


# ----------------------------------------------------------------------- Folien
STIL = """
@page { size: 297mm 210mm; margin: 0; }
:root { --text:#1b2733; --grau:#5a6b7c; --linie:#d7dee6; --akzent:#2b6cb0; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Segoe UI",system-ui,sans-serif; color:var(--text); }
.folie { width:1120px; height:790px; padding:48px 64px 34px; margin:0 auto;
         page-break-after:always; display:flex; flex-direction:column; }
.folie:last-child { page-break-after:auto; }
h1 { font-size:52px; line-height:1.1; margin:0 0 12px; }
h2 { font-size:34px; margin:0 0 6px; }
.unter { font-size:20px; color:var(--grau); margin:0 0 28px; }
p, li { font-size:19px; line-height:1.55; }
ul { padding-left:22px; }
.dia, .tafel { width:100%; height:auto; margin:14px 0 8px; }
.raster { stroke:#e7ecf1; stroke-width:1; }
.hilfe  { stroke:#9fb0c0; stroke-width:1.5; stroke-dasharray:5 5; }
.punkt  { fill:#1b2733; }
.mark   { font-size:15px; fill:#1b2733; }
.feld   { font-size:13px; fill:var(--grau); }
.achse  { font-size:15px; fill:var(--grau); }
.nr     { font-size:26px; font-weight:700; fill:var(--akzent); }
.kopf   { font-size:18px; font-weight:600; }
.marke  { font-size:14px; font-weight:600; }
table { border-collapse:collapse; width:100%; margin-top:10px; }
th, td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--linie); font-size:17px; }
th { color:var(--grau); font-weight:600; }
.kasten { background:#f4f7fa; border-left:5px solid var(--akzent);
          padding:16px 20px; margin:18px 0; font-size:19px; }
.warn { background:#fff6e8; border-left-color:#c9821f; }
.zwei { display:grid; grid-template-columns:1fr 1fr; gap:34px; }
.fuss { margin-top:auto; padding-top:18px; border-top:1px solid var(--linie);
        font-size:14px; color:var(--grau); display:flex; justify-content:space-between; }
.gross { font-size:30px; font-weight:600; }
"""

FUSS = ('<div class="fuss"><span>Kino-Look als 4-Node-Kette</span>'
        '<span>wunder-media.de</span></div>')


def folie(inhalt):
    return f'<section class="folie">{inhalt}{FUSS}</section>'


def bauen():
    f = []

    f.append(folie(f"""
      <h1>Kino-Look in DaVinci&nbsp;Resolve</h1>
      <p class="unter">Vier Nodes. Drei bleiben gleich, einer wird eingemessen.</p>
      {kettenbild()}
      <div class="kasten">Das Ziel ist nicht der spektakulärste Look, sondern ein
      <b>wiederholbarer</b>: derselbe Aufbau für jeden Dreh, in Sekunden übertragen,
      nach Monaten noch verständlich — und mit genau einer Stelle, an der man dreht.</div>
      <p style="color:#5a6b7c">Für Interviews, Vorträge und Veranstaltungen ·
      Mehrkamera · Log- und Rec.709-Material</p>"""))

    f.append(folie(f"""
      <h2>Das Problem</h2>
      <p class="unter">Warum es überhaupt eine feste Kette braucht</p>
      <div class="zwei">
        <div>
          <p><b>Log sieht flau aus — mit Absicht.</b> Die Kamera speichert
          Belichtungsumfang, kein fertiges Bild. Irgendwer muss daraus ein Bild machen.</p>
          <p><b>Jedes Mal neu klicken kostet Stunden</b> und liefert jedes Mal ein
          etwas anderes Ergebnis. Bei zwei Kameras fällt das sofort auf.</p>
          <p><b>Und nach drei Monaten</b> weiß niemand mehr, warum Node&nbsp;3 auf 40&nbsp;%
          steht.</p>
        </div>
        <div>
          <div class="kasten">Die Antwort ist nicht „mehr Regler", sondern
          <b>Arbeitsteilung</b>:<br><br>
          alles, was <b>immer gleich</b> ist, wird einmal festgelegt und übertragen —<br><br>
          alles, was <b>vom Motiv abhängt</b>, bekommt einen einzigen, klar benannten Node.</div>
        </div>
      </div>
      <p class="gross" style="margin-top:20px">Übertragen statt klicken: Sekunden statt
      Stunden — und exakt statt ungefähr.</p>"""))

    f.append(folie(f"""
      <h2>Die Kette</h2>
      <p class="unter">Die Reihenfolge ist nicht beliebig</p>
      {kettenbild()}
      <div class="kasten warn"><b>Weißabgleich und Grundbelichtung stehen VOR der
      kreativen LUT.</b> Andersherum verstärkt die LUT einen vorhandenen Farbstich mit —
      und man korrigiert am Ende gegen den eigenen Look an.</div>
      <table>
        <tr><th>Node</th><th>bleibt gleich?</th><th>Aufgabe</th></tr>
        <tr><td>1 Filmemulation</td><td>ja</td>
            <td>Log dekodieren und die Kennlinie eines Kinofilms geben</td></tr>
        <tr><td>2 Weißabgleich + Helligkeit</td><td><b>nein — pro Dreh und Kamera</b></td>
            <td>Belichtung, Schwarzpunkt, Farbtemperatur</td></tr>
        <tr><td>3 Finish</td><td>ja</td><td>die gestalterische Handschrift, auf 40 % gedrosselt</td></tr>
        <tr><td>4 Film-Look-Erzeuger</td><td>ja</td><td>Lichthof um helle Kanten, Vignette</td></tr>
      </table>"""))

    f.append(folie(f"""
      <h2>Node 1 — Filmemulation</h2>
      <p class="unter">Was mit den Tonwerten passiert</p>
      {diagramm_kennlinie()}
      <p>Die gestrichelte Linie wäre „nichts tun". Die Kurve macht drei Dinge, die ein
      Kinofilm von Natur aus tut: Der <b>Fuß</b> lässt Schwarz nie ganz zulaufen, der
      <b>gerade Teil</b> erzeugt den Kontrast, die <b>Schulter</b> fängt Lichter weich ab,
      statt sie abzuschneiden. Dass die drei Kanäle in den Lichtern leicht auseinandergehen,
      ist gewollt — daran erkennt das Auge Film.</p>"""))

    f.append(folie(f"""
      <h2>Node 2 — der einzige Node, an dem gedreht wird</h2>
      <p class="unter">Alles Motivabhängige gehört hierher, und nirgendwo sonst hin</p>
      <table>
        <tr><th>Regler</th><th>wofür</th><th>Faustregel</th></tr>
        <tr><td>Offset (R/G/B gleich)</td><td>Schwarzpunkt</td>
            <td>Tiefen nicht auf 0 drücken — eine Bodenschwelle lassen</td></tr>
        <tr><td>Gain</td><td>Lichter</td><td>niedrig halten, sonst brennen Gesichter aus</td></tr>
        <tr><td>Gamma / Mitteltöne</td><td>Helligkeit</td>
            <td><b>hier</b> wird das Bild hell und freundlich</td></tr>
        <tr><td>Temperatur / Tönung</td><td>Weißabgleich</td>
            <td>an einer echten neutralen Fläche im Bild messen</td></tr>
      </table>
      <div class="kasten">Zwei Kameras gleicht man <b>nur über Node 2 der Nebenkamera</b> an:
      dieselbe neutrale Fläche in beiden Winkeln messen, Differenz dort korrigieren.
      Eine zusätzliche LUT für eine Kamera macht den Unterschied unsichtbar —
      aber auch unkorrigierbar.</div>
      <div class="kasten warn">Ob heller oder dunkler <i>richtig</i> ist, entscheidet kein
      Messgerät. Werte vorschlagen, Richtung vom Menschen bestätigen lassen.</div>"""))

    f.append(folie(f"""
      <h2>Node 3 — Finish</h2>
      <p class="unter">Sättigung je Farbton: was ruhiger wird und was wärmer</p>
      {diagramm_finish()}
      <p>Grün und Cyan gehen deutlich zurück — Wände, Pflanzen und Hintergrund werden
      ruhig, statt vom Gesicht abzulenken. Rot und Orange bleiben kräftig und drehen ein
      paar Grad ins Warme: das ist der Hautton.</p>
      <div class="kasten"><b>Warum nur 40 %?</b> Voll aufgetragen wirken Finish-LUTs
      ausgewaschen statt zurückhaltend. Der Key-Ausgabe-Gain dosiert dieselbe LUT stufenlos
      — eine LUT mit Regler statt zehn LUT-Varianten.</div>"""))

    f.append(folie(f"""
      <h2>Node 4 — Film-Look-Erzeuger</h2>
      <p class="unter">Kostet nichts extra und ist trotzdem der letzte Schliff</p>
      <div class="zwei">
        <div>
          <p><b>Lichthof (Halation)</b> — der warme Saum um helle Kanten. Auf echtem Film
          entsteht er, weil Licht durch die Emulsion hindurch von der Rückseite reflektiert
          wird. Im Bild wirkt er wie Weichheit, ohne dass etwas unscharf wird.</p>
          <p><b>Vignette</b> — die Ränder eine Spur dunkler. Der Blick bleibt in der Mitte,
          da wo das Gesicht ist.</p>
        </div>
        <div>
          <div class="kasten"><b>Der Trick sind zwei getrennte Regler.</b><br><br>
          „Farbüberblendung" steuert Film-Look, Farbeinstellungen und Teiltonung —
          hier auf <b>17&nbsp;%</b>.<br><br>
          „Effektüberblendung" steuert Vignette, Lichthof, Bloom, Korn —
          hier auf <b>100&nbsp;%</b>.<br><br>
          So wirken gezielt nur die Effekte, während die Farbe aus Node 1 und 3 kommt.</div>
        </div>
      </div>
      <p>Filmkorn bleibt hier aus, wenn Node 1 schon Korn liefert — sonst wird es hier
      eingeschaltet. Alle 190 Parameter mit ihren Werten stehen in der Referenz.</p>"""))

    f.append(folie(f"""
      <h2>Vorher / nachher</h2>
      <p class="unter">Synthetische Messtafel: links wie sie aus der Kamera kommt,
      rechts nach der Kette</p>
      {diagramm_felder()}
      <p>Keine Aufnahmen, sondern gerechnete Farbfelder — Szenenlicht, in Kamera-Log
      kodiert. So lässt sich jede Änderung an der Kette in Zahlen prüfen, statt sie zu
      erahnen. Gut zu sehen: die flauen Log-Werte liegen alle eng beieinander,
      nach der Kette sind Schwarz, Mitten und Lichter auseinandergezogen — und
      die Farben haben Richtung bekommen.</p>"""))

    f.append(folie(f"""
      <h2>Mit gekauften Werkzeugen — oder ganz ohne</h2>
      <p class="unter">Dieselbe Kette, zwei Bestückungen</p>
      <table>
        <tr><th></th><th>Node 1</th><th>Node 3</th><th>Node 4</th></tr>
        <tr><td><b>gekauft</b> (Standard)</td><td>Plugin mit vermessenem Kameraprofil
            und gescannten Emulsionen</td><td>LUT-Satz mit vielen Handschriften</td>
            <td colspan="1">in Resolve enthalten</td></tr>
        <tr><td><b>kostenlos</b></td><td>selbst gerechnete LUT</td>
            <td>selbst gerechnete LUT</td><td>in Resolve enthalten</td></tr>
      </table>
      <div class="kasten">Die kostenlose Variante ist <b>kein Nachbau</b>. Die LUTs
      entstehen aus einem gerechneten Modell — Log-Dekodierung nach veröffentlichter
      Formel, Negativ- und Kopierfilm-Kennlinien, Farbtonbänder. Es werden keine
      fremden LUT-Daten gelesen oder angenähert.</div>
      <p>Zwei Skripte, dann steht sie:
      <code>luts_erzeugen.py</code> → <code>luts_installieren.py</code> →
      <code>look_anwenden.py --frei</code></p>"""))

    f.append(folie(f"""
      <h2>Was der Verzicht kostet — gemessen</h2>
      <p class="unter">Abweichung der freien Kette gegenüber der gekauften,
      auf derselben Messtafel</p>
      {diagramm_abweichung()}
      <p><b>Die Grauachse stimmt</b> — über sechs Blenden unter zwei Prozentpunkten.
      Das ist der Teil, der über „sieht richtig belichtet aus" entscheidet.
      <b>Hauttöne liegen nah beieinander.</b> Auseinander gehen die kräftigen Bunttöne:
      die gekaufte Finish-LUT entsättigt stärker, die freie hält mehr Farbe. Das ist kein
      Fehler, sondern der Unterschied zwischen zwei Handschriften — und über den
      Key-Ausgabe-Gain angleichbar.</p>
      <div class="kasten">Gegenprobe: die freie Kette wurde zusätzlich in Resolve
      gerendert und mit der Rechnung verglichen — 0,3 Prozentpunkte Abweichung im Mittel.
      Die Zahlen bilden also ab, was Resolve wirklich tut.</div>"""))

    f.append(folie(f"""
      <h2>Wer macht was</h2>
      <p class="unter">Skript macht Zahlen, Pfade, Struktur. Der Mensch macht Zeigen
      und Beurteilen.</p>
      <table>
        <tr><th>Aufgabe</th><th>per Skript</th><th>von Hand</th></tr>
        <tr><td>Ganze Kette inkl. Plugin, LUT und Werten anlegen</td><td>Sekunden</td>
            <td>5–15 min je Clip</td></tr>
        <tr><td>Kette auf alle Kameras verteilen</td><td>Schleife</td><td>× Anzahl</td></tr>
        <tr><td>Nodes beschriften, Nodes entfernen, Werte auslesen</td><td>ja</td><td>—</td></tr>
        <tr><td>Kameras gegeneinander messen</td><td>ja, in Zahlen</td><td>nach Augenmaß</td></tr>
        <tr><td>Weißabgleich und Helligkeit <b>beurteilen</b></td><td>nein</td>
            <td><b>Mensch</b></td></tr>
        <tr><td>Geteilte Nodes verknüpfen, LUT-Interpolation tetraedrisch</td>
            <td>geht nicht</td><td><b>Mensch</b>, wenige Klicks</td></tr>
        <tr><td>Sekundärkorrekturen mit Fenster und Qualifizierer</td><td>unbrauchbar</td>
            <td><b>Mensch</b></td></tr>
      </table>
      <div class="kasten warn">Eine Kette per Bildschirmsteuerung nachzuklicken dauert
      über eine Stunde und wird ungenau. Die Vorlage überträgt sie exakt — also nie tun.</div>"""))

    f.append(folie(f"""
      <h2>Fallstricke, die Zeit gekostet haben</h2>
      <ul>
        <li><b>Color Management killt die Filmemulation.</b> Node 1 will unveränderte
        Kamerapixel — deshalb DaVinci YRGB, nicht Color Managed.</li>
        <li><b>LUT-Interpolation auf „Tetraedrisch".</b> Sonst wandern bei steilen LUTs
        Streifen durch Verläufe. Nicht über die Schnittstelle erreichbar.</li>
        <li><b>In einer Grade-Vorlage stehen nur Nicht-Standardwerte.</b> Ein fehlender
        Parameter steht auf Plugin-Standard, nicht auf 0 — wer nur das Gelesene nachbaut,
        bekommt ein anderes Bild.</li>
        <li><b>Keyframes in übertragenen Effekten werten zu 0 aus.</b> Der Effekt hängt
        sichtbar am Node und rechnet trotzdem nichts. Vorlagen keyframe-frei sichern.</li>
        <li><b>Motivabhängiges gehört nicht in eine Vorlage.</b> Ein kopiertes Fenster
        sitzt im nächsten Motiv falsch.</li>
        <li><b>Jedes Anwenden erzeugt eigene geteilte Nodes.</b> Echtes Verknüpfen bleibt
        ein Rechtsklick pro Node.</li>
      </ul>"""))

    f.append(folie("""
      <h1>Kurz gesagt</h1>
      <p class="gross">Drei Nodes, die nie wieder angefasst werden.<br>
      Einer, an dem man dreht.<br>
      Und eine Vorlage, die das in Sekunden überträgt.</p>
      <div class="kasten">Alles nachlesbar: die Werte jedes Nodes, alle 190 Parameter des
      Film-Look-Erzeugers, die Messwerte des Vergleichs und die Skripte, die die LUTs
      erzeugen. Nichts davon ist eine Blackbox.</div>
      <p style="margin-top:28px">Entstanden in der täglichen Arbeit an
      Mehrkamera-Mitschnitten.<br>
      Fragen und Rückmeldungen gern an <b>wunder-media.de</b></p>"""))

    html = (f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f'<title>Kino-Look als 4-Node-Kette</title><style>{STIL}</style></head>'
            f'<body>{"".join(f)}</body></html>')
    ziel = os.path.join(HIER, "praesentation.html")
    open(ziel, "w", encoding="utf-8").write(html)
    print("geschrieben:", ziel, f"({len(f)} Folien)")
    print("PDF daraus:")
    print(r'  chrome --headless=new --no-pdf-header-footer '
          r'--print-to-pdf="Kino-Look-4-Node-Kette.pdf" praesentation.html')


if __name__ == "__main__":
    bauen()
