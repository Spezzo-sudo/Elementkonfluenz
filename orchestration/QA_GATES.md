# ValueRacer QA Gates

Stand: 2026-06-21

Dieses Dokument definiert die Qualitaetspruefungen, die ein ValueRacer-Run bestehen muss, bevor ein Video ueberhaupt als reviewfaehig oder spaeter publishbar gilt.

## Grundsatz

ValueRacer darf aufmerksamkeitsstark sein, aber nicht ungenau. Jede starke Hook braucht eine ehrliche datenbasierte Aufloesung.

```text
Hook stark -> Daten korrekt -> Einordnung ehrlich -> Review sichtbar
```

## QA-Artefakt

Jeder vollstaendige Run soll spaeter schreiben:

```text
runs/<job_id>/qa.json
```

Minimal:

```json
{
  "contract_version": "0.1",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "ok": true,
  "hard_fail": false,
  "requires_review": true,
  "ready_to_publish": false,
  "checks": []
}
```

## Check-Kategorien

### 1. Topic QA

Prueft, ob das Thema ueberhaupt sauber formulierbar ist.

Hard Fail, wenn:

- Thema eine sichere Prognose behauptet
- Thema eine Kauf-/Verkaufsempfehlung ist
- Thema politisch oder finanziell brisant ist und keine Review-Markierung hat
- Thema keinen klaren Zeitraum oder Vergleichsrahmen erlaubt

### 2. Data QA

Prueft, ob Daten vorhanden und plausibel sind.

Hard Fail, wenn:

- keine Daten geladen wurden
- Daten zu alt sind
- zu viele Luecken vorhanden sind
- Start-/Endwert fehlt
- Rendite-/Indexberechnung nicht reproduzierbar ist
- Waehrungen/Einheiten vermischt werden, ohne es zu markieren

Warnung, wenn:

- Zeitraum kurz ist
- Datenquelle approximativ ist
- ein Asset extreme Ausreisser hat
- Daten nicht fuer alle Assets denselben Zeitraum abdecken

### 3. Source QA

Prueft, ob Quellen nachvollziehbar sind.

Hard Fail, wenn:

- `sources.json` fehlt
- keine Abrufzeit dokumentiert ist
- keine Datenquelle genannt wird

Warnung, wenn:

- Quelle nur ein Research-Signal ist, z. B. Keyword Planner
- Quelle keinen wirtschaftlichen Fakt belegt, sondern nur Nachfrage/Interesse zeigt

### 4. Advisory QA

Prueft, ob Anlageberatungsgrenzen eingehalten werden.

Hard Fail, wenn Titel, Script oder Beschreibung enthalten:

- Kaufaufforderung
- Verkaufsaufforderung
- garantierter Gewinn
- sichere Rendite
- kein Risiko
- All-in-Framing

Warnung, wenn:

- stark zugespitzte Finanzsprache genutzt wird
- Crash-/Chance-Framing vorkommt

### 5. Clickbait Integrity QA

Prueft, ob Titel/Thumbnail ehrlich aufgeloest werden.

Hard Fail, wenn:

- Titel eine absolute Aussage macht, die Daten nicht belegen
- Thumbnail Zahlen zeigt, die nicht im Video vorkommen
- Hook Panik erzeugt, aber keine Datenbasis vorhanden ist
- Beschreibung eine andere Story verspricht als das Video liefert

### 6. Repetition QA

Prueft, ob sich Video, Thema oder Template zu stark wiederholen.

Hard Fail, wenn:

- exakt dasselbe Thema innerhalb des Cooldowns erneut geplant wird
- derselbe Run erneut unter neuer Job-ID erzeugt wird

Warnung, wenn:

- gleiche Asset-Kombination mehrfach in kurzer Zeit verwendet wird
- gleicher Video-Typ zu oft hintereinander genutzt wird
- Thumbnail-Struktur zu aehnlich ist

### 7. Visual QA

Prueft, ob das Video technisch und visuell zur Plattform passt.

Hard Fail, wenn:

- Render-Datei fehlt
- falsches Seitenverhaeltnis fuer Shorts/Reels/TikTok
- Text ausserhalb Safe Area
- wichtige Labels unlesbar
- Dauer ausserhalb Zielkorridor

Warnung, wenn:

- wenig visuelle Abwechslung
- zu viele Zahlen gleichzeitig
- schwache Lesbarkeit auf Mobile

## QA-Ergebnislogik

```text
hard_fail=true  -> nicht publishbar, Review zwingend
warnings>0      -> reviewfaehig, aber nicht automatisch publishbar
all clear       -> weiterhin requires_review bis Produktionsfreigabe
```

Bis Auto-Publishing explizit freigegeben wurde, bleibt:

```json
{
  "requires_review": true,
  "ready_to_publish": false
}
```

## Fehlercodes

Empfohlene QA-Fehlercodes:

```text
QA_TOPIC_UNSAFE
QA_DATA_MISSING
QA_DATA_STALE
QA_DATA_INCONSISTENT
QA_SOURCES_MISSING
QA_ADVISORY_FLAGGED
QA_CLICKBAIT_MISMATCH
QA_REPETITION_BLOCKED
QA_RENDER_MISSING
QA_VISUAL_UNSAFE
```

## Hermes-Verhalten

Hermes liest `qa.json` und `job_result.json`.

Hermes darf:

- Nutzer informieren
- Retry bei technischen Fehlern starten
- Runs fuer Review markieren

Hermes darf nicht:

- `hard_fail=true` uebergehen
- Auto-Publishing trotz `requires_review=true` aktivieren
- Content-Regeln ignorieren
