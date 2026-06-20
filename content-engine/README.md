# content-engine

Rendert die eigentlichen Videos.

## Geplant

- Remotion (React/TypeScript) statt Python/matplotlib — GPU-beschleunigtes Rendering über Chromium, echte Easing-Kurven, kein Ruckeln.
- Diagramm-Typen als austauschbare Templates: Bar Race, Line Race, Pie-Morph, Map/Choropleth, Ranking-Tabelle.
- Visuelle Themes (Farben, Typografie, Übergänge) als separate Variante, kombinierbar mit jedem Diagramm-Typ.
- Rotierende Hook-Intros, damit Videos sich nicht strukturell wiederholen (Vermeidung algorithmischer "templated content"-Abwertung).
- Audio-Mixing (Musik/Voiceover) als Teil der Remotion-Composition.

## Offen

- Referenz-Engine (vom User bereitgestellte ZIP) auf wiederverwendbare Konzepte prüfen, z.B. dynamische X/Y-Achsen-Skalierung.
- Finale Diagramm-Bibliothek (D3.js vs. eigene Implementierung) festlegen.
