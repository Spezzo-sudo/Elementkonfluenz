# Hermes Contract

Stand: 2026-06-21

Dieses Dokument definiert, wie Hermes spaeter **ValueRacer** auf dem VPS automatisiert steuern soll. Ziel ist eine einfache, robuste Orchestrierung: klare Befehle, klare Input-/Output-Dateien, keine versteckten manuellen Schritte und keine Datenverluste.

## Naming

- Produktname: `ValueRacer`
- Empfohlener VPS-Pfad: `/srv/valueracer`
- Alter Arbeitsname: `Elementkonfluenz`

Der alte Name kann noch in historischen Commits, offenen PRs oder internen Python-Paketnamen vorkommen. Neue Deployments, Run-Pfade und Hermes-Konfigurationen sollen ab jetzt `ValueRacer` verwenden.

## Leitprinzipien

1. Hermes ruft Module ueber stabile CLIs auf, nicht ueber interne Python-/TypeScript-Implementierungsdetails.
2. Jedes Modul liest Input-Dateien und schreibt Output-Dateien.
3. Jeder Produktionslauf schreibt in einen eigenen Run-Ordner.
4. Jeder Schritt liefert ein maschinenlesbares Ergebnis.
5. Fehler stoppen die Pipeline sicher und nachvollziehbar.
6. Auto-Posting bleibt deaktiviert, bis Dry-Runs mehrfach erfolgreich und manuell geprueft wurden.
7. Bestehende VPS-Daten werden niemals ungefragt ueberschrieben oder geloescht.
8. Bestehende Hermes-Secrets und `.env`-Dateien werden gelesen, aber nicht automatisch neu erzeugt, rotiert oder ueberschrieben.

## Aktueller sicherer Dry-Run

Der aktuell implementierte sichere Hermes-Loop fuer ein manuelles Thema ist:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode manual_topic \
  --with-youtube-seo \
  --with-qa \
  --topic "Gold vs S&P 500" \
  --out runs/<job_id>
```

Der aktuell implementierte sichere Hermes-Loop fuer automatische Katalogauswahl ist:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode market_scan \
  --with-youtube-seo \
  --with-qa \
  --out runs/<job_id>
```

Dieser Loop erzeugt:

```text
topic_brief.json
sources.json
metadata/youtube.json
publish/youtube_publish_plan.json
qa.json
job_result.json
logs/orchestrator.log
```

Er postet nichts, liest keine Secrets, rendert nichts und setzt `ready_to_publish` nicht auf true. Wenn QA `hard_fail=true` meldet, setzt der Orchestrator `job_result.ok=false`, `stage=qa` und `error_code=QA_HARD_FAIL`.

## Run Modes

Die konkreten Betriebsarten sind in `orchestration/RUN_MODES.md` definiert.

Aktuelle und geplante Modi:

```text
manual_topic  -> Nutzer/Hermes gibt Thema vor
market_scan   -> ValueRacer waehlt aus Markt-/Asset-Katalog
trend_scan    -> ValueRacer waehlt aus Trend-/Nachfrage-Signalen
rerun_failed  -> Hermes wiederholt technische Fehler, wenn retryable=true
```

`manual_topic` und `market_scan` sind aktuell als Dry-Run implementiert. `trend_scan` ist eine definierte naechste Ausbaustufe.

## QA Gates

Die Qualitaetsregeln sind in `orchestration/QA_GATES.md` definiert. Die erste `qa-engine` Implementierung schreibt `qa.json` direkt im Run-Ordner.

Minimum-Regel:

```text
qa.hard_fail == true  -> niemals publishen
requires_review=true  -> Review melden
ready_to_publish=false -> nicht publishen
```

## Rotation und Cooldown

Wiederholungs- und Abwechslungsregeln sind in `orchestration/ROTATION_AND_COOLDOWN.md` definiert.

Ziel:

- keine doppelte Story innerhalb des Cooldowns
- keine gleiche Asset-Kombination zu oft
- nicht immer derselbe Video-Typ
- nicht immer dieselbe Hook-Struktur

## VPS-Schnittstelle

Die Verbindung zwischen bestehendem VPS/Hermes und diesem Repository ist in `orchestration/HERMES_VPS_INTERFACE.md` definiert.

Wichtig:

- vorhandenes VPS-Projekt `ValueRacer` nicht blind ueberschreiben
- zuerst inventarisieren
- Backups anlegen
- parallel testen
- erst danach verbinden

## Ziel-Pipeline

```text
Hermes
  -> trend-engine
  -> content-engine/brain
  -> content-engine/renderer
  -> seo-engine
  -> qa-engine
  -> distribution
  -> manual review or publish decision
```

## Ziel-Kommandos

Die genauen CLI-Module werden schrittweise implementiert. Der Contract legt bereits die Ziel-Form fest.

```bash
python -m trend_engine.cli \
  --dry-run \
  --mode market_scan \
  --out runs/<job_id>/topic_brief.json \
  --sources-out runs/<job_id>/sources.json

python -m elementkonfluenz_brain.cli \
  --topic runs/<job_id>/topic_brief.json \
  --out runs/<job_id>/scene_plan.json

cd content-engine/renderer
npm run render -- --props=../../runs/<job_id>/scene_plan.json

python -m valueracer_seo.cli \
  --dry-run \
  --run-dir runs/<job_id>

python -m qa_engine.cli \
  --dry-run \
  --run-dir runs/<job_id> \
  --history runs/history.jsonl

python -m distribution.cli \
  --run-dir runs/<job_id> \
  --dry-run
```

Bis alle Ziel-CLIs existieren, duerfen Teilmodule eigene Zwischenbefehle verwenden. Neue Implementierungen muessen sich aber an diesem Contract orientieren.

## Run-Ordner

Jeder Produktionslauf erzeugt einen eigenen Ordner unter `runs/`. Diese Ordner sind Arbeitsartefakte und sollen auf dem VPS persistiert werden. Im Git-Repo liegt nur `runs/.gitkeep`, keine echten Runs.

Empfohlene Job-ID:

```text
YYYY-MM-DD_HHMMSS_<short-topic-slug>
```

Beispiel:

```text
runs/2026-06-21_093000_gold-vs-sp500/
├── topic_brief.json
├── sources.json
├── scene_plan.json
├── render.mp4
├── metadata/
│   ├── youtube.json
│   ├── tiktok.json
│   ├── instagram.json
│   └── x.json
├── qa.json
├── posting_plan.json
├── job_result.json
└── logs/
    ├── trend-engine.log
    ├── brain.log
    ├── renderer.log
    ├── seo-engine.log
    └── distribution.log
```

## Stage-Ergebnisse

Jede Stage soll ein Ergebnis im selben Grundformat liefern. Das finale `job_result.json` aggregiert alle Stage-Ergebnisse.

```json
{
  "ok": true,
  "stage": "brain",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "artifacts": ["scene_plan.json"],
  "warnings": [],
  "requires_review": true,
  "ready_to_publish": false
}
```

Bei Fehlern:

```json
{
  "ok": false,
  "stage": "renderer",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "error_code": "RENDER_FAILED",
  "message": "Renderer failed before producing render.mp4.",
  "retryable": false,
  "artifacts": [],
  "warnings": ["No publishable video was created."],
  "requires_review": true,
  "ready_to_publish": false
}
```

## Review-Gates

Die Pipeline darf `ready_to_publish: true` nur setzen, wenn alle folgenden Punkte erfuellt sind:

- `job_result.ok == true`
- `qa.hard_fail == false`
- Video-Datei existiert
- Plattform-Metadaten existieren
- Quellenmanifest existiert
- Keine red-flag Content-Policy-Verletzung
- Kein Auto-Posting-Sperrflag aktiv

Bis zur ausdruecklichen Freigabe bleibt `requires_review: true` Standard.

## Dry-Run Default

Alle Distribution-Kommandos muessen standardmaessig im Dry-Run laufen. Ein echtes Posting darf nur moeglich sein, wenn ein spaeterer Befehl explizit eine Publish-Option setzt, z. B.:

```bash
python -m distribution.cli --run-dir runs/<job_id> --publish --platform youtube
```

Diese Publish-Option wird erst implementiert, wenn Migration, Backups, API-Zugaenge und manuelle Review-Regeln stabil sind.

## Hermes-Verantwortung

Hermes darf:

- Jobs starten
- Run-Ordner anlegen
- Module in Reihenfolge ausfuehren
- `job_result.json` lesen
- `qa.json` lesen
- vorhandene VPS-Environment-Variablen verwenden
- den Nutzer bei `requires_review: true` informieren
- fehlgeschlagene, als `retryable: true` markierte Stages neu starten

Hermes darf nicht:

- alte Runs loeschen
- bestehende Produktionsdaten ueberschreiben
- API-Keys veraendern
- `.env`-Dateien ueberschreiben
- Auto-Posting aktivieren
- fehlerhafte Runs trotzdem veroeffentlichen
- Content-Regeln umgehen

## Environment-Variablen

Spaetere Deployments sollen sensible Daten nur ueber Environment-Variablen oder einen separaten Secret-Store laden. Keine Secrets im Repo.

Neue Variablen sollen den `VALUERACER_` Prefix verwenden:

```text
VALUERACER_ENV=production|staging|local
VALUERACER_RUNS_DIR=/srv/valueracer/runs
VALUERACER_LOGS_DIR=/srv/valueracer/logs
VALUERACER_DRY_RUN=true
YOUTUBE_CLIENT_ID=...
TIKTOK_CLIENT_ID=...
INSTAGRAM_CLIENT_ID=...
X_API_KEY=...
```

Legacy-Variablen mit altem Prefix duerfen in einer Uebergangsphase gelesen werden, wenn sie auf dem VPS bereits existieren:

```text
ELEMENTKONFLUENZ_ENV=production|staging|local
ELEMENTKONFLUENZ_RUNS_DIR=/srv/elementkonfluenz/runs
ELEMENTKONFLUENZ_DRY_RUN=true
```

Regel: lesen ja, automatisch veraendern nein.

## Versionierung

Dieser Contract startet mit Version 0.1. Sobald CLIs und JSON-Schemas stabil sind, wird daraus `contract_version: 1`.
