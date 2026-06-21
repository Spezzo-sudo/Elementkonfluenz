# Roadmap: ValueRacer

Stand: 2026-06-21

Diese Roadmap ordnet die naechsten Schritte nach Risiko und Nutzen. Ziel ist, aus dem aktuellen technischen Kern eine reproduzierbare, erweiterbare und spaeter automatisierbare Short-Video-Pipeline zu machen.

## Phase 0: Stabilisierung und Naming

Ziel: Der vorhandene Stand soll reproduzierbar pruefbar werden und unter dem korrekten Produktnamen `ValueRacer` weiterlaufen.

- [x] GitHub Actions Workflow anlegen
  - [x] Python-Brain installieren
  - [x] Python-Import/CLI-Smoke-Test ausfuehren
  - [x] Renderer mit `npm ci` installieren
  - [x] Renderer-Typecheck ausfuehren
- [x] `README.md` um einen Quickstart erweitern
- [x] Hermes Contract definieren
- [x] Content Standard definieren
- [x] VPS-Migration absichern
- [ ] Produktname und neue Dokumentation auf `ValueRacer` setzen
- [ ] Offene PRs auf alte `Elementkonfluenz`-Nennung pruefen
- [ ] GitHub-Repo optional auf `Spezzo-sudo/ValueRacer` umbenennen
- [ ] VPS-Zielpfad `/srv/valueracer` vorbereiten
- [ ] Beispiel-ScenePlan sauber dokumentieren
- [ ] Zielauflösung klaeren: 16:9 Debug-Render vs. 9:16 Shorts-Render

Akzeptanzkriterium:

- Ein Pull Request zeigt automatisch, ob Brain und Renderer grundsaetzlich baubar sind.
- Neue Dokumentation verwendet `ValueRacer` als Produktnamen.
- Alte Namen sind nur noch als Legacy/Migration markiert.

## Phase 1: Content Engine MVP haerten

Ziel: Ein Video soll aus einem Topic-Brief stabil erzeugt werden koennen.

- [ ] CLI-Ausgabe standardisieren
- [ ] Fehlerfaelle fuer fehlende oder leere Marktdaten sauber behandeln
- [ ] QA-Ergebnisse maschinenlesbar halten
- [ ] ScenePlan-Schema versionieren und validieren
- [ ] Renderer-Fehler bei unvollstaendigem ScenePlan vermeiden
- [ ] 9:16 Composition fuer Shorts/Reels/TikTok ergaenzen
- [ ] Python-Brain-Namespace kontrolliert von `elementkonfluenz_brain` auf ValueRacer-Namespace migrieren oder Alias einfuehren

Akzeptanzkriterium:

- Ein ScenePlan fuer mehrere Ticker rendert reproduzierbar als vertikales Short-Video.
- Legacy-Namensraeume brechen bestehende Hermes-/CI-Flows nicht.

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

`naming/complete-valueracer-followups`

Inhalt:

- offene PRs auf alten Namen pruefen
- Duplicate/obsolete PRs schliessen
- Orchestrator/YouTube-Spec auf ValueRacer-Naming aktualisieren
- danach erst SEO-Dry-Run bauen
