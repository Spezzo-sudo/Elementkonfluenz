# ValueRacer Rotation and Cooldown

Stand: 2026-06-21

Dieses Dokument definiert, wie ValueRacer Wiederholungen vermeidet und verschiedene Video-Typen erzeugt.

## Ziel

ValueRacer soll nicht dreimal pro Woche denselben Clip mit anderem Titel erzeugen. Jeder Lauf braucht eine begruendete Themenwahl, Abwechslung im Video-Typ und Schutz vor Wiederholung.

## Video-Typen

### 1. `market_race`

Datenbasierter Vergleich mehrerer Assets oder Indikatoren.

Beispiele:

- Gold vs S&P 500
- Nasdaq vs Dow
- Bitcoin vs Tech
- Oil vs Inflation

Geeignet fuer:

- Bar Race
- Line Race
- Ranking-Verlauf

Mindestdaten:

- mindestens zwei Assets
- gemeinsamer Zeitraum
- reproduzierbare Start-/Endwerte
- Quellenmanifest

### 2. `trend_explainer`

Kurzes Erklaervideo zu einem Trendthema.

Beispiele:

- Warum reden alle ueber Zinsen?
- Was zeigt der Dollar Index gerade?
- Warum Rohstoffe wieder im Fokus stehen

Geeignet fuer:

- Hook-Intro
- einfache Chart-Erklaerung
- Text-/Icon-Overlays

Mindestdaten:

- nachvollziehbare Trendquelle
- mindestens eine sachliche Datenquelle
- klare Abgrenzung: Suchinteresse ist kein wirtschaftlicher Beweis

### 3. `macro_snapshot`

Momentaufnahme mehrerer makrooekonomischer Signale.

Beispiele:

- Inflation, Zinsen, Dollar in 30 Sekunden
- Drei Maerkte, eine Geschichte?
- Was sich diese Woche bewegt hat

Geeignet fuer:

- Dashboard-Layout
- Ranking-Tabelle
- Multi-Chart Short

Mindestdaten:

- mehrere Indikatoren
- jeweiliger Zeitraum
- klares Caveat

## Cooldown-Regeln

### Topic Cooldown

Dasselbe Thema darf innerhalb eines definierten Fensters nicht erneut verwendet werden.

Empfohlen:

```text
default_topic_cooldown_days = 14
```

Beispiel blockiert:

```text
Gold vs S&P 500
Gold gegen S&P500
S&P 500 vs Gold
```

### Asset-Pair Cooldown

Dieselbe Asset-Kombination darf nicht zu oft wiederholt werden.

Empfohlen:

```text
asset_pair_cooldown_days = 21
```

### Template Cooldown

Derselbe Video-Typ oder dieselbe visuelle Vorlage soll nicht unbegrenzt hintereinander laufen.

Empfohlen:

```text
max_same_video_type_in_row = 2
max_same_template_in_row = 2
```

### Hook Cooldown

Gleiche Hook-Struktur nicht direkt wiederholen.

Beispiel zu aehnlich:

```text
"Gold vs Tech: Wer hat wirklich geliefert?"
"Bitcoin vs Aktien: Wer hat wirklich geliefert?"
```

## Run History Store

Spaeter soll ValueRacer eine kleine History-Datei oder SQLite-Datenbank pflegen.

Minimal als JSONL:

```text
runs/history.jsonl
```

Beispiel-Eintrag:

```json
{
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "created_at": "2026-06-21T09:30:00Z",
  "run_mode": "manual_topic",
  "video_type": "market_race",
  "template": "bar_race",
  "topic_slug": "gold-vs-sp500",
  "asset_keys": ["gold", "sp500"],
  "title": "Gold vs S&P 500",
  "qa_hard_fail": false
}
```

## Auswahl-Algorithmus fuer Market Scan

```text
1. Kandidaten aus Topic Catalog laden
2. Kandidaten mit fehlenden Daten entfernen
3. Kandidaten mit Cooldown-Verstoss entfernen
4. Kandidaten nach Aktualitaet/Relevanz sortieren
5. Video-Typ gegen letzte Runs rotieren
6. Plausibilitaetscheck ausfuehren
7. besten Kandidaten als topic_brief.json schreiben
```

## Auswahl-Algorithmus fuer Trend Scan

```text
1. Trend-Signale laden
2. ungeeignete/unsichere Themen entfernen
3. Nachfrage-Signal mit Topic Catalog matchen
4. Fakten-/Datenquelle pruefen
5. Cooldown pruefen
6. Video-Typ rotieren
7. Topic Brief schreiben
```

## Hermes-Regel

Hermes soll nicht selbst entscheiden, ob ein Thema zu aehnlich ist. Hermes startet `market_scan` oder `trend_scan`; ValueRacer entscheidet intern anhand History, Cooldown und QA.

Hermes liest danach:

```text
job_result.json
qa.json
```

Wenn kein geeignetes Thema gefunden wird, schreibt ValueRacer:

```json
{
  "ok": false,
  "stage": "trend-engine",
  "error_code": "NO_ELIGIBLE_TOPIC",
  "retryable": true,
  "requires_review": true,
  "ready_to_publish": false
}
```
