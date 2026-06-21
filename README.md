# ValueRacer

Automatisierte Pipeline, die täglich datengetriebene Short-Videos (Bar/Line-Race-Charts, Rankings, Maps) für YouTube Shorts, TikTok, Instagram Reels und X produziert und verteilt. Themenwahl orientiert sich an aktuellen gesellschaftlichen/finanziellen Trends statt an Zufall.

> Projektname: **ValueRacer**. Der alte Arbeitsname `Elementkonfluenz` kann in historischen Commits, offenen PRs oder internen Paketnamen noch vorkommen und wird schrittweise abgeloest.

## Module

- [`content-engine/`](content-engine) — Video-Rendering (Remotion), Diagramm-/Theme-Varianten, Audio-Mixing.
- [`trend-engine/`](trend-engine) — Themen-Katalog, Trend-Signale (Google Trends, GDELT, RSS), Scoring & Dedup/Cooldown.
- [`seo-engine/`](seo-engine) — Titel-, Hashtag- und Beschreibungs-Generierung pro Plattform.
- [`distribution/`](distribution) — Plattform-spezifische Exporte (wasserzeichenfrei) und Posting-Scheduler.

## Status

Phase 1 (content-engine Kern) steht: Brain (Python, portierte Entscheidungslogik) und Renderer
(Remotion) sind end-to-end verifiziert — ein live generierter `ScenePlan` rendert ruckelfrei mit
korrekter eigener Länge. trend-engine, seo-engine und distribution sind noch Konzeptphase, Details
in den jeweiligen README-Dateien der Module.

## Naming / Migration

Zielname fuer Repository, VPS-Verzeichnis und Produktkommunikation:

```text
ValueRacer
```

Empfohlener VPS-Zielpfad:

```text
/srv/valueracer
```

Das aktuelle GitHub-Repository kann noch `Elementkonfluenz` heissen, bis es in GitHub selbst umbenannt wurde. Die Code-Namespaces werden bewusst nicht in einem ungetesteten Big-Bang umbenannt, sondern schrittweise, damit CI und Hermes lauffaehig bleiben.

## Quickstart für lokale Entwicklung

### 1. Python-Brain prüfen

```bash
cd content-engine/brain
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m elementkonfluenz_brain.cli --help
```

Optional kann ein `ScenePlan` erzeugt werden:

```bash
python -m elementkonfluenz_brain.cli \
  --tickers BTC-USD,^GSPC,GC=F \
  --days 1825 \
  --out ../renderer/scene_plan.json \
  --locale de \
  --fps 30 \
  --investment 1000 \
  --mode evergreen
```

### 2. Remotion-Renderer prüfen

```bash
cd content-engine/renderer
npm ci
npm run typecheck
```

Rendern mit einem vorhandenen ScenePlan:

```bash
npm run render -- --props=scene_plan.json
```

### 3. CI-Checks

Pull Requests gegen `main` führen automatisch zwei Basischecks aus:

- Python-Brain Smoke-Test: Paket installieren, Import prüfen, CLI-Hilfe aufrufen.
- Renderer Typecheck: `npm ci` und `npm run typecheck`.

Diese Checks sind absichtlich klein gehalten. Sie sollen zuerst verhindern, dass grundlegende Import-, Installations- oder TypeScript-Fehler unbemerkt ins Projekt wandern.
