# Roadmap: Elementkonfluenz

Stand: 2026-06-21

Diese Roadmap ordnet die naechsten Schritte nach Risiko und Nutzen. Ziel ist, aus dem aktuellen technischen Kern eine reproduzierbare, erweiterbare und spaeter automatisierbare Short-Video-Pipeline zu machen.

## Phase 0: Stabilisierung

Ziel: Der vorhandene Stand soll reproduzierbar pruefbar werden.

- [ ] GitHub Actions Workflow anlegen
  - [ ] Python-Brain installieren
  - [ ] Python-Import/CLI-Smoke-Test ausfuehren
  - [ ] Renderer mit `npm ci` installieren
  - [ ] Renderer-Typecheck ausfuehren
- [ ] `README.md` um einen Quickstart erweitern
- [ ] Beispiel-ScenePlan sauber dokumentieren
- [ ] Zielauflösung klaeren: 16:9 Debug-Render vs. 9:16 Shorts-Render

Akzeptanzkriterium:

- Ein Pull Request zeigt automatisch, ob Brain und Renderer grundsaetzlich baubar sind.

## Phase 1: Content Engine MVP haerten

Ziel: Ein Video soll aus einem Topic-Brief stabil erzeugt werden koennen.

- [ ] CLI-Ausgabe standardisieren
- [ ] Fehlerfaelle fuer fehlende oder leere Marktdaten sauber behandeln
- [ ] QA-Ergebnisse maschinenlesbar halten
- [ ] ScenePlan-Schema versionieren und validieren
- [ ] Renderer-Fehler bei unvollstaendigem ScenePlan vermeiden
- [ ] 9:16 Composition fuer Shorts/Reels/TikTok ergaenzen

Akzeptanzkriterium:

- Ein ScenePlan fuer mehrere Ticker rendert reproduzierbar als vertikales Short-Video.

## Phase 2: Template-Erweiterung

Ziel: Videos sollen nicht alle gleich aussehen.

- [ ] Bar Race als erstes stabiles Template markieren
- [ ] Line Race Template anlegen
- [ ] Ranking-Tabelle als einfaches zweites Template pruefen
- [ ] Theme-Pool definieren
- [ ] Hook-Intro-Pool definieren
- [ ] Template-Auswahl im ScenePlan abbilden

Akzeptanzkriterium:

- Mindestens zwei Templates koennen aus demselben Datenmodell rendern.

## Phase 3: Trend Engine MVP

Ziel: Das System waehlt ein Thema nicht zufaellig, sondern begruendet aus einem Katalog.

- [ ] `trend-engine` als installierbares Python-Paket oder Script-Struktur anlegen
- [ ] Themen-Katalog als JSON/YAML definieren
- [ ] Cooldown-/Dedup-Speicher per SQLite anlegen
- [ ] Einfaches Scoring implementieren
- [ ] Fallback-Round-Robin implementieren
- [ ] Output-Contract fuer `content-engine` definieren

Akzeptanzkriterium:

- `trend-engine` gibt einen Topic-Brief aus, den `content-engine` direkt verarbeiten kann.

## Phase 4: SEO Engine MVP

Ziel: Jedes produzierte Video bekommt verwertbare Plattform-Metadaten.

- [ ] Input-Contract definieren: Topic, Daten, Hook, Ereignisse, Plattform
- [ ] Regelbasierte Titel fuer YouTube Shorts erzeugen
- [ ] Hashtags pro Plattform erzeugen
- [ ] Beschreibungen fuer YouTube generieren
- [ ] TikTok/Instagram/X-Tonalitaet getrennt behandeln
- [ ] Advisory-Wording-Check wiederverwenden

Akzeptanzkriterium:

- Ein Video-Job erzeugt fuer jede Plattform ein eigenes Metadata-Set.

## Phase 5: Distribution MVP

Ziel: Erst exportieren und planen, dann spaeter posten.

- [ ] Output-Ordnerstruktur definieren
- [ ] Pro Plattform wasserzeichenfreie Exportdatei erzeugen
- [ ] Posting-Plan als JSON/SQLite ablegen
- [ ] Manuellen Review-Schritt einbauen
- [ ] API-Zugaenge separat dokumentieren

Akzeptanzkriterium:

- Ein Produktionslauf erzeugt Video + Metadaten + geplanten Posting-Slot, ohne automatisch live zu posten.

## Phase 6: Automation Loop

Ziel: Aus Einzelproduktion wird ein regelmaessiger Produktionsfluss.

- [ ] Tagesjob definieren
- [ ] Trend-Auswahl -> Content Engine -> SEO Engine -> Distribution verbinden
- [ ] Logging und Fehlerreports einbauen
- [ ] Analytics-Feedback als spaetere Erweiterung vorbereiten

Akzeptanzkriterium:

- Ein trockener Tageslauf erzeugt mehrere publishbare Video-Pakete mit nachvollziehbaren Logs.

## Empfohlener naechster PR nach dieser Roadmap

`ci/bootstrap-quality-checks`

Inhalt:

- `.github/workflows/ci.yml`
- Python-Brain Smoke-Test
- Renderer TypeScript Check
- README Quickstart
