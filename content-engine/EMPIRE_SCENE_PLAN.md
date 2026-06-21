# EmpireScenePlan — Brain (imperium) → Renderer Contract

`EmpireScenePlan` ist das Pendant zu `ScenePlan` (siehe [`SCENE_PLAN.md`](SCENE_PLAN.md)) für die
zweite Content-Vertical **„Imperium"**. Gleiches Prinzip: der Renderer liest ausschließlich diese
JSON-Struktur, importiert nie Brain-Code und enthält keine Geschäftslogik. Die Datenform ist
bewusst nicht die von `ScenePlan` — keine Zeitreihen-Kamera, sondern eine feste Phasen-Abfolge aus
Karten/Stempel/Balkenvergleich.

`schema_version: 1`

```jsonc
{
  "schema_version": 1,
  "video_id": "string",
  "topic": {
    "topic_id": "imperium_nestle",
    "company_name": "Nestlé",
    "ticker": "NESN.SW",
    "sector": "consumer_goods",
    "region": "EU"
  },
  "fps": 30,
  "duration": {
    "total_frames": 630,
    "total_duration_sec": 21.0,
    "phases": {
      "hook": { "start_frame": 0, "end_frame": 60 },
      "register_cards": { "start_frame": 60, "end_frame": 180 },
      "beat": { "start_frame": 180, "end_frame": 225 },
      "stamp": { "start_frame": 225, "end_frame": 270 },
      "facts": { "start_frame": 270, "end_frame": 420 },
      "scale": { "start_frame": 420, "end_frame": 540 },
      "endcard": { "start_frame": 540, "end_frame": 630 }
    }
  },
  "owner": {
    "display_name": "Nestlé",
    "legal_name": "Nestlé S.A.",
    "hq_city": "Vevey, Schweiz",
    "founded_year": 1866
  },
  "hook_lines": ["WEM GEHÖRT", "DAS ALLES?"],
  "beat_line": "ALLE SPUREN FÜHREN ZU EINEM NAMEN",
  "brands": [
    { "name": "KitKat", "category": "Schokolade", "year": 1988, "color": "#D52B1E", "text_color": "#FFFFFF" }
  ],
  "facts": [
    { "label": "UMSATZ", "display_value": "91,4", "unit": "Mrd. CHF", "year": 2024, "description": "string" }
  ],
  "scale_comparison": {
    "headline": "Mehr wert als Unilever und Danone zusammen",
    "unit": "Mrd. USD",
    "rows": [{ "label": "Nestlé", "value": 251.1, "hero": true }]
  },
  "endcard": {
    "ticker_label": "AKTIE · NESN.SW · 10 JAHRE",
    "stock_from": 1000.0,
    "stock_to": 1528.0,
    "gain_pct": 52.8,
    "disclaimer": "Keine Anlageberatung · Vergangenheit ungleich Zukunft"
  },
  "theme": { "id": "imperium_dark", "accent_color": "#C0392B", "stamp_color": "#8B0000" },
  "qa": {
    "hard_fail": false,
    "sources_verified": true,
    "results": [{ "check": "string", "passed": true, "detail": "string" }]
  }
}
```

## Herkunft der Daten

- `brands`, `facts`, `scale_comparison`: ausschließlich aus der kuratierten, quellenbelegten
  `CompanyResearch`-YAML (`content-engine/brain/value_racer_brain/imperium/research.py`,
  Episoden unter `imperium/data/*.yaml`) — es gibt keine API für "welche Marken gehören zu
  Konzern X", deshalb ist dies der einzige Pipeline-Schritt, der von einem Menschen (oder einer
  KI mit echter Web-Recherche) geschrieben und belegt wird, nicht berechnet.
- `endcard`: einziger Live-Datenpunkt der Vertical — Aktienkurs-Performance per yfinance, exakt
  wie im chart_race-Ast, weil das die eine verlässlich per API beantwortbare Tatsache über ein
  reales Unternehmen ist.

## Invarianten

- Frames sind die einzige Zeiteinheit, die der Renderer kennt (wie bei `ScenePlan`).
- `qa.sources_verified == false` bedeutet: `distribution` darf das Ergebnis nicht automatisch
  posten, unabhängig vom sonstigen QA-Ergebnis — siehe Projekt-Plan, Abschnitt „Strengeres Gate
  (imperium)". `qa.hard_fail` bezieht sich nur auf strukturelle Checks (Mindestanzahl Marken/
  Fakten, jede Zahl mit Quelle) und ist davon unabhängig.
- `brands` ist auf 6–12 Einträge begrenzt (`qa.py: MIN_BRANDS/MAX_BRANDS`), sortiert nach
  `surprise_factor` (überraschendste zuerst sichtbar in der Kartenwand).
- `scale_comparison.rows[0]` ist immer der Owner-Konzern (`hero: true`); mindestens 2 weitere
  Vergleichsfirmen sind Pflicht.

## Automatisierungs-Modell dieser Vertical

Im Gegensatz zum chart_race-Ast (komplett API-getrieben) lässt sich Imperium nicht vollständig
automatisieren — die Recherche selbst bleibt ein manueller/KI-unterstützter Schritt. Was
automatisiert ist:

1. **Recherche entkoppelt von der Tagesproduktion**: eine `CompanyResearch`-YAML wird einmal
   geschrieben, dann beliebig oft vom Cross-Vertical-Scorer gezogen (wie jeder andere
   Katalog-Eintrag) — Recherche-Tempo und Posting-Kadenz sind unabhängig voneinander.
2. **Strukturelle QA ist hart automatisiert**: `qa.py` prüft Pflichtfelder, Mindestanzahlen und
   dass *jede* Zahl ein `source_url` trägt, sofort beim Befüllen — nicht erst beim Rendern.
3. **Staleness wird automatisch verfolgt, nicht von Hand**: `verified_at` +
   `verify_interval_days` pro Episode; `python -m value_racer_brain.imperium.cli research-status`
   listet alle Episoden mit Verifikations-Status (`verified` / `STALE` / `UNVERIFIED`), ohne dass
   jemand Daten im Kopf behalten muss.
4. **Katalog als Puffer, nicht Just-in-Time**: da der Scorer `imperium` nur zu 1/5 und nie 2×
   in Folge zieht, reicht es, Recherche in Batches voraus zu erledigen (z.B. 5 Konzerne an einem
   Stück) und einen stehenden Puffer verifizierter Episoden zu halten — die Tagespipeline blockiert
   dadurch nie auf laufender Recherche.
5. **Bewusste Grenze der Autonomie**: Erstkontakt-Episoden und alles mit `sources_verified=false`
   gehen laut Plan immer in die manuelle Review-Queue. Das ist kein Automatisierungs-Defizit,
   sondern eine Entscheidung — ein falscher Fakt über ein echtes Unternehmen kostet mehr als ein
   verpasster Post.
