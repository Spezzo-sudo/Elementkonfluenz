# ValueRacer orchestrator

Minimaler Hermes-kompatibler Dry-Run-Orchestrator fuer ValueRacer.

Dieses Paket ist absichtlich klein. Es verbindet noch keine echten Produktionsmodule, sondern beweist zuerst den wichtigsten Contract:

- Hermes kann einen Job starten.
- Der Job schreibt einen eigenen Run-Ordner.
- Der Run-Ordner enthaelt maschinenlesbare Artefakte.
- Der Job bleibt im Dry-Run und postet nichts.

## Ziel

Der Orchestrator ist die spaetere Einstiegsschicht fuer Hermes auf dem VPS. Hermes soll nicht in interne Moduldetails greifen, sondern klare Kommandos ausfuehren und `job_result.json` lesen.

## Manual Topic Quickstart

```bash
cd orchestrator
python -m pip install -e .
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode manual_topic \
  --topic "Gold vs S&P 500" \
  --out ../runs/test-gold-sp500
```

Alternativ ueber den installierten Script-Entry:

```bash
valueracer-orchestrator \
  --dry-run \
  --run-mode manual_topic \
  --topic "Gold vs S&P 500" \
  --out ../runs/test-gold-sp500
```

Erwartete Ausgabe:

```text
../runs/test-gold-sp500/
├── topic_brief.json
├── sources.json
├── job_result.json
└── logs/
    └── orchestrator.log
```

## Market Scan Dry-Run

Wenn `trend-engine` installiert ist, kann Hermes ein Thema automatisch aus dem ValueRacer Topic-Katalog waehlen lassen:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode market_scan \
  --out ../runs/test-market-scan
```

Dabei nutzt der Orchestrator:

- Topic-Katalog aus `trend-engine`
- Topic Cooldown
- Asset-Pair Cooldown
- Video-Typ-Rotation
- Template-Rotation
- History-Datei, standardmaessig im uebergeordneten `runs/`-Ordner

## Market Scan + YouTube SEO

Wenn `trend-engine` und `seo-engine` installiert sind, kann Hermes in einem Schritt ein neues Thema waehlen und YouTube-Metadaten vorbereiten:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --run-mode market_scan \
  --with-youtube-seo \
  --out ../runs/test-market-scan
```

Dann entstehen:

```text
../runs/test-market-scan/
├── topic_brief.json
├── sources.json
├── metadata/
│   └── youtube.json
├── publish/
│   └── youtube_publish_plan.json
├── job_result.json
└── logs/
    └── orchestrator.log
```

## Mit YouTube SEO Dry-Run fuer Manual Topic

Wenn `seo-engine` installiert ist, kann Hermes auch fuer ein manuelles Thema YouTube-Metadaten und einen privaten Publish-Plan erzeugen:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --with-youtube-seo \
  --topic "Gold vs S&P 500" \
  --out ../runs/test-gold-sp500
```

Dann entstehen zusaetzlich:

```text
../runs/test-gold-sp500/
├── metadata/
│   └── youtube.json
└── publish/
    └── youtube_publish_plan.json
```

Sicherheitsregeln bleiben unveraendert:

- keine YouTube API Calls
- keine Google Ads API Calls
- keine Secrets
- `privacy_status = private`
- `requires_review = true`
- `ready_to_publish = false`

## Legacy-Hinweis

Die interne Implementierung kann fuer eine Uebergangsphase noch den alten Paketnamen `elementkonfluenz_orchestrator` enthalten. Neue Aufrufe sollen aber `valueracer_orchestrator` oder `valueracer-orchestrator` verwenden.

## Wichtig

Dieser Orchestrator ruft bewusst noch keine Live-Marktdaten, keinen Renderer und keine Distribution auf. Market Scan und YouTube SEO sind lokale Dry-Run-Artefaktgeneratoren und posten nichts.
