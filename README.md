# Kino-Look in DaVinci Resolve — als 4-Node-Kette

Ein Film-Look für Interviews, Vorträge und Veranstaltungen, aufgebaut so, dass man ihn
nach Monaten noch versteht und in jedes neue Projekt in Sekunden überträgt.

**Der Grundgedanke: drei Nodes bleiben gleich, einer wird eingemessen.**

```
   ┌──────────────┐   ┌──────────────────┐   ┌──────────┐   ┌────────────────────┐
   │ 1 Film-      │   │ 2 Weißabgleich   │   │ 3 Finish │   │ 4 Film-Look-       │
   │   emulation  │──▶│   + Helligkeit   │──▶│   (40 %) │──▶│   Erzeuger         │
   │ bleibt gleich│   │ pro Dreh NEU     │   │ bl. gleich│  │ bleibt gleich      │
   └──────────────┘   └──────────────────┘   └──────────┘   └────────────────────┘
     Log → Rec.709      Belichtung, Farbe      Handschrift    Lichthof + Vignette
```

Die Reihenfolge ist nicht beliebig: Weißabgleich und Grundbelichtung stehen **vor** der
kreativen LUT. Sonst verstärkt die LUT einen Farbstich mit, und man korrigiert am Ende
gegen den eigenen Look an.

## Zwei Wege zum selben Aufbau

|  | Node 1 | Node 3 | Node 4 |
|---|---|---|---|
| **mit gekauften Werkzeugen** (Standard) | Filmemulations-Plugin mit Kameraprofil | gekaufte Finish-LUT bei 40 % | ResolveFX, in Resolve enthalten |
| **kostenlos** (`--frei`) | selbst gerechnete LUT | selbst gerechnete LUT bei 40 % | ResolveFX, in Resolve enthalten |

Die kostenlose Variante ist **kein Nachbau** der gekauften: die LUTs entstehen aus einem
gerechneten Modell (Log-Dekodierung nach veröffentlichter Formel, Negativ- und
Kopierfilm-Kennlinien, Farbtonbänder), nicht aus fremden LUT-Daten. Gemessen liegt sie
auf der Grauachse innerhalb von 2 Prozentpunkten, bei kräftigen Farben bewusst
eigenständig — Zahlen in [`referenzen/messwerte.md`](referenzen/messwerte.md).

## Loslegen

```bash
py werkzeuge/luts_erzeugen.py          # LUTs rechnen
py werkzeuge/luts_installieren.py      # dorthin kopieren, wo Resolve sie findet
py werkzeuge/look_anwenden.py          # Kette auf die Clips legen  (--frei für die kostenlose Variante)
```

Voraussetzungen: DaVinci Resolve Studio (Skript-Schnittstelle aktiv), Python,
`py -m pip install numpy colour-science pillow`.

## Was hier drin ist

| Ordner | Inhalt |
|---|---|
| [`SKILL.md`](SKILL.md) | die Kurzanleitung — auch als Skill für Claude Code nutzbar |
| `vorlagen/` | fertige `.drx`-Ketten (gekauft und frei) inkl. Node-Beschriftungen |
| `luts/` | die selbst gerechneten LUTs |
| `werkzeuge/` | LUT-Generatoren, Übertragung, DRX-Werkzeuge, Messung |
| `referenzen/` | [Nodekette](referenzen/nodekette.md) · [alle Film-Look-Erzeuger-Parameter](referenzen/film-look-erzeuger.md) · [Messwerte](referenzen/messwerte.md) · [gekaufte Werkzeuge](referenzen/gekaufte-werkzeuge.md) · [Fallstricke](referenzen/fallstricke.md) |
| `praesentation/` | Foliensatz, der die Kette grafisch erklärt |

## Werkzeuge, die es so sonst nicht gibt

Resolves Skript-Schnittstelle kann keine Nodes anlegen, keine OFX-Plugins setzen und
keine Nodes beschriften. Alles davon steht aber in einer `.drx`. Deshalb liegen hier
drei kleine Werkzeuge, die eine Grade-Vorlage direkt umbauen:

* `drx_node_entfernen.py` — einen Node herausnehmen, Kette schließt sich
* `drx_node_voranstellen.py` — einen Node kopieren und vorn anhängen (so entsteht die
  freie Variante aus der gekauften, ganz ohne Maus)
* `drx_node_beschriften.py` — Nodes benennen, die Namen wandern in jedes Projekt mit

Dazu `drx_werte.py`, das jede Vorlage im Klartext ausliest — Reglerwerte, OFX-Parameter,
LUT-Zuweisungen —, ohne dass Resolve laufen muss.

## Lizenz und Herkunft

MIT (siehe [LICENSE](LICENSE)). Die gekauften Plugins und LUT-Sätze sind **nicht**
enthalten und werden auch nicht nachgebildet; sie sind in
[`referenzen/gekaufte-werkzeuge.md`](referenzen/gekaufte-werkzeuge.md) nur beschrieben.

Entstanden in der täglichen Arbeit an Mehrkamera-Mitschnitten bei
[wunder-media.de](https://wunder-media.de) — Fragen und Rückmeldungen gern dorthin.
