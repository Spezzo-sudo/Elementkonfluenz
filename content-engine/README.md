# content-engine

Rendert die eigentlichen Videos. Aufgeteilt in **Brain** (Python, Entscheidungslogik) und
**Renderer** (Remotion/TypeScript, reines Pixel-Malen). Es gibt zwei parallele Content-Verticals,
jede mit eigenem JSON-Contract zwischen Brain und Renderer:

- **chart_race** (Asset-Preis-Vergleiche) — `ScenePlan`, siehe [`SCENE_PLAN.md`](SCENE_PLAN.md).
- **imperium** (Konzern-Dossiers: welche Marken gehören zu wem) — `EmpireScenePlan`, siehe
  [`EMPIRE_SCENE_PLAN.md`](EMPIRE_SCENE_PLAN.md).

Beide Brain-Pakete importieren nie gegenseitig interne Klassen; der Renderer importiert nie
Brain-Code.

## Status

- [`brain/`](brain) — Python-Paket `value_racer_brain`.
  - chart_race-Ast: Daten (yfinance), Kamera-Policy, Zeitachsen-Mapping, Event-Erkennung,
    Dauer-Planung/QA und Advisory-Wording-Check sind aus der alten Engine portiert und laufen
    end-to-end über `python -m value_racer_brain.cli`.
  - imperium-Ast (`value_racer_brain/imperium/`): eigenes Subpackage (`research.py`/`qa.py`/
    `scene_plan.py`/`builder.py`/`cli.py`), liest kuratierte, quellenbelegte Konzern-Recherche aus
    `imperium/data/*.yaml` und baut daraus ein `EmpireScenePlan`. Einziger Live-Datenpunkt ist die
    Endcard-Aktienperformance (yfinance) — Marken/Fakten/Skalenvergleich kommen ausschließlich aus
    der sourced YAML, da es dafür keine API gibt. Erste echte, recherchierte Episode (Nestlé)
    läuft end-to-end durch (`python -m value_racer_brain.imperium.cli build --data
    value_racer_brain/imperium/data/imperium_nestle.yaml --out <pfad>`), Status/Staleness aller
    Episoden über `python -m value_racer_brain.imperium.cli research-status`.
- [`renderer/`](renderer) — Remotion-Projekt, das `ScenePlan`-JSON liest und per `interpolate()`
  echte Kamera-/Event-Übergänge rendert (kein Keyframe-Snapping, kein Ruckeln). Verifiziert per
  `npm run render -- --props=<scene_plan.json>`. Deckt bisher nur den chart_race-Ast ab; eine
  zweite Composition (`ImperiumComposition`) für `EmpireScenePlan` ist noch offen.
- Brain → Renderer End-to-End geprüft (chart_race): ein live aus yfinance generierter
  `scene_plan.json` rendert korrekt mit seiner eigenen Frame-Anzahl/Dauer (nicht nur mit dem
  Beispiel-Plan).

## Geplant

- `ImperiumComposition`-Renderer für `EmpireScenePlan` (Register-Karten, Stempel-Reveal,
  Fakten-Karten, Skalenvergleich, Endcard) — Optik orientiert sich am bereitgestellten
  HTML-Prototyp.
- Weitere Imperium-Episoden über mehrere Sektoren/Regionen, recherchiert in Batches (siehe
  „Automatisierungs-Modell" in [`EMPIRE_SCENE_PLAN.md`](EMPIRE_SCENE_PLAN.md)).
- Diagramm-Typen als austauschbare Templates (chart_race): aktuell nur Bar Race; Line Race, Pie-Morph, Map/Choropleth, Ranking-Tabelle folgen.
- Theme-Pool (mehrere Farb-/Typografie-Sets) und Hook-Intro-Pool mit gewichteter Auswahl, damit sich Videos nicht strukturell wiederholen.
- Audio-Mixing (Musik/Voiceover) als Teil der Remotion-Composition.

## Offen

- Theme-/Hook-Pool-Größe und initiale Gewichtung (vor Anbindung an den Analytics-Feedback-Loop).
- Finale Diagramm-Bibliothek für weitere Diagramm-Typen (D3.js vs. eigene Implementierung).
- HTML-Prototyp für `ImperiumComposition` (liegt noch nicht im Repo).
