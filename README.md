# ValueRacer

Automatisierte Pipeline, die täglich datengetriebene Short-Videos (Bar/Line-Race-Charts, Rankings, Maps) für YouTube Shorts, TikTok, Instagram Reels und X produziert und verteilt. Themenwahl orientiert sich an aktuellen gesellschaftlichen/finanziellen Trends statt an Zufall.

## Module

- [`content-engine/`](content-engine) — Video-Rendering (Remotion), Diagramm-/Theme-Varianten, Audio-Mixing. Zwei Content-Verticals: `chart_race` (Asset-Vergleiche) und `imperium` (Konzern-Dossiers, sourced Recherche statt Live-API).
- [`trend-engine/`](trend-engine) — Themen-Katalog, Trend-Signale (Google Trends, GDELT, RSS), Scoring & Dedup/Cooldown.
- [`seo-engine/`](seo-engine) — Titel-, Hashtag- und Beschreibungs-Generierung pro Plattform.
- [`distribution/`](distribution) — Plattform-spezifische Exporte (wasserzeichenfrei) und Posting-Scheduler.

## Status

Phase 1 (content-engine Kern, chart_race) steht: Brain (Python, portierte Entscheidungslogik) und
Renderer (Remotion) sind end-to-end verifiziert — ein live generierter `ScenePlan` rendert
ruckelfrei mit korrekter eigener Länge. trend-engine hat einen ersten verifizierten
Cross-Vertical-Scorer (`chart_race` vs. `imperium`, siehe
[`trend-engine/README.md`](trend-engine/README.md)). Für die zweite Vertical **imperium** steht
das Brain-Subpackage (`EmpireScenePlan`-Contract, sourced Recherche, strukturelle QA,
Staleness-Tracking) UND der Renderer (`EmpireScenePlanComposition`, sieben Phasen-Komponenten)
mit vier echten, recherchierten Episoden über vier Sektoren/Regionen (Nestlé, LVMH, Alphabet,
Toyota) end-to-end verifiziert — Details in [`content-engine/README.md`](content-engine/README.md).
seo-engine und distribution sind noch Konzeptphase, Details in den jeweiligen README-Dateien der
Module.
