# ValueRacer Separation Policy

This policy prevents accidental merging of the existing VPS ValueRacer project with the new GitHub test line.

## Current project lines

### Existing VPS project

```text
/root/valueracer
```

Status:

- existing project
- production-near
- currently running via existing services and cron
- must remain untouched unless explicitly approved

Known existing runtime pieces:

```text
value-racer-bot.service
existing daily workflow cron
existing Hermes environment files under /root
```

### New GitHub test line

```text
/srv/valueracer_repo_test
```

Status:

- GitHub checkout
- test-only line
- dry-run only
- not production
- must not be merged into `/root/valueracer`

## Hard rules

Do not merge, copy, replace, or synchronize files between these project lines.

Do not treat `/srv/valueracer_repo_test` as a replacement for `/root/valueracer`.

Do not activate systemd timers, cron jobs, publishing, rendering, or service changes from the GitHub test line without explicit approval.

Do not create or modify `/srv/valueracer` as a production path until a separate migration plan has been approved.

Do not read, print, copy, rotate, or overwrite secrets while testing the GitHub line.

## Allowed actions for the GitHub test line

Allowed:

```text
cd /srv/valueracer_repo_test
git fetch --all --prune
git checkout main
git pull --ff-only
python -m valueracer_orchestrator.cli --dry-run --run-mode market_scan --with-youtube-seo --with-qa --out runs/<job_id>
```

Allowed outputs:

```text
runs/<job_id>/topic_brief.json
runs/<job_id>/sources.json
runs/<job_id>/metadata/youtube.json
runs/<job_id>/publish/youtube_publish_plan.json
runs/<job_id>/qa.json
runs/<job_id>/job_result.json
runs/<job_id>/logs/orchestrator.log
```

Allowed reporting:

- commit hash
- run id
- selected topic
- dry-run status
- QA status
- whether `ready_to_publish` is false
- whether `requires_review` is true

## Forbidden actions without explicit approval

Forbidden:

```text
cp -r /srv/valueracer_repo_test/* /root/valueracer/
cp -r /root/valueracer/* /srv/valueracer_repo_test/
rsync between both trees
git remote add for /root/valueracer pointing to the GitHub repo
changing value-racer-bot.service
changing existing cron jobs
installing or enabling ops/systemd templates
installing ops/cron templates
running any publish-capable command
running any renderer against production outputs
printing /root/.env or /root/.hermes/.env
```

## Separation safety report

Before any activation, Hermes must report:

```text
/root/valueracer vorhanden: yes/no
/root/valueracer git status clean: yes/no
/root/valueracer modified by this test: yes/no
value-racer-bot.service changed: yes/no
existing cron changed: yes/no
/root/.env or /root/.hermes/.env printed: yes/no
/srv/valueracer_repo_test dry-run ok: yes/no
systemd timer activated: yes/no
cron installed: yes/no
/srv/valueracer production path created or modified: yes/no
merge between project lines performed: yes/no
```

Expected safe answer:

```text
/root/valueracer modified by this test: no
value-racer-bot.service changed: no
existing cron changed: no
/root/.env or /root/.hermes/.env printed: no
systemd timer activated: no
cron installed: no
/srv/valueracer production path created or modified: no
merge between project lines performed: no
```

## Future migration gate

A future migration from the existing VPS project to the GitHub line requires a separate approved plan.

That plan must include:

- backup of `/root/valueracer`
- backup of existing cron and service units
- inventory of existing Python files and runtime dependencies
- comparison between legacy renderer and new pipeline
- staging path separate from `/root/valueracer`
- rollback plan
- explicit approval before switching Hermes, cron, systemd, publishing, or rendering

Until then, the only approved GitHub-line path is:

```text
/srv/valueracer_repo_test
```

## Current decision

The GitHub line may continue to be tested independently.

The existing VPS ValueRacer project remains the source of truth for the running legacy bot until a separate migration is approved.
