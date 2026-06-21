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
    `imperium/data/*.yaml` und baut daraus ein `EmpireScenePlan`. Wie eine neue Episode
    recherchiert/befüllt wird (Feld-für-Feld-Schema, Quellenregeln, Ownership-Genauigkeitscheck,
    Checkliste) ist vollständig spezifiziert in
    [`imperium/RESEARCH_GUIDE.md`](brain/value_racer_brain/imperium/RESEARCH_GUIDE.md) — diese
    Recherche ist bewusst nicht automatisierbar (keine API für „welche Marken gehören zu Konzern
    X"), die Spezifikation macht sie aber an einen Menschen oder eine andere KI delegierbar, ohne
    weiteren Kontext aus diesem Projekt zu brauchen. Einziger Live-Datenpunkt ist die
    Endcard-Aktienperformance (yfinance) — Marken/Fakten/Skalenvergleich kommen ausschließlich aus
    der sourced YAML, da es dafür keine API gibt. Vier echte, recherchierte Episoden über
    verschiedene Sektoren/Regionen laufen end-to-end durch (`python -m
    value_racer_brain.imperium.cli build --data value_racer_brain/imperium/data/imperium_<id>.yaml
    --out <pfad>`): Nestlé (`consumer_goods`/EU), LVMH (`luxury`/EU), Alphabet (`tech`/US), Toyota
    (`automotive`/APAC). Status/Staleness aller Episoden über `python -m
    value_racer_brain.imperium.cli research-status`.
- [`renderer/`](renderer) — Remotion-Projekt mit zwei parallelen Compositions, beide ohne
  Geschäftslogik (reines Pixel-Malen aus dem jeweiligen JSON-Contract):
  - `ScenePlan` (chart_race, 1920×1080) — liest `ScenePlan`-JSON und rendert per `interpolate()`
    echte Kamera-/Event-Übergänge (kein Keyframe-Snapping, kein Ruckeln). Verifiziert per
    `npm run render -- --props=<scene_plan.json>`; ein live aus yfinance generierter Plan
    rendert korrekt mit seiner eigenen Frame-Anzahl/Dauer (nicht nur mit dem Beispiel-Plan).
  - `EmpireScenePlan` (imperium, 1080×1920) — liest `EmpireScenePlan`-JSON, sieben
    Phasen-Komponenten unter `src/components/imperium/` (Hook, Register-Karten-Cascade, Beat,
    Stempel-Reveal via `spring()`, Fakten-Karten, Skalenvergleich-Balken, Endcard). Verifiziert
    per `npm run render:imperium` gegen alle vier echten Episoden (Nestlé, LVMH, Alphabet, Toyota:
    Typecheck clean, voller Render 630/630 Frames, alle sieben Phasen per `remotion still` visuell
    geprüft — u.a. lange Markennamen, zweizeilige Headlines, sehr große/dezimale
    Skalenvergleichswerte, "Bio."- statt "Mrd."-Einheiten). Da kein Original-HTML/CSS-Prototyp im
    Repo liegt, ist die Optik direkt aus dem `EMPIRE_SCENE_PLAN.md`-Contract und den
    Design-Notizen abgeleitet, nicht 1:1 portiert.

## Geplant

- Weitere Imperium-Episoden über mehrere Sektoren/Regionen, recherchiert in Batches (siehe
  „Automatisierungs-Modell" in [`EMPIRE_SCENE_PLAN.md`](EMPIRE_SCENE_PLAN.md)).
- Diagramm-Typen als austauschbare Templates (chart_race): aktuell nur Bar Race; Line Race, Pie-Morph, Map/Choropleth, Ranking-Tabelle folgen.
- Theme-Pool (mehrere Farb-/Typografie-Sets) und Hook-Intro-Pool mit gewichteter Auswahl, damit sich Videos nicht strukturell wiederholen.
- Audio-Mixing (Musik/Voiceover) als Teil der Remotion-Composition.

## Offen

- Theme-/Hook-Pool-Größe und initiale Gewichtung (vor Anbindung an den Analytics-Feedback-Loop).
- Finale Diagramm-Bibliothek für weitere Diagramm-Typen (D3.js vs. eigene Implementierung).
- Original-HTML/CSS-Prototyp für `imperium` liegt nicht im Repo — die `EmpireScenePlan`-Composition
  wurde daher aus dem Contract und den Design-Notizen heraus gebaut, nicht 1:1 portiert. Ein
  späterer visueller Abgleich gegen den Prototyp (falls verfügbar gemacht) steht noch aus.
