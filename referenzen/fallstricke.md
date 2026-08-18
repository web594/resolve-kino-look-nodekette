# Fallstricke — alles einmal schmerzhaft gelernt

## Projekt und Farbmanagement

**Color Management killt die Filmemulation.** Node 1 erwartet unveränderte Kamerapixel.
Steht das Projekt auf Color Managed, rechnet Resolve das Bild vorher um — die Emulation
bekommt kein Log mehr und der Look kippt. Deshalb **DaVinci YRGB**, Timeline und Ausgabe
`Rec.709 (Scene)`, Eingang `Rec.709 Gamma 2.4`, DRT auf `None`.

**LUT-Interpolation auf „Tetraedrisch" stellen.** Die Voreinstellung ist trilinear; bei
steilen LUTs auf knapp belichtetem oder 8-Bit-Material erzeugt das wandernde Streifen
(Banding) in Verläufen. Die Einstellung ist **nicht** über die Skript-Schnittstelle
erreichbar — ein Klick von Hand, einmal pro Projekt.

**Wiedergabe-Framerate prüfen.** Steht sie nicht auf der Timeline-Framerate, klingt der
Ton verzerrt. Kostet zwei Sekunden und erspart eine lange Fehlersuche in der falschen Ecke.

## Vorlagen (.drx)

**Es stehen nur Nicht-Standardwerte drin.** Ein Parameter, der in der Datei fehlt, steht
auf dem Standard des Plugins — nicht auf 0. Wer eine Kette aus einer `.drx` nachbaut und
nur die gelesenen Werte einträgt, bekommt ein anderes Bild. Deshalb gibt es
[film-look-erzeuger.md](film-look-erzeuger.md) mit dem vollständigen Parametersatz.

**Keyframe-Falle.** Übertragene OFX-Bodies mit keyframe-animierten Parametern werten
außerhalb ihres Quell-Zeitbereichs zu 0 aus: der Effekt hängt sichtbar am Node, rechnet
aber nichts. Vorlagen immer keyframe-frei sichern.

**Ausgeschaltete Nodes gehören nicht in eine Vorlage.** Sonst wandern verworfene Versuche
in jedes neue Projekt mit. Vor dem Sichern aufräumen — oder hinterher mit
`werkzeuge/drx_node_entfernen.py`.

**Motivabhängiges gehört nicht in eine Vorlage.** Power Windows, Qualifizierer,
Sekundärkorrekturen auf einzelne Bildpartien: in einem anderen Motiv sitzen sie falsch.
`ApplyGradeFromDRX` filtert Power Windows ohnehin heraus.

## Schnittstelle

**`ApplyGradeFromDRX` geht nur auf Clip-Ebene.** Auf dem Vor-Clip- oder Nach-Clip-Graphen
einer Farbgruppe liefert es `False` (gemessen, Resolve 21). Die Kette landet also auf den
Clips, nicht in der Gruppe.

**Jedes Anwenden erzeugt eigene geteilte Nodes.** Die Vorlage merkt sich, dass ein Node
geteilt war — aber zweimal angewendet ergibt zwei getrennte Sätze („Shared Node 1–3" und
„Shared Node 4–6"). Echtes Verknüpfen ist Handarbeit: pro Node ein Rechtsklick.

**Nodes lassen sich nicht per Schnittstelle anlegen** und OFX-Plugins nicht setzen. Beides
kommt nur über eine `.drx` ins Projekt. Wer eine Kette ohne ein bestimmtes Plugin braucht,
baut sich die Vorlage um — dafür sind `drx_node_entfernen.py` und
`drx_node_voranstellen.py` da.

**`SetNodeLabel` gibt es nicht.** Beschriftungen stehen aber als Klartext in der `.drx`
und kommen von dort in jedes Projekt mit → `drx_node_beschriften.py`.

**Vor LUT-Zuweisungen `projekt.RefreshLUTList()`** aufrufen (Methode am *Projekt*), sonst
kommt `False` zurück, obwohl die Datei da ist.

**`grade-set` ersetzt den ganzen Node-Baum.** Ohne `--base sicherung.drx` ist die Kette weg.

## Look

**Finish-LUTs nie voll auftragen.** Bei 100 % wirkt das Bild ausgewaschen statt
zurückhaltend. 35–45 % Key-Ausgabe-Gain ist der bewährte Bereich.

**Helligkeit über Gamma, nicht über Gain.** Gain hoch heißt: Gesichter brennen aus. Der
freundliche, helle Eindruck entsteht in den Mitteltönen.

**Am mittleren Frame beurteilen, nicht am Anfang.** Der Anfang eines Mitschnitts ist oft
untypisch — jemand richtet noch das Licht, das Motiv ist noch nicht da.

**Kameras nur über Node 2 angleichen.** Dieselbe neutrale Fläche in beiden Winkeln messen
und die Abweichung dort korrigieren. Eine zusätzliche LUT für eine Kamera macht den
Unterschied dauerhaft unsichtbar — aber auch unkorrigierbar.

**Temporale Effekte nie auf Anpassungsclips legen.** Rauschminderung und Ähnliches
rechnen dort ins Leere und liefern schwarze Bilder — immer auf echte Clips.
