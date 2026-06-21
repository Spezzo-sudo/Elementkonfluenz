# distribution

Exportiert und veröffentlicht die fertigen Videos. Python-Paket `value_racer_distribution`.
Liest ausschließlich JSON-Contracts (`EmpireScenePlan` etc.) als plain dict — importiert nie
interne Klassen von content-engine/trend-engine, gleiche Modul-Grenze wie überall sonst im
Projekt.

## Status

- **Imperium-Freigabe-Gate** (`value_racer_distribution/gate.py`) — implementiert das
  „Strengeres Gate (imperium)" aus dem Projekt-Plan. Drei voneinander unabhängige Gründe zwingen
  `pending_review`, jeder einzelne reicht:
  1. `qa.hard_fail` — strukturelle QA fehlgeschlagen.
  2. `qa.sources_verified == false` — deckt sowohl nie verifizierte als auch wieder verfallene
     (`is_stale`) Episoden ab, da `qa.py` Staleness bereits in `sources_verified` faltet.
  3. **Erstkontakt** — noch nie ein Post für diesen `topic.topic_id` verzeichnet
     (`value_racer_distribution/history.py`, SQLite). Auch eine komplett grüne Episode über einen
     erstmals behandelten Konzern geht beim ersten Mal immer in die manuelle Review.
  - Nur wenn keiner der drei Gründe zutrifft: `status=auto_post`.
  - Verifiziert per `python -m value_racer_distribution.cli gate --plan <empire_scene_plan.json>`
    gegen die echte Nestlé-Episode: leere History → `pending_review`
    (`first_contact_requires_manual_review`); nach `record-post` → `auto_post`; künstlich
    `sources_verified=false` bzw. `qa.hard_fail=true` gesetzt → jeweils `pending_review`, auch mit
    bereits vorhandenem Post in der History.
  - `record-post` steht für die echte Posting-Integration ein (noch nicht gebaut, siehe unten) —
    erlaubt es aber, das Gate inkl. Erstkontakt-Logik schon jetzt end-to-end zu prüfen.
- **chart_race-Hybrid-Gate** und die eigentliche Plattform-Anbindung/Posting-Scheduler sind noch
  nicht gebaut (siehe „Geplant").

## Geplant

- **Hybrid-Freigabe-Gate (chart_race)**: `qa_hard_fail == false` UND Advisory-Wording-Check
  bestanden → Auto-Post, sonst Review-Queue — analog zum Imperium-Gate, aber ohne dessen
  Erstkontakt-Regel (chart_race-Themen sind Live-Daten ohne Recherche-Risiko).
  Voraussetzung: seo-engine liefert den Advisory-Check als `PostingPackage`.
- Review-Queue als sichtbarer Workflow-Status (`pending_review` → `approved`/`rejected` →
  `scheduled` → `posted`), nicht nur als Rückgabewert der Gate-Funktion.
- Pro Plattform ein eigener, wasserzeichenfreier Export (kein Wiederverwenden von z.B. TikTok-Downloads auf YouTube/Instagram — kostet 30–50% Reichweite).
- Posting-Scheduler: Mo–Fr 3×/Tag, Sa/So 2×/Tag, auf YouTube Shorts, TikTok, Instagram Reels, X.
- Anbindung an Plattform-APIs (YouTube Data API, TikTok Content Posting API, Instagram Graph API, X API) bzw. vorerst manuelle/teilautomatisierte Veröffentlichung, falls API-Zugänge fehlen.
- Periodische Re-Verifikation als eigener Reminder-Workflow (heute deckt `sources_verified`
  Staleness implizit ab, aber niemand wird aktiv benachrichtigt, wenn eine Episode verfällt).

## Offen

- Welche Plattform-APIs initial verfügbar sind (Zugangsbeschränkungen, Kosten).
- `PostResult`-Contract (Plattform-Post-ID, Zeitstempel, Status) erst sinnvoll, wenn eine echte
  Posting-Integration existiert — `history.py`s `posts`-Tabelle ist bewusst minimal gehalten
  (nur `topic_id`/`video_id`/`posted_at`), bis dahin.
