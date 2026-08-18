# Die vier Nodes im Einzelnen

Alle Werte sind aus der mitgelieferten Vorlage ausgelesen. Neu auslesen jederzeit:

```bash
py werkzeuge/drx_werte.py vorlagen/kino_look_4nodes_v1.drx
```

---

## Node 1 — Filmemulation

**Aufgabe:** das Log-Signal der Kamera dekodieren *und* ihm in einem Schritt die
Kennlinie eines Kinofilms geben. Beides gehört zusammen, weil eine Filmkennlinie nur
dann stimmt, wenn sie auf echtem Szenenlicht sitzt.

Danach liegt das Bild in Rec.709 vor — alles Weitere in der Kette rechnet in Rec.709.

### Variante „gekauft": Filmemulations-Plugin

`com.rubbermonkey:filmconvertnitrate` — die im Grade gesetzten Werte:

| Parameter | Wert | Bedeutung |
|---|---|---|
| `Make` / `Model` / `Profile` | 34 / 46 / 4 | Kamerahersteller, Modell, Log-Profil (**Indizes**) |
| `ProfileID` | 1306 | eindeutige Profilkennung |
| `Film Stock` | 2 | Emulsion (Kunstlicht) |
| `Grain Strength` / `Grain Size` | 15,0 / 1,0 | Kornstärke, 35 mm |
| `Grain Shadows` … `Grain Highlights` | 1,54 / 13,9 / 16,3 / 10,5 / 1,05 | Kornverteilung über die Tonwerte |
| `OSC Grain Curve` | `0.0154\|0.139\|0.163\|0.105\|0.0105` | dieselbe Verteilung als Kurve |

Belichtung, Temperatur und Tönung stehen im Plugin bewusst auf 0 — die Feinkorrektur
passiert erst in Node 2. Der plugin-eigene Lichthof bleibt ungenutzt; er kommt
kostenlos aus Node 4.

⚠️ Die Auswahlfelder sind **Indizes, keine Namen**. Bei einer anderen Plugin-Version
kann sich die Zuordnung verschieben — nach dem Übertragen einmal im Bedienfeld prüfen.

### Variante „frei": `Filmemulation_SLog3_zu_Rec709.cube`

Gerechnet von `werkzeuge/lut_filmemulation_log_zu_rec709.py`:
Log → Szenenlicht → Negativdichte je Schicht → Schichtkopplung → Kopierfilm →
Durchlässigkeit → Rec.709. Für Kameras ohne Log-Profil gibt es
`Filmemulation_Rec709_zu_Rec709.cube`.

Gemessene Kennwerte (Graukeil, Grünkanal):

| Szene | −3 Bl. | −2 Bl. | −1 Bl. | 18 % | +1 Bl. | +2 Bl. | +3 Bl. | 90 % Weiß |
|---|---|---|---|---|---|---|---|---|
| Ausgabe | 0,102 | 0,181 | 0,311 | 0,488 | 0,671 | 0,812 | 0,898 | 0,845 |

Schwarz landet nicht auf 0 (Filmschwarz), Weiß nicht auf 1 (weiche Schulter).

---

## Node 2 — Weißabgleich + Helligkeit

**Der einzige Node, der pro Dreh und pro Kamera neu eingestellt wird.** In der Vorlage
steht er neutral, damit nichts Ungewolltes mitkommt.

| Regler | neutral | typischer Bereich | wofür |
|---|---|---|---|
| `offsetR/G/B` (gleich) | 25,0 | 10–25 | Schwarzpunkt |
| `gainM` | 1,0 | 0,90–1,05 | Lichter, niedrig halten |
| `gammaM` | 0,0 | −0,05 … +0,10 | **hier** wird das Bild hell und freundlich |
| `temp` | 0 | −80 … +80 | Farbtemperatur |
| `toenung` | 0 | −25 … +25 | Grün/Magenta |

Ein Beispiel aus einem Innenraum mit warmem Kunstlicht: Offset gleichmäßig von 25 auf
11 (Schwarzpunkt heruntergezogen), `gainM` 0,93, `temp` +61, `toenung` −19. Das sind
**Größenordnungen, keine Sollwerte** — bei anderem Licht sieht es anders aus.

Setzen lässt sich das ohne Maus, z. B. mit dem Werkzeugkasten aus dem verwandten
Repo `resolve-multicam-workflow`:

```bash
py rctl.py grade-save sicherung.drx
py rctl.py grade-set gainM=0.93 temp=60 toenung=-19 --base sicherung.drx
```

⚠️ `grade-set` ersetzt den ganzen Node-Baum — ohne `--base` ist die Kette weg.

---

## Node 3 — Finish

**Aufgabe:** die gestalterische Handschrift. Sitzt bewusst **hinter** dem Weißabgleich.

```
Key-Ausgabe-Gain = 0,40        (Parameter-Kennung 0x0c30001d)
```

Bei 100 % Wirkung entsättigt eine Finish-LUT typischerweise zu stark — das Bild wirkt
ausgewaschen statt zurückhaltend. **35–45 % ist der bewährte Bereich.** Genau dafür ist
der Key-Ausgabe-Gain da: eine LUT, die man dosieren kann, statt zehn LUT-Varianten.

### Variante „frei": `Finish_Kinofarben_Rec709.cube`

Gerechnet von `werkzeuge/lut_finish_kinofarben.py`:

1. weiche Kontrastkurve um Mittelgrau (Drehpunkt 0,42), Lichter laufen weich aus
2. Schwarz leicht angehoben
3. Grün und Cyan entsättigt — Hintergrund und Wandfarben werden ruhig
4. Rot Richtung Orange gedreht — Hauttöne bekommen Wärme
5. Lichter warm, tiefe Schatten leicht kühl
6. Gesamtsättigung leicht zurück

Gemessen (volle LUT, in der Kette wirkt sie nur zu 40 %):

| Probe | Sättigung vorher → nachher | Farbton vorher → nachher |
|---|---|---|
| Rot | 0,714 → 0,759 | 0° → 8° |
| Grün | 0,714 → 0,446 | 120° → 113° |
| Blau | 0,714 → 0,656 | 240° → 232° |
| Hautton | 0,417 → 0,438 | 24° → 29° |

---

## Node 4 — Film-Look-Erzeuger

In DaVinci Resolve enthalten, kostet nichts extra. In dieser Kette macht er den
letzten Schliff: **Lichthof (Halation)** um helle Kanten und **Vignette**.

Die wichtigsten gesetzten Werte:

| Parameter | Wert | Bedeutung |
|---|---|---|
| `globalPreset` | `GlobalPresetCustom` | eigene Einstellung statt Voreinstellung |
| `colourBlend` / `filmLookBlend` | 0,1705 | Farbanteil sehr zurückhaltend |
| `effectsBlend` | 1,0 | Effektanteil voll |
| `halationIsEnable` | 1 | Lichthof an |
| `halationHue` / `halationSat` | 0,5 / 0,705 | Farbton und Sättigung des Lichthofs |
| `vignetteIsEnable` | 1 | Vignette an |
| `flPreSat` | 0,7 | Sättigung vor dem Kern-Look |
| `lumVsSat` | 0,85 | Sättigung über Helligkeit (Kurve 1,6/1,2/0,9/0,4) |
| `satVsSat` | 0,9 | Sättigung über Sättigung (Kurve 1,2/1,2/0,5/0,0) |
| `flSplitToneBlend` / `flSplitToneMidPnt` | 0,5 / 0,336 | Teiltonung |
| `flSph*` (7 Farbtonbänder) | Mitten 0/20/60/120/200/240/300° | Farbcharakter des Kern-Looks |

**Zwei getrennte Regler, und das ist der Trick:** „Farbüberblendung" steuert Film-Look,
Farbeinstellungen und Teiltonung; „Effektüberblendung" steuert Vignette, Lichthof,
Bloom, Filmkorn, Flimmern und Bildfenster. Getrennt dosiert lässt sich gezielt nur eine
Gruppe wirken lassen — hier: Farbe fast aus (17 %), Effekte voll.

Filmkorn ist hier bewusst **aus**. In der gekauften Variante kommt das Korn schon aus
Node 1; wer die freie Variante nutzt und Korn möchte, schaltet es hier ein
(`grainIsEnable`, `grainAmount` 0,125 ist der Standard).

**Die vollständige Tabelle aller 190 Parameter** — gesetzte Werte und Plugin-Standards —
steht in [film-look-erzeuger.md](film-look-erzeuger.md).
