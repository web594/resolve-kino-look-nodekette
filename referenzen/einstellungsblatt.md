# Einstellungsblatt — was genau auf jeden Node kommt

Eine Seite zum Danebenlegen. Links steht, **was** auf den Node kommt (Plugin oder
LUT), rechts, **was man darin noch umstellt**. Alles, was hier nicht steht, bleibt
so, wie ein frisch angelegter Node es anlegt.

Wer die Kette nicht von Hand baut, sondern überträgt:
`py werkzeuge/look_anwenden.py` (`--frei` für die kostenlose Variante). Dann ist
nur noch Node 2 offen.

Die Werte stammen aus den mitgelieferten Vorlagen und lassen sich jederzeit
nachlesen: `py werkzeuge/drx_werte.py vorlagen/kino_look_4nodes_v1.drx`.

---

## Auf einen Blick

| Node | Was drauf kommt (gekauft) | Was drauf kommt (frei) | Was einzustellen ist |
|---|---|---|---|
| 1 Filmemulation | OFX **FilmConvert Nitrate** | LUT `Filmemulation_SLog3_zu_Rec709.cube` | gekauft: Kameraprofil, Filmmaterial, Korn · frei: nichts |
| 2 Weißabgleich + Helligkeit | nichts | nichts | **alles** — pro Dreh und Kamera neu |
| 3 Finish | gekaufte Rec.709-Finish-LUT | LUT `Finish_Kinofarben_Rec709.cube` | Key-Ausgabe-Gain **0,40** |
| 4 Film-Look-Erzeuger | ResolveFX **Film-Look-Erzeuger** | derselbe | Lichthof an, Vignette an, **Bildfenster-Weave AUS** |

---

## Node 1 — Filmemulation

### Variante „gekauft": FilmConvert Nitrate

Auf den Node kommt das OFX-Plugin **FilmConvert Nitrate**
(`com.rubbermonkey:filmconvertnitrate`) — in Resolve auf der Farbseite in der
Effektbibliothek unter „OpenFX → Filter", per Ziehen auf den Node.

**Das stellt man um:**

| Bedienfeld | Wert |
|---|---|
| Camera Settings → Make | der Hersteller der Kamera, z. B. `Sony` |
| Camera Settings → Model | das Modell, z. B. `FS7` |
| Camera Settings → Profile | das Log-Profil, z. B. `S-Log3 S-Gamut3.Cine` |
| Film Settings → Film Stock | `KD 5213 Vis3` (Kunstlicht-Emulsion) |
| Grain → Strength | `15` |
| Grain → Size | `1` (35 mm) |

**Das stellt FilmConvert selbst, sobald das Filmmaterial gewählt ist** — nur zum
Vergleichen, nicht zum Eintippen: Grain Shadows `1,54` · Mid Shadows `13,9` ·
Midtones `16,3` · Mid Highlights `10,5` · Highlights `1,05`. Das ist exakt das
Hundertfache der `OSC Grain Curve` der Emulsion.

**Das bleibt, wie es ist:** Exposure, Temp und Tint auf `0` — die Feinkorrektur
gehört in Node 2, sonst korrigiert man später gegen den eigenen Look an. Tone und
Neutralise auf `0`. Der plugin-eigene Lichthof bleibt aus, der kommt aus Node 4.

> ⚠️ **Die Auswahlfelder speichern einen Listenplatz, keinen Namen — und der Platz
> ist nicht stabil.** Dasselbe Kameraprofil (Profil-Kennung `1306`) stand in drei
> gemessenen Fällen auf `34/46/4`, `33/45/3` und `36/48/6`: Die Liste wächst mit
> jedem zusätzlich installierten Kameraprofil, und alles dahinter rutscht. Deshalb
> **immer nach dem Namen auswählen, nie nachzählen** — und nach dem Übertragen
> einer Vorlage einmal ins Bedienfeld sehen, ob Hersteller, Modell und Profil
> stimmen. Stabil ist allein die `ProfileID`.

### Variante „frei": LUT statt Plugin

Auf den Node kommt die LUT **`Filmemulation_SLog3_zu_Rec709.cube`**
(Rechtsklick auf den Node → LUT → Ordner → Datei). Für Kameras ohne Log-Profil
stattdessen `Filmemulation_Rec709_zu_Rec709.cube`.

**Einzustellen ist nichts.** Korn liefert diese LUT nicht; wer welches möchte,
schaltet es in Node 4 ein (`grainIsEnable`, Standardmenge `0,125`).

---

## Node 2 — Weißabgleich + Helligkeit

**Auf den Node kommt nichts** — kein Plugin, keine LUT. Hier arbeiten nur die
eingebauten Räder.

Das ist der einzige Node, den man pro Dreh und pro Kamera neu einstellt; in den
Vorlagen steht er bewusst neutral. Wie man ihn einmisst, steht in
[nodekette.md](nodekette.md#node-2--weißabgleich--helligkeit): Helligkeit über
**Gamma**, Gain niedrig lassen, auf eine im Bild vorhandene neutrale Fläche
abgleichen — nicht auf das Gesicht.

---

## Node 3 — Finish

### Variante „gekauft"

Auf den Node kommt eine **Rec.709-Finish-LUT aus einem gekauften LUT-Satz** —
in der mitgelieferten Vorlage ist das `PRISMO – Rec709` aus dem Satz
**VisionColor OSIRIS**. Jede andere Finish-LUT tut es genauso; nur muss es die
**Rec.709-Variante** sein, nicht die Log-Variante: Ab Node 1 liegt das Bild
bereits in Rec.709 vor.

Die LUT-Datei selbst liegt aus Lizenzgründen **nicht** in diesem Repo.

### Variante „frei"

Auf den Node kommt **`Finish_Kinofarben_Rec709.cube`** aus `luts/`.

### In beiden Fällen einzustellen

| Bedienfeld | Wert |
|---|---|
| Key → Key-Ausgabe → Gain | **0,40** (Standard 1,0) |

Bei voller Wirkung entsättigt eine Finish-LUT typischerweise zu stark — das Bild
wirkt ausgewaschen statt zurückhaltend. 35–45 % ist der bewährte Bereich. Genau
dafür ist der Key-Ausgabe-Gain da: eine LUT, die man dosieren kann, statt zehn
LUT-Varianten.

---

## Node 4 — Film-Look-Erzeuger

Auf den Node kommt **ResolveFX „Film-Look-Erzeuger"** (englisch *Film Look
Creator*, `com.blackmagicdesign.resolvefx.filmlook`) — in DaVinci Resolve
enthalten, kostet nichts extra.

**Das stellt man um:**

| Bedienfeld | Wert |
|---|---|
| Voreinstellung | `Custom` (statt einer mitgelieferten Voreinstellung) |
| Grundeinstellung → Farbüberblendung | `0,171` |
| Grundeinstellung → Effektüberblendung | `1,0` |
| Film-Look → Film-Look-Überblendung | `0,171` |
| Lichthof → Lichthof aktivieren | **an** |
| Lichthof → Farbton | `0,5` |
| Lichthof → Sättigung | `0,705` |
| Vignette → Vignette aktivieren | **an** |
| Filmkorn | **aus** (in der gekauften Variante kommt das Korn schon aus Node 1) |
| Bildfenster-Weave → aktivieren | **aus** |

> ⚠️ **Bildfenster-Weave ist ab Werk eingeschaltet** (`gateWeaveIsEnable` Standard
> `1`, Intensität `0,25`). Es simuliert das seitliche Wandern des Films im
> Bildfenster — und lässt ein Stativbild wackeln. Wer sich wundert, warum eine
> ruhige Einstellung plötzlich zittert: **zuerst hier nachsehen**, bevor man
> stabilisiert. Die mitgelieferten Vorlagen setzen diesen Schalter nicht, er steht
> darin also auf dem Werkswert „an" — nach dem Übertragen einmal ausschalten.

**Zwei getrennte Regler, und das ist der Trick:** „Farbüberblendung" steuert
Film-Look, Farbeinstellungen und Teiltonung; „Effektüberblendung" steuert
Vignette, Lichthof, Bloom, Filmkorn, Flimmern und Bildfenster. Getrennt dosiert
lässt sich gezielt nur eine Gruppe wirken lassen — hier: Farbe fast aus (17 %),
Effekte voll.

**Nicht im Bedienfeld einstellbar:** Der Kern-Look besteht aus rund 48 weiteren
Werten (Farbkugeln, Teiltonung, Sättigungskurven), die das Bedienfeld gar nicht
zeigt. Die kommen ausschließlich über die `.drx`-Vorlage mit. Wer den Node von
Hand baut, bekommt den Lichthof und die Vignette, aber nicht den Kern-Look — für
den führt kein Weg an `vorlagen/kino_look_4nodes_v1.drx` vorbei. Die vollständige
Liste steht in [film-look-erzeuger.md](film-look-erzeuger.md).

---

## Reihenfolge nicht vertauschen

```
1 Filmemulation  →  2 Weißabgleich + Helligkeit  →  3 Finish (40 %)  →  4 Film-Look-Erzeuger
```

Weißabgleich und Grundbelichtung stehen **vor** der kreativen LUT. Sonst verstärkt
die LUT einen Farbstich mit, und man korrigiert am Ende gegen den eigenen Look an.
