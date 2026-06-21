#!/usr/bin/env bash
set -euo pipefail

# Safe ValueRacer dry-run runner for Hermes/VPS.
# This script intentionally does not publish, render, print secrets, or modify services.

VALUERACER_ROOT="${VALUERACER_ROOT:-/srv/valueracer}"
VALUERACER_RUNS_DIR="${VALUERACER_RUNS_DIR:-$VALUERACER_ROOT/runs}"
VALUERACER_JOB_PREFIX="${VALUERACER_JOB_PREFIX:-hermes-full-loop}"
VALUERACER_DRY_RUN="${VALUERACER_DRY_RUN:-true}"
VALUERACER_LOGS_DIR="${VALUERACER_LOGS_DIR:-$VALUERACER_ROOT/logs}"

if [ "$VALUERACER_DRY_RUN" != "true" ]; then
  echo "error: VALUERACER_DRY_RUN must be true for this runner" >&2
  exit 2
fi

if [ ! -d "$VALUERACER_ROOT" ]; then
  echo "error: ValueRacer root not found: $VALUERACER_ROOT" >&2
  exit 1
fi

cd "$VALUERACER_ROOT"

# Load existing VPS environment files if present. Never print their contents.
if [ -f /root/.env ]; then
  set -a
  # shellcheck disable=SC1091
  source /root/.env
  set +a
fi

if [ -f /root/.hermes/.env ]; then
  set -a
  # shellcheck disable=SC1091
  source /root/.hermes/.env
  set +a
fi

if [ -f "$VALUERACER_ROOT/.env.local" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$VALUERACER_ROOT/.env.local"
  set +a
fi

mkdir -p "$VALUERACER_RUNS_DIR" "$VALUERACER_LOGS_DIR"

JOB_ID="${VALUERACER_JOB_ID:-$(date -u +%Y-%m-%d_%H%M%S)_${VALUERACER_JOB_PREFIX}}"
RUN_DIR="$VALUERACER_RUNS_DIR/$JOB_ID"
LOG_FILE="$VALUERACER_LOGS_DIR/${JOB_ID}.log"

{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) starting ValueRacer dry-run"
  echo "job_id=$JOB_ID"
  echo "run_dir=$RUN_DIR"
  echo "root=$VALUERACER_ROOT"

  python -m valueracer_orchestrator.cli \
    --dry-run \
    --run-mode market_scan \
    --with-youtube-seo \
    --with-qa \
    --out "$RUN_DIR"

  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) finished ValueRacer dry-run"
  echo "job_result=$RUN_DIR/job_result.json"
  echo "qa_result=$RUN_DIR/qa.json"
} >> "$LOG_FILE" 2>&1

cat "$RUN_DIR/job_result.json"

if [ -f "$RUN_DIR/qa.json" ]; then
  cat "$RUN_DIR/qa.json"
fi
