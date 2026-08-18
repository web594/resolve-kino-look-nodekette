# Die gekauften Werkzeuge — was sie sind und warum sie hier nicht beiliegen

Zwei der vier Nodes lassen sich mit gekauften Produkten bestücken. Diese Produkte sind
**nicht Teil dieses Repos** und dürfen es auch nicht sein: sie sind lizenzpflichtig.
Hier steht nur, welche Rolle sie in der Kette spielen — und was an ihre Stelle tritt,
wenn man sie nicht hat.

## Node 1 — Filmemulations-Plugin mit Kameraprofil

**In der Vorlage:** FilmConvert Nitrate (`com.rubbermonkey:filmconvertnitrate`),
OFX-Plugin für die Farbseite.

**Was man dafür bekommt:** vermessene Kameraprofile (Hersteller, Modell, Log-Profil als
Auswahl) und gescannte Filmemulsionen samt Korn. Das Profil nimmt einem die Frage ab,
wie das Log der eigenen Kamera genau dekodiert werden muss — es ist an echtem Material
gemessen, nicht gerechnet.

**Bezug:** Hersteller-Website des jeweiligen Produkts; es gibt vergleichbare Angebote
mehrerer Anbieter.

**Frei stattdessen:** `luts/Filmemulation_SLog3_zu_Rec709.cube`, erzeugt von
`werkzeuge/lut_filmemulation_log_zu_rec709.py`. Die Log-Dekodierung folgt der
veröffentlichten Sony-Formel, die Filmkennlinie einem gerechneten Negativ-Kopierfilm-Modell.
Kein Korn — das kommt bei Bedarf aus Node 4.

## Node 3 — Finish-LUT-Satz

**In der Vorlage:** eine Rec.709-Finish-LUT aus einem gekauften LUT-Satz, aufgetragen
mit 40 % Key-Ausgabe-Gain.

**Was man dafür bekommt:** einen Katalog fertiger Handschriften, aufeinander abgestimmt,
jeweils in Varianten für Log- und Rec.709-Eingang. Wer viele verschiedene Looks braucht,
spart damit Zeit.

**Wichtig:** die Rec.709-Variante nehmen, nicht die Log-Variante — ab Node 1 liegt das
Bild bereits in Rec.709 vor.

**Frei stattdessen:** `luts/Finish_Kinofarben_Rec709.cube`, erzeugt von
`werkzeuge/lut_finish_kinofarben.py`. Eine Handschrift statt eines Katalogs, dafür in
jedem Parameter nachlesbar und änderbar.

## Node 4 — kostet nichts

Der Film-Look-Erzeuger (ResolveFX Film Look Creator) ist in DaVinci Resolve Studio
enthalten. Er liefert Lichthof, Vignette, Bloom, Filmkorn, Flimmern und Bildfenster —
also genau die Effekte, für die man sonst zusätzliche Plugins kauft. In dieser Kette
werden davon nur Lichthof und Vignette genutzt.

## Wie mit den Messwerten umgegangen wurde

Um die freie Variante einzuordnen, wurde die gekaufte Kette **vermessen** (Ausgabewerte
einer synthetischen Messtafel, siehe [messwerte.md](messwerte.md)). Es wurden dabei
**keine fremden LUT-Daten übernommen, umgerechnet oder angenähert**: die freien LUTs
entstehen aus dem Modell in den Generator-Skripten. Der Abgleich beschränkt sich auf die
Belichtungslage — 18-%-Grau auf einen Standardwert zu legen ist eine technische
Festlegung, keine gestalterische Übernahme.
