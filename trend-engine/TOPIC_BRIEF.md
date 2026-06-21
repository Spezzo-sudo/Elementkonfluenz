# TopicBrief — trend-engine → content-engine Contract

`TopicBrief` ist die einzige Schnittstelle zwischen trend-engine (Themenwahl/Scoring)
und content-engine (Brain). Es trägt das Diskriminator-Feld `content_type`, das
festlegt, welcher der beiden Content-Engine-Äste (`chart_race` oder `imperium`)
das Thema verarbeitet. Genau eines von `chart_race`/`imperium` ist gesetzt, je
nach `content_type`.

`schema_version: 1`

```jsonc
// content_type == "chart_race"
{
  "schema_version": 1,
  "content_type": "chart_race",
  "selected_at": "2026-06-20T08:00:00+00:00",
  "trend_score": 0.0,
  "reason": "category-rotation pick, category=crypto_alt",
  "chart_race": {
    "topic_id": "crypto_alt_sol_ada_doge",
    "tickers": ["SOL-USD", "ADA-USD", "DOGE-USD"],
    "category": "crypto_alt",
    "period_days": 365,
    "keywords": ["altcoins", "solana", "cardano", "dogecoin"]
  },
  "imperium": null
}

// content_type == "imperium"
{
  "schema_version": 1,
  "content_type": "imperium",
  "selected_at": "2026-06-20T08:00:00+00:00",
  "trend_score": 0.0,
  "reason": "sector-rotation pick, sector=automotive",
  "chart_race": null,
  "imperium": {
    "topic_id": "imperium_toyota",
    "company_name": "Toyota Motor Corporation",
    "ticker": "7203.T",
    "sector": "automotive",
    "region": "APAC",
    "keywords": ["toyota", "autokonzern", "japan"]
  }
}
```

## Felder

- `content_type`: `"chart_race" | "imperium"` — entscheidet, welcher Brain-Ast das Thema verarbeitet.
- `trend_score`: aktuell immer `0.0` — Google-Trends/GDELT/RSS-Signale sind noch nicht
  angebunden (siehe `trend-engine/README.md`, "Geplant"). Der Scorer arbeitet bis dahin
  rein über Cooldown/Kategorie-Rotation. Sobald echte Trend-Signale existieren, ersetzt
  ihr Score die Kategorie-Alters-Heuristik in `scorer.py`, ohne den Contract zu ändern.
- `reason`: kurzer Klartext, warum dieses Thema gewählt wurde (für Debugging/Review-Queue).
- `chart_race.category`: eine von `crypto_major`, `crypto_alt`, `single_stock`,
  `index_etf`, `commodity`, `mixed_basket` — Grundlage für Kategorie-Cooldown.
- `imperium.sector`: eine von `consumer_goods`, `automotive`, `tech`, `finance`,
  `pharma`, `luxury`, `retail`, `energy`, `media` — Grundlage für Sektor-Cooldown.

## Anti-Repetition-Garantie

Der Scorer (`elementkonfluenz_trend.scorer`) garantiert:
1. `content_type`-Verhältnis konvergiert auf die konfigurierte Gewichtung (Default 4:1
   chart_race:imperium) über einen deficit-basierten Scheduler — reines Zufalls-Sampling
   mit einem Wiederholungs-Cap verzerrt diese Quote nachweislich nach oben (empirisch
   verifiziert, siehe Kommentar in `scorer.py`).
2. Cap auf aufeinanderfolgende `content_type`-Picks ist **asymmetrisch**: max. 4× `chart_race`
   in Folge, aber nie 2× `imperium` in Folge (`MAX_CONSECUTIVE` in `scorer.py`). Ein
   symmetrischer Cap für beide Typen würde das Verhältnis rechnerisch auf max. 2:1 begrenzen
   und wäre mit 4:1-Gewichtung unvereinbar.
3. Kein `topic_id` innerhalb von `TOPIC_COOLDOWN_DAYS` (Default 21) erneut.
4. Innerhalb eines `content_type` wird die Kategorie/Sektor bevorzugt, die am längsten
   nicht gewählt wurde (Tie-Breaker bei gleichem Cooldown-Status).

Verifizierbar über `python -m elementkonfluenz_trend.cli --simulate 200`.
