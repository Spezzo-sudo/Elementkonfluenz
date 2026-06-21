# ValueRacer orchestrator

Minimaler Hermes-kompatibler Dry-Run-Orchestrator fuer ValueRacer.

Dieses Paket ist absichtlich klein. Es verbindet noch keine echten Produktionsmodule, sondern beweist zuerst den wichtigsten Contract:

- Hermes kann einen Job starten.
- Der Job schreibt einen eigenen Run-Ordner.
- Der Run-Ordner enthaelt maschinenlesbare Artefakte.
- Der Job bleibt im Dry-Run und postet nichts.

## Ziel

Der Orchestrator ist die spaetere Einstiegsschicht fuer Hermes auf dem VPS. Hermes soll nicht in interne Moduldetails greifen, sondern klare Kommandos ausfuehren und `job_result.json` lesen.

## Quickstart

```bash
cd orchestrator
python -m pip install -e .
python -m valueracer_orchestrator.cli \
  --dry-run \
  --topic "Gold vs S&P 500" \
  --out ../runs/test-gold-sp500
```

Alternativ ueber den installierten Script-Entry:

```bash
valueracer-orchestrator \
  --dry-run \
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

## Legacy-Hinweis

Die interne Implementierung kann fuer eine Uebergangsphase noch den alten Paketnamen `elementkonfluenz_orchestrator` enthalten. Neue Aufrufe sollen aber `valueracer_orchestrator` oder `valueracer-orchestrator` verwenden.

## Wichtig

Dieser erste Orchestrator ruft bewusst noch keine Trend Engine, keine yfinance-Daten, keinen Renderer und keine Distribution auf. Er ist ein sicherer Contract-Smoke-Test fuer Hermes.
