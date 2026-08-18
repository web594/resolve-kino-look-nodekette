# Node 4 — Film-Look-Erzeuger, alle Einstellungen

Der Film-Look-Erzeuger (ResolveFX Film Look Creator) ist in DaVinci Resolve
enthalten und kostet nichts extra. Er macht in dieser Kette den letzten Schliff:
Lichthof um helle Kanten, Vignette, Teiltonung und die Saettigungskurven.

**Wie diese Tabelle entstanden ist:** Werte in der Spalte *gesetzt* stehen so im
Grade; alle uebrigen Parameter stehen auf Plugin-Standard, der direkt aus dem
OFX-Beschreiber ausgelesen wurde. Neu erzeugen mit
`py werkzeuge/flc_tabelle_erzeugen.py --drx <vorlage.drx> --out <datei.md>`.

Gesetzte Parameter: **58** von **190**.

## Grundeinstellung

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `globalPreset` | Voreinstellungen | GlobalPresetCustom | **gesetzt** |
| `colourBlend` | Farbüberblendung | 0.1705 | **gesetzt** |
| `effectsBlend` | Effektüberblendung | 1 | **gesetzt** |
| `isLutCompatible` | 3D-LUT-kompatibel | 0 | Standard |
| `colorSpaceGroup` | Farbraum außer Kraft setzen | 0 | Standard |
| `inputColorSpace` | Eingabefarbraum | TIMELINE_COLORSPACE | Standard |
| `inputGamma` | Eingabe-Gamma | AUTO_GAMMA | Standard |
| `outputColorSpace` | Ausgabefarbraum | TIMELINE_COLORSPACE | Standard |
| `outputGamma` | Ausgabe-Gamma | AUTO_GAMMA | Standard |
| `outputIlluminat` | Ausgabeweißpunkt | ILLUMINANT_D65 | Standard |

## Film-Look

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `filmLookGroup` | Film-Look | 1 | Standard |
| `filmLookBlend` | Film-Look-Überblendung | 0.1705 | **gesetzt** |
| `filmLookCore` | Kern-Look | CoreLookCinematic | Standard |
| `colorSkinBias` | Hauttendenz | 0 | Standard |

## Farbeinstellungen

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `colorGroup` | Farbeinstellungen | 1 | Standard |
| `colorExposure` | Belichtung | 0 | Standard |
| `colorContrast2` | Kontrast | 1.25 | Standard |
| `colorHighlightThreshold` | Lichter | 0.65 | Standard |
| `colorHighlightRolloff` | Lichter-Rolloff | 0.5 | Standard |
| `colorFadeThreshold` | Auf-/Abblenden | 0 | Standard |
| `colorFadeRolloff` | Abblende-Rolloff | 0.65 | Standard |
| `colorHighlights` | Lichter | 0.35 | Standard |
| `colorFade` | Auf-/Abblenden | 0.285 | Standard |
| `colorSourceWB` | Weißabgleich | 6500 | Standard |
| `colorSourceTint` | Tönung | 10 | Standard |
| `colorPostSat` | Subtraktive Sättigung | 1.2 | Standard |
| `colorRichness` | Kontrastreichtum | 1 | Standard |
| `colorBleachBypass` | Bleichauslassung | 0 | Standard |

## Teiltonung

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `splitGroup` | Teiltonung | 0 | Standard |
| `splitIsEnable` | Teiltonung aktivieren | 0 | Standard |
| `splitToneMode` | Teiltonungsmodus | SplitModeNatural | Standard |
| `splitIsProtectNeutrals` | Neutralfarben erhalten | 0 | Standard |
| `splitAmount` | Intensität | 0 | Standard |
| `splitAngle` | Farbtonwinkel | 20 | Standard |
| `splitPivot` | Drehpunkt | 0.3 | Standard |

## Vignette

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `vignetteGroup` | Vignette | 0 | Standard |
| `vignetteIsEnable` | Vignette aktivieren | 1 | **gesetzt** |
| `vignetteAmount` | Intensität | 0.25 | Standard |
| `vignetteSize` | Größe | 0.25 | Standard |

## Lichthof

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `halationGroup` | Lichthof | 0 | Standard |
| `halationIsEnable` | Lichthof aktivieren | 1 | **gesetzt** |
| `halationIsHighlightsOnly` | Nur Lichter | 1 | Standard |
| `halationAmount` | Intensität | 0.25 | Standard |
| `halationRadius` | Radius | 4 | Standard |
| `halationSat` | Sättigung | 0.7054 | **gesetzt** |
| `halationHue` | Farbton | 0.5 | **gesetzt** |

## Bloom

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `bloomGroup` | Bloom | 0 | Standard |
| `bloomIsEnable` | Bloom aktivieren | 1 | Standard |
| `bloomAmount` | Intensität | 0.25 | Standard |
| `bloomRadius` | Radius | 10 | Standard |

## Filmkorn

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `grainGroup` | Filmkorn | 0 | Standard |
| `grainIsEnable` | Filmkorn aktivieren | 1 | Standard |
| `grainPreset` | Voreinstellung | GrainPreset65 | Standard |
| `grainAmount` | Intensität | 0.125 | Standard |
| `grainSize` | Größe | 0 | Standard |
| `softness` | Weichheit | 0.1 | Standard |
| `grainSaturation` | Sättigung | 0.3 | Standard |
| `grainImageDefocus` | Defokussierung | 1 | Standard |
| `grainIsApplyToBlack` | Auf Schwarz anwenden | 1 | Standard |

## Flimmern

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `flickerGroup` | Flimmern | 0 | Standard |
| `flickerIsEnable` | Flimmern aktivieren | 1 | Standard |
| `flickerAmount` | Intensität | 0.15 | Standard |
| `flickerRate` | Rate | 0.5 | Standard |

## Bildfenster-Weave

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `gateWeaveGroup` | Bildfenster-Weave | 0 | Standard |
| `gateWeaveIsEnable` | Bildfenster-Weave aktivieren | 1 | Standard |
| `gateWeaveAmount` | Intensität | 0.25 | Standard |
| `gateWeaveRate` | Rate | 0.5 | Standard |

## Bildfenster

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `filmGateGroup` | Bildfenster | 0 | Standard |
| `filmGateIsEnable` | Bildfenster aktivieren | 0 | Standard |
| `filmGatePreset` | Voreinstellung | FilmGatePreset1331 | Standard |
| `filmGateRatio` | Verhältnis | {1: 1.3300000429153442, 2: 1.0, 3: 0.0} | Standard |
| `filmGateIsCurved` | Krümmung aktivieren | 1 | Standard |
| `filmGateSoftness` | Weichheit | 0.2 | Standard |
| `filmGatePadding` | Padding | 0 | Standard |
| `isFirstLoad` | INTERNAL | 0 | **gesetzt** |

## Innere Werte des Kern-Looks (kein Bedienfeld)

| Parameter | Bedienfeld | Wert | Quelle |
|---|---|---|---|
| `flPreSat` | PreSaturation | 0.7 | **gesetzt** |
| `flTetraGroup` | Tetra | 1 | Standard |
| `flTetraRedX` | Red X | 1 | Standard |
| `flTetraRedY` | Red Y | 0.03 | Standard |
| `flTetraRedZ` | Red Z | 0 | Standard |
| `flTetraGrnX` | Grn X | 0 | Standard |
| `flTetraGrnY` | Grn Y | 1.3 | Standard |
| `flTetraGrnZ` | Grn Z | 0.3 | Standard |
| `flTetraBluX` | Blu X | -0.15 | Standard |
| `flTetraBluY` | Blu Y | 0 | Standard |
| `flTetraBluZ` | Blu Z | 1 | Standard |
| `flTetraCynX` | Cyn X | 0 | Standard |
| `flTetraCynY` | Cyn Y | 1 | Standard |
| `flTetraCynZ` | Cyn Z | 1 | Standard |
| `flTetraMagX` | Mag X | 1.2 | Standard |
| `flTetraMagY` | Mag Y | 0 | Standard |
| `flTetraMagZ` | Mag Z | 1 | Standard |
| `flTetraYelX` | Yel X | 1 | Standard |
| `flTetraYelY` | Yel Y | 0.8 | Standard |
| `flTetraYelZ` | Yel Z | 0.2 | Standard |
| `flSphAxis0` | Sph Axis 0 | 1 | Standard |
| `flSphCenter0` | Center | 0 | **gesetzt** |
| `flSphHueWid0` | HueWidth | 60 | **gesetzt** |
| `flSphRot0` | Rotate | 2 | **gesetzt** |
| `flSphSat0` | Sat | 1.1 | **gesetzt** |
| `flSphBright0` | Bright | -0.25 | **gesetzt** |
| `flSphAxis1` | Sph Axis 1 | 1 | Standard |
| `flSphCenter1` | Center | 20 | **gesetzt** |
| `flSphHueWid1` | HueWidth | 20 | **gesetzt** |
| `flSphRot1` | Rotate | 5 | **gesetzt** |
| `flSphSat1` | Sat | 1 | **gesetzt** |
| `flSphBright1` | Bright | -0.75 | **gesetzt** |
| `flSphAxis2` | Sph Axis 2 | 1 | Standard |
| `flSphCenter2` | Center | 60 | **gesetzt** |
| `flSphHueWid2` | HueWidth | 60 | **gesetzt** |
| `flSphRot2` | Rotate | 15 | **gesetzt** |
| `flSphSat2` | Sat | 2 | **gesetzt** |
| `flSphBright2` | Bright | -1 | **gesetzt** |
| `flSphAxis3` | Sph Axis 3 | 1 | Standard |
| `flSphCenter3` | Center | 120 | **gesetzt** |
| `flSphHueWid3` | HueWidth | 60 | **gesetzt** |
| `flSphRot3` | Rotate | -30 | **gesetzt** |
| `flSphSat3` | Sat | 1 | **gesetzt** |
| `flSphBright3` | Bright | -2 | **gesetzt** |
| `flSphAxis4` | Sph Axis 4 | 1 | Standard |
| `flSphCenter4` | Center | 200 | **gesetzt** |
| `flSphHueWid4` | HueWidth | 60 | **gesetzt** |
| `flSphRot4` | Rotate | -2 | **gesetzt** |
| `flSphSat4` | Sat | 1 | **gesetzt** |
| `flSphBright4` | Bright | 0 | **gesetzt** |
| `flSphAxis5` | Sph Axis 5 | 1 | Standard |
| `flSphCenter5` | Center | 240 | **gesetzt** |
| `flSphHueWid5` | HueWidth | 60 | **gesetzt** |
| `flSphRot5` | Rotate | 5 | **gesetzt** |
| `flSphSat5` | Sat | 1.2 | **gesetzt** |
| `flSphBright5` | Bright | -0.42 | **gesetzt** |
| `flSphAxis6` | Sph Axis 6 | 1 | Standard |
| `flSphCenter6` | Center | 300 | **gesetzt** |
| `flSphHueWid6` | HueWidth | 60 | **gesetzt** |
| `flSphRot6` | Rotate | 0 | **gesetzt** |
| `flSphSat6` | Sat | 0.9 | **gesetzt** |
| `flSphBright6` | Bright | -0.59 | **gesetzt** |
| `flSplitToneGroup` | Split Tone Group | 1 | Standard |
| `flSplitToneBlend` | SplitToneBlend | 0.5 | **gesetzt** |
| `flSplitToneMidPnt` | SplitToneMidPnt | 0.336 | **gesetzt** |
| `flSplitToneTargetTopHSVX` | SplitToneTargetTopHSV X | 0.225 | Standard |
| `flSplitToneTargetTopHSVY` | SplitToneTargetTopHSV Y | 0.4 | Standard |
| `flSplitToneTargetTopHSVZ` | SplitToneTargetTopHSV Z | 1 | Standard |
| `flSplitToneTargetBotHSVX` | SplitToneTargetBotHSV X | 0.515 | Standard |
| `flSplitToneTargetBotHSVY` | SplitToneTargetBotHSV Y | 0.6 | Standard |
| `flSplitToneTargetBotHSVZ` | SplitToneTargetBotHSV Z | 0.37 | Standard |
| `flLiftGammaGainRGB` | Lift Gamma Gain RGB | 1 | Standard |
| `flLiftRGBX` | LiftRGB X | 0 | Standard |
| `flLiftRGBY` | LiftRGB Y | 0 | Standard |
| `flLiftRGBZ` | LiftRGB Z | 0 | Standard |
| `flGammaRGBX` | GammaRGB X | 1 | Standard |
| `flGammaRGBY` | GammaRGB Y | 1 | Standard |
| `flGammaRGBZ` | GammaRGB Z | 1 | Standard |
| `flGainRGBX` | GainRGB X | 1 | Standard |
| `flGainRGBY` | GainRGB Y | 1 | Standard |
| `flGainRGBZ` | GainRGB Z | 1 | Standard |
| `flSGroup` | Interpolation ranges for Skin Bias | 1 | Standard |
| `flSRotateX` | SRotate X | 10 | Standard |
| `flSRotateY` | SRotate Y | 5 | Standard |
| `flSRotateZ` | SRotate Z | 0 | Standard |
| `flSSatX` | SSat X | 1.15 | Standard |
| `flSSatY` | SSat Y | 1 | Standard |
| `flSSatZ` | SSat Z | 0.85 | Standard |
| `flSBrightX` | SBright X | -4 | Standard |
| `flSBrightY` | SBright Y | -0.75 | Standard |
| `flSBrightZ` | SBright Z | 0.75 | Standard |
| `vsGroup` | VS Group | 1 | Standard |
| `satVsSatCurveBot` | Sat Vs Sat Bot | 1.2 | **gesetzt** |
| `satVsSatCurveLow` | Sat Vs Sat Low | 1.2 | **gesetzt** |
| `satVsSatCurveHigh` | Sat Vs Sat High | 0.5 | **gesetzt** |
| `satVsSatCurveTop` | Sat Vs Sat Top | 0 | **gesetzt** |
| `satVsSat` | Sat Vs Sat | 0.9 | **gesetzt** |
| `lumVsSatCurveBot` | Lum Vs Sat Bot | 1.6 | **gesetzt** |
| `lumVsSatCurveLow` | Lum Vs Sat Low | 1.2 | **gesetzt** |
| `lumVsSatCurveHigh` | Lum Vs Sat High | 0.9 | **gesetzt** |
| `lumVsSatCurveTop` | Lum Vs Sat Top | 0.4 | **gesetzt** |
| `lumVsSat` | Lum Vs Sat | 0.85 | **gesetzt** |
| `isLegacyIgnoreAlphaIn` | INTERNAL | 0 | Standard |
| `IsLegacyContrastRolloffs` | INTERNAL | 0 | Standard |
| `isLegacyDiscontinuities` | INTERNAL | 0 | Standard |
| `IsLegacyAlwaysClampForCoreLook` | INTERNAL | 0 | Standard |
| `blendGroup` | Global überblenden | 0 | Standard |
| `blendIn` | Überblenden | 1 | Standard |
| `blend` | Überblenden | 0 | Standard |
| `ignoreContentShape` | Legacy Content Fit | 0 | Standard |
| `legacyIsProcessRGBOnly` | Ignore the alpha channel in and out | 0 | Standard |
| `IsNoTemporalFramesReqd` | INTERNAL | 0 | Standard |
| `srcProcessingAlphaMode` | Integer tied to OFX::PreMultiplicationEnum | -1 | Standard |
| `dstProcessingAlphaMode` | Integer tied to OFX::PreMultiplicationEnum | -1 | Standard |
| `resolvefxVersion` | resolvefxVersion | 1.6 | **gesetzt** |
