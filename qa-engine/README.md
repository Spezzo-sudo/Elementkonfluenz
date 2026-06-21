# ValueRacer QA Engine

Basic dry-run QA gates for ValueRacer run folders.

The first version checks already-generated artifacts. It does not fetch market data, call platform APIs, render video, publish content, or read secrets.

## Quickstart

```bash
cd qa-engine
python -m pip install -e .
```

Run QA against a full dry-run folder:

```bash
python -m qa_engine.cli \
  --dry-run \
  --run-dir ../runs/test-market-scan \
  --history ../runs/history.jsonl
```

Or via script entrypoint:

```bash
valueracer-qa \
  --dry-run \
  --run-dir ../runs/test-market-scan \
  --history ../runs/history.jsonl
```

This writes:

```text
../runs/test-market-scan/qa.json
```

## Checks

Current checks:

- required artifacts exist
- JSON artifacts are parseable
- topic brief has required fields
- sources manifest is present and traceable
- job result is ok and review-gated
- advisory keywords are not present
- YouTube metadata is review-gated
- publish plan is private, dry-run, and review-gated
- optional repetition check against history JSONL

## Safety defaults

The QA result always keeps:

```json
{
  "requires_review": true,
  "ready_to_publish": false
}
```

A hard fail means the run must not be published.

## Example output

```json
{
  "contract_version": "0.1",
  "job_id": "hermes-market-scan-001",
  "ok": true,
  "hard_fail": false,
  "requires_review": true,
  "ready_to_publish": false,
  "checks": []
}
```

## Non-YouTube runs

For run folders that intentionally do not contain YouTube metadata, use:

```bash
python -m qa_engine.cli \
  --dry-run \
  --run-dir ../runs/manual-topic-only \
  --no-require-youtube
```

## Not yet included

- real market-data plausibility checks
- rendered video inspection
- thumbnail visual QA
- transcript/script QA
- source freshness via live API calls
- publish approval workflow
