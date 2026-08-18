# Messwerte: freie Kette gegen gekaufte Kette

Nach Gefühl zu vergleichen führt in die Irre — deshalb hier Zahlen. Verglichen werden
**Node 1 und Node 3** in beiden Varianten; Node 2 steht dabei neutral und Node 4 ist in
beiden Fällen derselbe (der Film-Look-Erzeuger gehört zu Resolve).

## So wurde gemessen

1. `werkzeuge/messtafel_erzeugen.py` erzeugt eine **synthetische Messtafel**: 18 Farbfelder,
   als Szenenlicht angegeben und in S-Log3/S-Gamut3.Cine kodiert. Keine Aufnahmen, kein
   Bildmaterial aus einer Produktion — nur gerechnete Werte.
2. Die Tafel läuft in DaVinci Resolve durch die **gekaufte** Kette; das Ergebnis wird als
   Standbild exportiert und Feld für Feld ausgemessen.
3. Die **freie** Kette wird mit denselben Formeln gerechnet, die auch die `.cube`-Dateien
   erzeugen — inklusive der 40 % Key-Ausgabe-Gain des Finish-Nodes.
4. `werkzeuge/vergleich_messen.py` stellt beides gegenüber.

**Gegenprobe:** dieselbe freie Kette wurde zusätzlich in Resolve gerendert und mit der
Rechnung verglichen — Abweichung im Mittel **0,30**, maximal **0,96 Prozentpunkte**.
Die Rechnung bildet also ab, was Resolve tatsächlich tut; Rest sind LUT-Interpolation
und 8-Bit-Quantisierung des Standbilds.

## Ergebnis

| Feld | gekauft (R/G/B) | frei (R/G/B) | Abweichung in Prozentpunkten |
|---|---|---|---|
| Grau -3 Blenden | 0.108 / 0.103 / 0.104 | 0.091 / 0.095 / 0.098 | -1.7 / -0.9 / -0.6 |
| Grau -2 Blenden | 0.194 / 0.183 / 0.187 | 0.174 / 0.176 / 0.178 | -2.0 / -0.7 / -0.9 |
| Grau -1 Blende | 0.333 / 0.317 / 0.328 | 0.310 / 0.310 / 0.310 | -2.3 / -0.6 / -1.8 |
| Grau 18 % | 0.506 / 0.484 / 0.500 | 0.493 / 0.493 / 0.493 | -1.3 / +0.9 / -0.7 |
| Grau +1 Blende | 0.697 / 0.669 / 0.679 | 0.687 / 0.683 / 0.678 | -1.1 / +1.4 / -0.1 |
| Grau +2 Blenden | 0.851 / 0.812 / 0.808 | 0.840 / 0.829 / 0.815 | -1.1 / +1.8 / +0.8 |
| Grau +3 Blenden | 0.945 / 0.906 / 0.894 | 0.928 / 0.916 / 0.901 | -1.8 / +1.0 / +0.7 |
| Weiß 90 % | 0.886 / 0.846 / 0.839 | 0.876 / 0.864 / 0.848 | -1.0 / +1.8 / +0.9 |
| Haut hell | 0.661 / 0.554 / 0.534 | 0.707 / 0.586 / 0.500 | +4.5 / +3.2 / -3.4 |
| Haut mittel | 0.532 / 0.420 / 0.396 | 0.587 / 0.430 / 0.337 | +5.5 / +0.9 / -5.8 |
| Haut dunkel | 0.307 / 0.217 / 0.192 | 0.348 / 0.215 / 0.154 | +4.0 / -0.2 / -3.8 |
| Lippen | 0.469 / 0.289 / 0.276 | 0.588 / 0.257 / 0.246 | +12.0 / -3.2 / -3.0 |
| Himmel | 0.420 / 0.481 / 0.574 | 0.370 / 0.500 / 0.674 | -5.0 / +1.9 / +10.0 |
| Pflanze | 0.280 / 0.331 / 0.259 | 0.244 / 0.427 / 0.208 | -3.6 / +9.6 / -5.1 |
| Holz warm | 0.471 / 0.338 / 0.279 | 0.540 / 0.370 / 0.183 | +6.9 / +3.3 / -9.6 |
| Stoff blau | 0.203 / 0.268 / 0.367 | 0.170 / 0.251 / 0.500 | -3.3 / -1.7 / +13.3 |
| Rot kräftig | 0.476 / 0.215 / 0.173 | 0.694 / 0.174 / 0.132 | +21.8 / -4.1 / -4.1 |
| Gelb | 0.710 / 0.561 / 0.418 | 0.734 / 0.680 / 0.206 | +2.4 / +11.9 / -21.2 |

Mittlere absolute Abweichung: **4.0 Prozentpunkte**, groesste Einzelabweichung: **21.8**.

## Wie das zu lesen ist

**Die Grauachse stimmt.** Über sechs Blenden liegt die freie Kette innerhalb von rund
2 Prozentpunkten — Schwarzpunkt, Mittelgrau, Weiß und der Verlauf dazwischen sind
praktisch deckungsgleich. Das ist der Teil, der über „sieht richtig belichtet aus"
entscheidet, und er ist frei genauso gut zu haben.

**Hauttöne liegen nah beieinander** (unter 6 Prozentpunkten). Die freie Kette ist im
Rotkanal etwas kräftiger und im Blaukanal etwas kühler — im Bild heißt das: eine Spur
mehr Farbe im Gesicht.

**Kräftige Farben gehen auseinander** — bis 22 Prozentpunkte bei sattem Rot und Gelb.
Die gekaufte Finish-LUT entsättigt deutlich stärker, die freie hält mehr Farbe. Das ist
kein Fehler, sondern der Unterschied zwischen zwei Handschriften. Wer näher an die
gedämpfte Variante will, hat zwei Stellschrauben:

* `Key-Ausgabe-Gain` von Node 3 auf 0,55–0,70 erhöhen
* in `lut_finish_kinofarben.py` `SAETTIGUNG_GESAMT` von 0,96 auf etwa 0,88 senken
  und die LUT neu erzeugen

**Was nicht messbar ist:** Filmkorn. Das gekaufte Plugin bringt gemessenes Korn mit,
die freie Variante bekommt es aus dem Film-Look-Erzeuger (`grainIsEnable`). Auf einer
Messtafel aus einfarbigen Flächen fällt der Unterschied nicht auf, im bewegten Bild schon.

## Kurz gesagt

Die freie Kette ist **kein Nachbau** der gekauften und will es nicht sein. Sie trifft
dieselbe Belichtungslage und dieselbe Tonwertkurve und setzt darauf einen eigenen,
etwas farbigeren Look. Für Interviews und Vorträge — ruhiges Licht, ein Gesicht im
Bild, kein Katalog von Motiven — ist das eine tragfähige Grundlage.
