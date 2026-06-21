# Hermes VPS Runner for ValueRacer

This runbook describes how Hermes can run the current safest ValueRacer loop on a VPS.

The runner remains dry-run only. It does not publish, render, call platform APIs, rotate secrets, overwrite `.env` files, or modify existing services.

## Separation first

Before using this runner outside the GitHub test checkout, read and follow:

```text
ops/SEPARATION_POLICY.md
```

Current rule:

```text
/root/valueracer          = existing VPS project, do not touch
/srv/valueracer_repo_test = GitHub test line, dry-run only
```

The templates in this folder are not activation approval. They must not be installed, enabled, or used against production paths until a separate migration plan is approved.

## Current safe command

The underlying command is:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode market_scan \
  --with-youtube-seo \
  --with-qa \
  --out runs/<job_id>
```

The repo wrapper is:

```bash
ops/hermes_valueracer_dry_run.sh
```

It writes one new run folder per execution and logs to `logs/<job_id>.log`.

## Required VPS layout

Recommended future target layout after explicit migration approval:

```text
/srv/valueracer/
├── orchestrator/
├── trend-engine/
├── seo-engine/
├── qa-engine/
├── ops/
├── runs/
└── logs/
```

Do not create or use this future production path while the approved test path is still `/srv/valueracer_repo_test`.

Do not overwrite the legacy `/root/valueracer` project. Keep it running until migration is explicitly approved.

## Install packages

Only for an approved checkout path. For the current test line, use `/srv/valueracer_repo_test`.

From the repo root:

```bash
cd /srv/valueracer_repo_test
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e orchestrator
python -m pip install -e trend-engine
python -m pip install -e seo-engine
python -m pip install -e qa-engine
```

## Manual dry-run test

Current approved test command:

```bash
cd /srv/valueracer_repo_test
. .venv/bin/activate
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode market_scan \
  --with-youtube-seo \
  --with-qa \
  --out runs/<job_id>
```

The wrapper script is for future approved runner testing, not for activation against production paths.

Expected artifacts:

```text
runs/<job_id>/topic_brief.json
runs/<job_id>/sources.json
runs/<job_id>/metadata/youtube.json
runs/<job_id>/publish/youtube_publish_plan.json
runs/<job_id>/qa.json
runs/<job_id>/job_result.json
runs/<job_id>/logs/orchestrator.log
logs/<job_id>.log
```

Expected safety values:

```text
job_result.requires_review = true
job_result.ready_to_publish = false
qa.requires_review = true
qa.ready_to_publish = false
publish.mode = dry_run
publish.privacy_status = private
```

## Environment files

The runner may read existing environment files if present:

```text
/root/.env
/root/.hermes/.env
/srv/valueracer/.env.local
```

Rules:

- do not print secrets
- do not commit secrets
- do not overwrite env files
- do not create new credentials automatically
- do not rotate existing credentials automatically

## systemd option

Templates are provided under:

```text
ops/systemd/valueracer-dry-run.service
ops/systemd/valueracer-dry-run.timer
```

Do not install or enable these templates while the GitHub line is still only approved for `/srv/valueracer_repo_test` dry-runs.

Future manual install example after explicit approval:

```bash
sudo cp /srv/valueracer/ops/systemd/valueracer-dry-run.service /etc/systemd/system/valueracer-dry-run.service
sudo cp /srv/valueracer/ops/systemd/valueracer-dry-run.timer /etc/systemd/system/valueracer-dry-run.timer
sudo systemctl daemon-reload
sudo systemctl enable --now valueracer-dry-run.timer
```

Check status:

```bash
systemctl status valueracer-dry-run.timer
systemctl list-timers | grep valueracer
journalctl -u valueracer-dry-run.service -n 100 --no-pager
```

## cron option

A cron template is provided under:

```text
ops/cron/valueracer-dry-run.cron
```

Do not install this template while the GitHub line is still only approved for `/srv/valueracer_repo_test` dry-runs.

Future manual install example after explicit approval:

```bash
crontab -l > /tmp/valueracer.cron.current 2>/dev/null || true
cat /srv/valueracer/ops/cron/valueracer-dry-run.cron >> /tmp/valueracer.cron.current
crontab /tmp/valueracer.cron.current
```

Use systemd timer or cron, not both.

## Safety checklist before activation

Before enabling a schedule, Hermes should report:

```text
Repo path:
Git commit:
Python venv:
Installed packages:
Runner path:
Runs dir:
Logs dir:
Legacy /root/valueracer untouched: yes/no
Services changed: yes/no
Secrets printed: yes/no
Posting disabled: yes/no
Rendering disabled: yes/no
```

## Handling NO_ELIGIBLE_TOPIC

When all catalog topics are inside cooldown, the orchestrator can return:

```text
ok = false
stage = trend-engine
error_code = NO_ELIGIBLE_TOPIC
retryable = true
```

This is not a production failure. It means the catalog is exhausted under the current cooldown rules. Hermes should notify rather than force a duplicate topic.

## Handling QA_HARD_FAIL

If QA fails, the orchestrator returns:

```text
ok = false
stage = qa
error_code = QA_HARD_FAIL
requires_review = true
ready_to_publish = false
```

Hermes must not publish, render, or continue distribution after this state.

## Current recommended cadence

Use three dry-runs per week while the catalog contains five topics and a seven-day cooldown is active.

Recommended schedule:

```text
Monday 06:00
Wednesday 06:00
Friday 06:00
```

Increase cadence only after the topic catalog, live data checks, and render validation are expanded.
