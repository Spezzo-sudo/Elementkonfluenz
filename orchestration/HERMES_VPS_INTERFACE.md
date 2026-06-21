# Hermes VPS Interface

Stand: 2026-06-21

Dieses Dokument beschreibt, wie ein vorhandenes Hermes-/ValueRacer-System auf dem VPS mit diesem Repository verbunden werden soll, ohne bestehende Daten, Secrets oder Services zu gefaehrden.

## Ausgangspunkt

Auf dem VPS kann bereits ein Projekt namens `ValueRacer` existieren. Dieses Repository darf deshalb nicht blind darueber kopiert werden.

Regel:

```text
inventarisieren -> backup -> parallel testen -> dry-run -> vergleichen -> schrittweise verbinden
```

## Rollen

### Hermes

Hermes ist Operator und Scheduler.

Hermes darf:

- Zeitplaene ausloesen
- Run Mode waehlen
- Topic uebergeben oder Scan starten
- ValueRacer CLI ausfuehren
- Artefakte lesen
- Nutzer benachrichtigen

Hermes darf nicht:

- interne Module direkt patchen
- Secrets ausgeben
- `.env` ueberschreiben
- alte Runs loeschen
- Auto-Posting aktivieren

### ValueRacer

ValueRacer ist Pipeline-Worker.

ValueRacer darf:

- Run-Ordner erzeugen
- JSON-Artefakte schreiben
- QA pruefen
- Metadaten vorbereiten
- spaeter rendern

ValueRacer darf nicht:

- ohne Freigabe posten
- Secrets ins Repo schreiben
- alte Daten ungefragt veraendern

## Empfohlene VPS-Struktur

```text
/srv/hermes/                 # bestehender Hermes Bot
/srv/hermes/.env             # bestehende Secrets, nicht ins Repo kopieren
/srv/valueracer/             # dieses Repo oder neues Arbeitsverzeichnis
/srv/valueracer/.env.local   # lokale nicht-committete ValueRacer-Konfig
/srv/valueracer/runs/        # persistente Run-Artefakte
/srv/valueracer/logs/        # optionale globale Logs
```

Wenn bereits `/srv/ValueRacer` oder ein anderer Pfad existiert, zuerst inventarisieren und nicht blind ersetzen.

## Environment-Regel

ValueRacer liest vorhandene ENV, erzeugt sie aber nicht neu.

Beispiel:

```bash
set -a
source /srv/hermes/.env
source /srv/valueracer/.env.local 2>/dev/null || true
set +a
```

Keine Ausgabe von Secret-Werten. Preflight darf nur melden:

```text
YOUTUBE_CLIENT_ID=set
YOUTUBE_CLIENT_SECRET=set
YOUTUBE_REFRESH_TOKEN=missing
```

## Aktueller Dry-Run-Befehl

```bash
cd /srv/valueracer
python -m valueracer_orchestrator.cli \
  --dry-run \
  --with-youtube-seo \
  --topic "Gold vs S&P 500" \
  --out runs/manual-test-gold-sp500
```

## Geplanter Hermes Wrapper

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /srv/valueracer

set -a
source /srv/hermes/.env
source /srv/valueracer/.env.local 2>/dev/null || true
set +a

TOPIC="${VALUERACER_TOPIC:-Gold vs S&P 500}"
JOB_ID="${VALUERACER_JOB_ID:-$(date -u +%Y-%m-%d_%H%M%S)_manual-topic}"
RUNS_DIR="${VALUERACER_RUNS_DIR:-/srv/valueracer/runs}"

python -m valueracer_orchestrator.cli \
  --dry-run \
  --with-youtube-seo \
  --topic "$TOPIC" \
  --job-id "$JOB_ID" \
  --out "$RUNS_DIR/$JOB_ID"
```

## Beispiel: 3x pro Woche

Cron-Beispiel:

```cron
0 9 * * 1,3,5 /srv/valueracer/bin/hermes_dry_run.sh
```

Besser spaeter: systemd timer, weil Logs und Fehler sauberer kontrollierbar sind.

## Was Hermes nach jedem Run pruefen soll

1. Existiert `job_result.json`?
2. Ist `ok == true`?
3. Ist `requires_review == true`?
4. Ist `ready_to_publish == false`?
5. Gibt es `warnings`?
6. Existiert `metadata/youtube.json`?
7. Existiert `publish/youtube_publish_plan.json`?
8. Falls spaeter vorhanden: existiert `qa.json` und ist `hard_fail == false`?

## Ergebnis-Kategorien

### Erfolgreicher Dry-Run

```json
{
  "ok": true,
  "requires_review": true,
  "ready_to_publish": false
}
```

Hermes meldet:

```text
Run vorbereitet. Review erforderlich. Kein Posting ausgefuehrt.
```

### Technischer Fehler

```json
{
  "ok": false,
  "retryable": true,
  "error_code": "..."
}
```

Hermes darf Retry planen.

### Content-/QA-Fehler

```json
{
  "ok": false,
  "retryable": false,
  "requires_review": true,
  "error_code": "QA_..."
}
```

Hermes darf keinen Retry-Spam starten, sondern Review melden.

## Noch offen fuer echte Automation

- Preflight CLI
- Market Scan
- Trend Scan
- QA Engine
- Renderer-Verkabelung
- Run History / Cooldown Store
- systemd/cron Runbook
