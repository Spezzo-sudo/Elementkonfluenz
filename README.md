# Elementkonfluenz

Automatisierte Pipeline, die täglich datengetriebene Short-Videos (Bar/Line-Race-Charts, Rankings, Maps) für YouTube Shorts, TikTok, Instagram Reels und X produziert und verteilt. Themenwahl orientiert sich an aktuellen gesellschaftlichen/finanziellen Trends statt an Zufall.

> Arbeitstitel — Projekt wird umbenannt, sobald sich ein endgültiger Name ergibt.

## Module

- [`content-engine/`](content-engine) — Video-Rendering (Remotion), Diagramm-/Theme-Varianten, Audio-Mixing.
- [`trend-engine/`](trend-engine) — Themen-Katalog, Trend-Signale (Google Trends, GDELT, RSS), Scoring & Dedup/Cooldown.
- [`seo-engine/`](seo-engine) — Titel-, Hashtag- und Beschreibungs-Generierung pro Plattform.
- [`distribution/`](distribution) — Plattform-spezifische Exporte (wasserzeichenfrei) und Posting-Scheduler.

## Status

Phase 1 (content-engine Kern) steht: Brain (Python, portierte Entscheidungslogik) und Renderer
(Remotion) sind end-to-end verifiziert — ein live generierter `ScenePlan` rendert ruckelfrei mit
korrekter eigener Länge. trend-engine, seo-engine und distribution sind noch Konzeptphase, Details
in den jeweiligen README-Dateien der Module.
