# ValueRacer trend-engine

Entscheidet, welches Thema als naechstes produziert werden soll. Es gibt zwei sichere Dry-Run-Modi:

- `market_scan`: waehlt aus einem statischen Topic-Katalog mit Cooldown-Schutz.
- `trend_scan`: simuliert einen T-2h Research-Scan, scored Kandidaten und leitet daraus ein Thema ab.

Beide Modi sind aktuell Dry-Run only. Es werden noch keine Live-Marktdaten, Suchdaten, News-Feeds oder externen APIs abgefragt.

## market_scan

```bash
python -m trend_engine.cli \
  --dry-run \
  --mode market_scan \
  --out ../runs/test-market-scan/topic_brief.json \
  --sources-out ../runs/test-market-scan/sources.json \
  --history ../runs/history.jsonl \
  --write-history
```

## trend_scan

```bash
python -m trend_engine.cli \
  --dry-run \
  --mode trend_scan \
  --out ../runs/test-trend-scan/topic_brief.json \
  --sources-out ../runs/test-trend-scan/sources.json \
  --history ../runs/history.jsonl \
  --write-history
```

Schreibt:

```text
runs/<job_id>/trend_report.json
runs/<job_id>/scored_candidates.json
runs/<job_id>/topic_brief.json
runs/<job_id>/sources.json
```

## Scoring-Idee

`trend_scan` bewertet Kandidaten nach:

```text
attention
velocity
data_score
story_score
cooldown status
```

Harte Blocker:

```text
exaktes Topic im Cooldown
exaktes Asset-Paar im Cooldown
```

Der neue Video-Typ `imperiumkriege` ist als eigener Rotationstyp vorgesehen.

## Beispiel-Output

```json
{
  "ok": true,
  "stage": "trend-engine",
  "mode": "dry_run",
  "run_mode": "trend_scan",
  "requires_review": true,
  "ready_to_publish": false
}
```

## Kein geeignetes Thema

Wenn alle Kandidaten durch Cooldown blockiert sind:

```json
{
  "ok": false,
  "stage": "trend-engine",
  "error_code": "NO_ELIGIBLE_TREND_CANDIDATE",
  "retryable": true,
  "requires_review": true,
  "ready_to_publish": false
}
```

## Sicherheitsregeln

- `--dry-run` ist Pflicht.
- Keine API-Aufrufe.
- Keine Secrets.
- Keine echten Marktwerte.
- Keine Aktivierung ausserhalb der GitHub-Testlinie.
- Bestehendes `/root/valueracer` bleibt getrennt.
