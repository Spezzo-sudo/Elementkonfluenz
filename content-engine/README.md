# content-engine

Rendert die eigentlichen Videos. Aufgeteilt in **Brain** (Python, Entscheidungslogik) und
**Renderer** (Remotion/TypeScript, reines Pixel-Malen). Beide kommunizieren ausschließlich
über den versionierten `ScenePlan`-JSON-Contract — siehe [`SCENE_PLAN.md`](SCENE_PLAN.md).

## Status

- [`brain/`](brain) — Python-Paket `value_racer_brain`. Daten (yfinance), Kamera-Policy,
  Zeitachsen-Mapping, Event-Erkennung, Dauer-Planung/QA und Advisory-Wording-Check sind aus der
  alten Engine portiert und laufen end-to-end über `python -m value_racer_brain.cli`.
- [`renderer/`](renderer) — Remotion-Projekt, das `ScenePlan`-JSON liest und per `interpolate()`
  echte Kamera-/Event-Übergänge rendert (kein Keyframe-Snapping, kein Ruckeln). Verifiziert per
  `npm run render -- --props=<scene_plan.json>`.
- Brain → Renderer End-to-End geprüft: ein live aus yfinance generierter `scene_plan.json` rendert
  korrekt mit seiner eigenen Frame-Anzahl/Dauer (nicht nur mit dem Beispiel-Plan).

## Geplant

- Diagramm-Typen als austauschbare Templates: aktuell nur Bar Race; Line Race, Pie-Morph, Map/Choropleth, Ranking-Tabelle folgen.
- Theme-Pool (mehrere Farb-/Typografie-Sets) und Hook-Intro-Pool mit gewichteter Auswahl, damit sich Videos nicht strukturell wiederholen.
- Audio-Mixing (Musik/Voiceover) als Teil der Remotion-Composition.

## Offen

- Theme-/Hook-Pool-Größe und initiale Gewichtung (vor Anbindung an den Analytics-Feedback-Loop).
- Finale Diagramm-Bibliothek für weitere Diagramm-Typen (D3.js vs. eigene Implementierung).
