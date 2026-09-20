---
name: resolve-kino-look-nodekette
description: Kino-/Film-Look in DaVinci Resolve als schlanke Kette aus vier Nodes — drei mit fest bleibenden Einstellungen (Filmemulation, Finish-LUT, Film-Look-Erzeuger) und einer für Weißabgleich und Helligkeit, der pro Dreh neu eingemessen wird. Mit Skripten, die die Kette in Sekunden übertragen, die Nodes beschriften und die nötigen LUTs selbst erzeugen — wahlweise mit gekauften Werkzeugen oder komplett kostenlos. Nutzen bei "Kino-Look", "Filmlook anwenden", "Grading-Kette aufbauen", "Look auf alle Kameras", "Node-Kette übertragen", "FilmConvert", "Film-Look-Erzeuger", "Halation/Lichthof", "S-Log3 nach Rec.709", "Filmemulation", "Look ohne gekaufte Plugins".
---

# Kino-Look als 4-Node-Kette

Ein Film-Look für Interviews, Vorträge und Veranstaltungen — aufgebaut so, dass man ihn
nach Monaten noch versteht und in jedes neue Projekt in Sekunden übernimmt.

**Der Grundgedanke: drei Nodes bleiben gleich, einer wird eingemessen.**

| # | Node | Art | bleibt gleich? | Aufgabe |
|---|---|---|---|---|
| 1 | **Filmemulation** | Plugin oder LUT | ✅ ja | Log dekodieren und die Kennlinie eines Kinofilms geben |
| 2 | **Weißabgleich + Helligkeit** | Primärkorrektur | ❌ pro Dreh/Kamera | Belichtung und Farbtemperatur des Motivs |
| 3 | **Finish** | LUT, gedrosselt | ✅ ja | die gestalterische Handschrift |
| 4 | **Film-Look-Erzeuger** | ResolveFX | ✅ ja | Lichthof (Halation) und Vignette |

Die Reihenfolge ist nicht beliebig: **Weißabgleich und Grundbelichtung stehen VOR der
kreativen LUT.** Sonst verstärkt die LUT einen vorhandenen Farbstich mit, und man
korrigiert am Ende gegen den eigenen Look an.

## Von Hand bauen? → Einstellungsblatt

Wer die Kette nicht überträgt, sondern selbst aufbaut, braucht genau eine Seite:
**[referenzen/einstellungsblatt.md](referenzen/einstellungsblatt.md)** — Node für Node,
welches Plugin bzw. welche LUT darauf kommt und welche Werte darin umzustellen sind.

## Schnellstart

```bash
py werkzeuge/luts_erzeugen.py && py werkzeuge/luts_installieren.py
```

```bash
py werkzeuge/look_anwenden.py
```

Setzt die Projekt-Farbeinstellungen und legt die Kette auf die Clips aller Timelines,
deren Name „import" enthält. Optionen: `--timeline <fragment>` (mehrfach) ·
`--frei` (Variante ohne gekaufte Werkzeuge) · `--gruppe "Kino-Look"` ·
`--nur-einstellungen`.

## Voraussetzung: Projekt auf DaVinci YRGB

| Einstellung | Wert |
|---|---|
| `colorScienceMode` | `davinciYRGB` — **nicht** Color Managed |
| `colorSpaceTimeline` / `colorSpaceOutput` | `Rec.709 (Scene)` |
| `colorSpaceInput` | `Rec.709 Gamma 2.4` |
| `inputDRT` / `outputDRT` | `None` |
| LUT-Interpolation | **Tetraedrisch** — ❌ nicht über die Schnittstelle, einmal in der Oberfläche |

⚠️ Node 1 erwartet **unveränderte Kamerapixel**. Unter Color Management rechnet Resolve
das Bild vorher um; die Filmemulation bekäme dann kein Log mehr und der Look kippt.

## Zwei Varianten, dieselbe Kette

|  | Node 1 | Node 3 | Node 4 |
|---|---|---|---|
| **gekauft** (Standard) | Filmemulations-Plugin mit Kameraprofil | gekaufte Finish-LUT bei 40 % | ResolveFX (kostenlos) |
| **frei** (`--frei`) | `Filmemulation_SLog3_zu_Rec709.cube` | `Finish_Kinofarben_Rec709.cube` bei 40 % | ResolveFX (kostenlos) |

Beide Vorlagen liegen fertig in `vorlagen/`. Die freien LUTs erzeugt
`werkzeuge/luts_erzeugen.py` aus dem Modell — es werden **keine fremden LUT-Daten
gelesen oder angenähert**. Gemessener Vergleich: auf der Grauachse unter 2
Prozentpunkte Abweichung, bei kräftigen Farben deutlich mehr — Einzelheiten in
`referenzen/messwerte.md`.

**Empfehlung:** wer die gekauften Werkzeuge hat, nimmt sie. Die freie Variante ist
kein Ersatzteil, sondern ein eigenständiger, sauber gerechneter Look — und für
Kameras ohne Log-Profil oft die praktischere Wahl
(`Filmemulation_Rec709_zu_Rec709.cube`).

## Node 2 — der einzige Node, den man einstellt

Alles Motivabhängige gehört hierher und **nirgendwo sonst hin**. Wer die Helligkeit
in der LUT korrigiert, verliert die Vergleichbarkeit zwischen Kameras.

| Regler | Richtung | Hinweis |
|---|---|---|
| Offset (R/G/B gleich) | Schwarzpunkt | Tiefen nicht auf 0 drücken — eine Bodenschwelle lassen |
| Gain (Master) | Lichter | niedrig halten, sonst brennen Gesichter aus |
| Gamma / Mitteltöne | Helligkeit | **hier** wird das Bild hell und freundlich, nicht über Gain |
| Temperatur / Tönung | Weißabgleich | an einer echten neutralen Fläche im Bild messen |

Zielwerte: Hauttöne im Vektorskop auf der Hautton-Linie, auf der Wellenform etwa
55–70 %. Zwei Kameras gleicht man **nur über Node 2 der Nebenkamera** an — dieselbe
neutrale Fläche in beiden Winkeln messen, nie eine zusätzliche LUT dazwischenschieben.

⚠️ Ob heller oder dunkler, wärmer oder kühler *richtig* ist, entscheidet der Mensch.
Werte vorschlagen, Richtung bestätigen lassen.

## ⭐ Wer macht was

Faustregel: **Skript macht alles, was Zahl, Pfad oder Struktur ist. Der Mensch macht
alles, was Zeigen oder Beurteilen ist.**

| Aufgabe | per Skript | von Hand | Wer |
|---|---|---|---|
| Ganze Kette inkl. Plugin/LUT/Werten anlegen | Sekunden | 5–15 min je Clip | ✅ Skript |
| Kette auf alle Kameras verteilen | Schleife | ×N | ✅ Skript |
| Nodes beschriften | `drx_node_beschriften.py` | Doppelklick ×4 | ✅ Skript |
| Node aus einer Vorlage entfernen | `drx_node_entfernen.py` | — | ✅ Skript |
| Projekt-Farbeinstellungen | `SetSetting` | Dialog | ✅ Skript |
| Frames ziehen, Kameras gegeneinander messen | Rechnung | Auge | ✅ Skript |
| Weißabgleich/Helligkeit **beurteilen** | — | — | ❌ Mensch |
| Nodes zu echten geteilten Nodes verknüpfen | geht nicht | Rechtsklick ×3 | ❌ Mensch |
| LUT-Interpolation tetraedrisch | geht nicht | 1 Klick | ❌ Mensch |
| Sekundärkorrekturen mit Fenster/Qualifizierer | motivabhängig | 1–3 min | ❌ Mensch |

⛔ **Nie per Bildschirmsteuerung nachbauen.** Eine Kette zusammenzuklicken dauert über
eine Stunde und wird ungenau — die Vorlage überträgt sie exakt.

## Ablauf für ein neues Projekt

1. **LUTs bereitstellen** — `luts_erzeugen.py`, dann `luts_installieren.py` (einmalig).
2. **Farbeinstellungen setzen** — `look_anwenden.py --nur-einstellungen`.
3. **Kette übertragen** — `look_anwenden.py` (ggf. `--frei`).
4. **Node 2 einmessen** — Frame aus der *Mitte* des Materials ziehen, nicht vom Anfang;
   Werte vorschlagen, Richtung vom Menschen bestätigen lassen.
5. **Kameras vergleichen** — dieselbe neutrale Fläche in allen Winkeln messen.
6. **Geteilte Nodes verknüpfen** und **LUT-Interpolation tetraedrisch** — beides von Hand.
7. **Gegenprüfen** — Frame rendern und messen, nicht nur schauen.

## Eine eigene Vorlage aus einem fertigen Grade gewinnen

Grade in Resolve als `.drx` sichern, dann aufräumen:

```bash
py werkzeuge/drx_node_entfernen.py fertig.drx sauber.drx --label "Gesicht"
py werkzeuge/drx_node_beschriften.py sauber.drx vorlage.drx "1 Filmemulation" "2 Weissabgleich + Helligkeit" "3 Finish" "4 Film-Look-Erzeuger"
py werkzeuge/drx_werte.py vorlage.drx
```

Motivabhängige Sekundärkorrekturen (Fenster, Qualifizierer, einzelne Bildpartien)
gehören **nicht** in eine Vorlage — in einem anderen Motiv sitzen sie falsch.

## Fallstricke

- ⚠️ **In einer .drx stehen nur Nicht-Standardwerte.** Ein fehlender Parameter steht auf
  Plugin-Standard, nicht auf 0. Deshalb die vollständige Tabelle in
  `referenzen/film-look-erzeuger.md`.
- ⚠️ **Keyframe-Falle:** übertragene OFX-Bodies mit keyframe-animierten Parametern werten
  außerhalb ihres Quell-Zeitbereichs zu 0 aus — der Effekt hängt am Node, rechnet aber
  nichts. Vorlagen immer keyframe-frei sichern.
- ⚠️ **`ApplyGradeFromDRX` funktioniert nur auf Clip-Ebene.** Auf den Vor-/Nach-Clip-Graphen
  einer Farbgruppe liefert es `False` (gemessen, Resolve 21).
- ⚠️ **Jedes Anwenden erzeugt eigene geteilte Nodes.** Die Vorlage merkt sich, dass ein Node
  geteilt war, aber zwei Anwendungen ergeben zwei getrennte Sätze — verknüpfen ist Handarbeit.
- ⚠️ **Ausgeschaltete Nodes gehören nicht in eine Vorlage** — sonst wandern verworfene
  Versuche mit.
- ⚠️ Vor LUT-Zuweisungen `projekt.RefreshLUTList()`, sonst kommt `False` zurück.
- ⚠️ Die Auswahlfelder eines Kamera-Plugins sind **Indizes, keine Namen**. Nach dem
  Übertragen einmal prüfen, ob Kamera, Modell und Profil zum Material passen.

## Was wo liegt

| Ordner | Inhalt |
|---|---|
| `vorlagen/` | die fertigen `.drx`-Ketten (gekauft und frei) |
| `luts/` | die selbst gerechneten LUTs |
| `werkzeuge/` | LUT-Generatoren, Übertragung, DRX-Werkzeuge, Messung |
| `referenzen/` | **[einstellungsblatt.md](referenzen/einstellungsblatt.md)** — was auf jeden Node kommt und was darin einzustellen ist · Werte je Node, Messwerte, Fallstricke, gekaufte Werkzeuge |
| `praesentation/` | Foliensatz, der die Kette grafisch erklärt |

Fragen zur Anwendung in der Praxis: [wunder-media.de](https://wunder-media.de)
