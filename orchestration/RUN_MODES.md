# ValueRacer Run Modes

Stand: 2026-06-21

Dieses Dokument definiert die Betriebsarten, mit denen Hermes ValueRacer starten darf. Ziel ist, dass Hermes nicht raten muss, sondern pro Lauf einen klaren Modus, klare Inputs, klare Outputs und klare Stop-Regeln kennt.

## Grundsatz

Hermes ist Scheduler und Operator. ValueRacer ist Pipeline-Worker.

```text
Hermes -> run_request.json or CLI args -> ValueRacer -> run folder -> job_result.json
```

Hermes darf ValueRacer starten und danach Artefakte lesen. Hermes soll keine internen Python-/TypeScript-Funktionen direkt aufrufen.

## Gemeinsame Sicherheitsregeln

Alle Run Modes gelten zuerst als Dry-Run.

Immer aktiv:

- kein Auto-Posting
- kein Loeschen alter Runs
- kein Ueberschreiben bestehender Runs
- keine Secret-Ausgabe
- `requires_review = true`
- `ready_to_publish = false`, bis QA, Review und Freigabe ausdruecklich abgeschlossen sind

## Mode A: `manual_topic`

Hermes oder der Nutzer gibt ein konkretes Thema vor.

Beispiel:

```bash
python -m valueracer_orchestrator.cli \
  --dry-run \
  --with-youtube-seo \
  --topic "Gold vs S&P 500" \
  --out runs/2026-06-21_093000_gold-vs-sp500
```

Ziel:

- schnelles Testen
- bewusstes Thema
- keine automatische Trend-Entscheidung

Mindest-Outputs:

```text
topic_brief.json
sources.json
metadata/youtube.json
publish/youtube_publish_plan.json
job_result.json
logs/orchestrator.log
```

Nicht erlaubt:

- Thema ungeprueft als faktische Aussage behandeln
- ohne Review publishen
- fehlende Quellen ignorieren

## Mode B: `market_scan`

ValueRacer waehlt ein Thema aus einem Markt-/Asset-Katalog.

Beispiele:

- Gold vs S&P 500
- Nasdaq vs Dow
- Bitcoin vs Tech
- Dollar Index vs Gold
- Oil vs Inflation

Ziel:

- wiederkehrender datenbasierter Marktvergleich
- verschiedene Assets
- keine Wiederholung derselben Story

Mindest-Entscheidungen:

```text
candidate_topics -> cooldown filter -> data availability check -> plausibility check -> topic_brief.json
```

Muss noch implementiert werden.

## Mode C: `trend_scan`

ValueRacer waehlt ein Thema aus externen Trend-/Nachfrage-Signalen.

Moegliche Quellen spaeter:

- Google Trends
- RSS / News Feeds
- GDELT
- YouTube / Google Ads Keyword Planner als Research-Signal
- manuell gepflegter Trend-Katalog

Ziel:

- Themen finden, die gerade Nachfrage haben
- aber nur verwenden, wenn sie zum Content-Standard passen

Nicht erlaubt:

- Suchvolumen als wirtschaftlichen Beweis darstellen
- News-Hype ohne Datenbasis uebernehmen
- politisch oder finanziell sensible Aussagen ohne Review pushen

Muss noch implementiert werden.

## Mode D: `rerun_failed`

Hermes darf einen fehlgeschlagenen Run erneut versuchen, wenn `job_result.retryable == true`.

Regeln:

- neuer Run-Ordner oder expliziter Retry-Ordner
- alter Run bleibt unveraendert
- Retry-Grund wird in Logs dokumentiert
- kein Retry, wenn Fehler Content-/QA-basiert ist

## Run Request

Ein spaeterer Hermes-Run kann ueber CLI-Argumente oder `run_request.json` gestartet werden.

Beispiel:

```json
{
  "contract_version": "0.1",
  "run_mode": "market_scan",
  "dry_run": true,
  "job_id": "2026-06-21_093000_market-scan",
  "platforms": ["youtube"],
  "video_types_allowed": ["market_race", "trend_explainer"],
  "cooldown_days": 14,
  "requires_review": true
}
```

## Entscheidungsbaum fuer Hermes

```text
schedule fires
  -> create job_id
  -> choose run_mode
  -> call ValueRacer CLI
  -> wait for process exit
  -> read job_result.json
  -> if ok=false: notify with error_code
  -> if requires_review=true: notify for review
  -> if ready_to_publish=false: do not publish
```

## Aktueller Implementierungsstand

Bereits vorhanden:

- `manual_topic` als Dry-Run
- optional YouTube SEO Dry-Run via `--with-youtube-seo`
- Run-Ordner
- `job_result.json`

Noch offen:

- `market_scan`
- `trend_scan`
- Cooldown-Store
- Template-/Video-Typ-Rotation
- echte Daten-Plausibilitaet
- `qa.json`
