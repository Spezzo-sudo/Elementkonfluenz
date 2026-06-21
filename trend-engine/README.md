# trend-engine

Entscheidet, welches Thema als nächstes produziert wird — und welche der beiden
Content-Verticals (`chart_race` oder `imperium`) als nächstes dran ist. Siehe
[`TOPIC_BRIEF.md`](TOPIC_BRIEF.md) für den Output-Contract.

## Status

- Python-Paket `value_racer_trend` (`value_racer_trend/`) ist gebaut und verifiziert:
  - `catalog_chart_race.py` — 13 Asset-Kombinationen, getaggt mit 6 Kategorien (`crypto_major`,
    `crypto_alt`, `single_stock`, `index_etf`, `commodity`, `mixed_basket`).
  - `catalog_imperium.py` — 8 Konzerne (Start-Katalog, von Grund auf neu aufgebaut), getaggt
    mit Sektor/Region.
  - `store.py` — SQLite-Cooldown/Dedup-Historie (Topic- und Kategorie-/Sektor-Ebene).
  - `scorer.py` — Cross-Vertical-Scorer: deficit-basierter Scheduler für die
    `content_type`-Wahl (konvergiert exakt auf die konfigurierte Gewichtung, anders als
    reines Zufalls-Sampling mit Cap) plus Kategorie-/Sektor-Rotation innerhalb der Vertical.
  - `cli.py` — `python -m value_racer_trend.cli` (Einzel-Pick als `TopicBrief`-JSON)
    und `--simulate N` (Verifikation von Quote/Anti-Repetition ohne Persistenz).
- Verifiziert per Simulation über 2000 Picks: Verhältnis exakt 4:1 (chart_race:imperium),
  `chart_race` max. 4× in Folge, `imperium` nie 2× in Folge, keine direkte Kategorie-/
  Sektor-Wiederholung.

## Geplant

- Trend-Signale (aktuell ist `trend_score` immer `0.0`, Scorer arbeitet rein über
  Cooldown/Rotation):
  - Google Trends via `pytrends` (offizielle API ist Alpha/Invite-only, später Wechsel möglich).
  - GDELT (kostenlos, globale News-Themen + Sentiment, 15-Minuten-Updates).
  - RSS-Feeds großer Magazine/Finanzmedien.
- Erweiterung der Kataloge (mehr Asset-Kombinationen, mehr Konzerne über weitere
  Sektoren/Regionen).

## Offen

- Konkretes Trend-Scoring-Verfahren (Keyword-Overlap vs. Embedding-Similarity), sobald
  echte Signale angebunden werden.
