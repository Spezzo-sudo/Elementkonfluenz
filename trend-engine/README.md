# trend-engine

Entscheidet, welches Thema als nächstes produziert wird.

## Geplant

- Themen-Katalog: Liste verfügbarer Chart-Datensätze, getaggt mit Keywords/Kategorien.
- Trend-Signale:
  - Google Trends via `pytrends` (offizielle API ist Alpha/Invite-only, später Wechsel möglich).
  - GDELT (kostenlos, globale News-Themen + Sentiment, 15-Minuten-Updates).
  - RSS-Feeds großer Magazine/Finanzmedien.
- Scoring: Katalog-Themen gegen aktuelle Trend-Keywords matchen, höchster Score gewinnt.
- Cooldown/Dedup: SQLite-Tabelle mit "zuletzt verwendet am"-Datum pro Thema, Ausschluss innerhalb konfigurierbarem Zeitraum (Default 14–30 Tage).
- Fallback: Round-Robin durch ungenutzte Katalog-Themen, wenn kein Trend-Match ausreichend stark ist.

## Offen

- Erste Version des Themen-Katalogs (welche Datensätze/Quellen).
- Konkretes Scoring-Verfahren (Keyword-Overlap vs. Embedding-Similarity).
