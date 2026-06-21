# ValueRacer trend-engine

Entscheidet, welches Thema als naechstes produziert werden soll. Die erste Implementierung ist bewusst ein sicherer `market_scan`-Dry-Run mit statischem Topic-Katalog und Cooldown-Schutz.

## Ziel der ersten Version

Die Trend Engine waehlt aus `data/topic_catalog.json` ein geeignetes Thema aus und schreibt:

```text
runs/<job_id>/topic_brief.json
runs/<job_id>/sources.json
```

Dabei werden bereits beruecksichtigt:

- Topic Cooldown
- Asset-Pair Cooldown
- Video-Typ-Rotation
- Template-Rotation
- History-Datei als JSONL

Es werden noch keine Live-Marktdaten, Google Trends, News-Feeds oder APIs abgefragt.

## Quickstart

```bash
cd trend-engine
python -m pip install -e .
python -m trend_engine.cli \
  --dry-run \
  --mode market_scan \
  --out ../runs/test-market-scan/topic_brief.json \
  --sources-out ../runs/test-market-scan/sources.json \
  --history ../runs/history.jsonl \
  --write-history
```

Oder ueber den Script-Entry:

```bash
valueracer-trend-engine \
  --dry-run \
  --mode market_scan \
  --out ../runs/test-market-scan/topic_brief.json \
  --sources-out ../runs/test-market-scan/sources.json \
  --history ../runs/history.jsonl \
  --write-history
```

## Beispiel-Output

```json
{
  "ok": true,
  "stage": "trend-engine",
  "mode": "dry_run",
  "run_mode": "market_scan",
  "selected_topic_slug": "gold-vs-sp500",
  "requires_review": true,
  "ready_to_publish": false
}
```

## Kein geeignetes Thema

Wenn alle Katalog-Themen durch Cooldown oder Rotation blockiert sind, gibt die CLI zurueck:

```json
{
  "ok": false,
  "stage": "trend-engine",
  "error_code": "NO_ELIGIBLE_TOPIC",
  "retryable": true,
  "requires_review": true,
  "ready_to_publish": false
}
```

## Geplant

- Live-Datenverfuegbarkeit pruefen.
- Google Trends / GDELT / RSS als Trend-Signale anbinden.
- Scoring gegen Nachfrage-Signale.
- Integration in den Orchestrator via `--run-mode market_scan`.

## Sicherheitsregeln

- `--dry-run` ist Pflicht.
- Keine API-Aufrufe.
- Keine Secrets.
- Keine echten Marktwerte.
- Keine Publish-Entscheidung.
