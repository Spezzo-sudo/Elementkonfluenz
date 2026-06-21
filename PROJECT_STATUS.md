# Projektstatus: Elementkonfluenz

Stand: 2026-06-21

## Kurzfassung

Elementkonfluenz ist aktuell als automatisierte Pipeline fuer datengetriebene Short-Videos angelegt. Ziel ist eine taegliche Produktion von Bar-/Line-Race-Charts, Rankings und Maps fuer YouTube Shorts, TikTok, Instagram Reels und X. Die Themenwahl soll spaeter ueber aktuelle gesellschaftliche und finanzielle Trends erfolgen, nicht zufaellig.

Das urspruengliche Unreal-/Tower-Defense-Konzept wurde mit PR #1 zurueckgesetzt und durch die neue Pipeline-Struktur ersetzt.

## Aktueller Architekturstand

```text
Elementkonfluenz/
├── content-engine/     # Video-Erzeugung: Python-Brain + Remotion-Renderer
├── trend-engine/       # Themenfindung und Trend-Scoring, derzeit Konzept
├── seo-engine/         # Titel, Hashtags, Beschreibungen, derzeit Konzept
└── distribution/       # Exporte und Posting-Scheduler, derzeit Konzept
```

## Modulstatus

### content-engine

Status: Phase-1-Kern vorhanden.

Die Content Engine ist in zwei Teile getrennt:

- `brain/`: Python-Paket `elementkonfluenz_brain`, erzeugt versionierte `ScenePlan`-JSON-Dokumente.
- `renderer/`: Remotion-/TypeScript-Projekt, rendert Videos aus einem `ScenePlan`.

Bereits angelegt:

- Datenpipeline mit `yfinance`
- Kamera-Policy
- Zeitachsen-Mapping
- Event-Erkennung
- Dauerplanung und QA
- Advisory-Wording-Check
- Remotion-Komposition mit dynamischer Dauer aus dem `ScenePlan`
- Bar-Race-Rendering als erstes Template

### trend-engine

Status: Konzept.

Geplant sind:

- Themen-Katalog mit verfuegbaren Datensaetzen
- Trend-Signale aus Google Trends, GDELT und RSS
- Scoring gegen aktuelle Trend-Keywords
- Dedup/Cooldown per SQLite
- Fallback-Round-Robin

### seo-engine

Status: Konzept.

Geplant sind:

- Plattform-spezifische Titel
- Hashtags
- Beschreibungen
- unterschiedliche Tonalitaet fuer YouTube Shorts, TikTok, Instagram und X

Offen ist, ob die erste Version regelbasiert oder LLM-gestuetzt laufen soll.

### distribution

Status: Konzept.

Geplant sind:

- wasserzeichenfreie Exporte pro Plattform
- Posting-Scheduler
- spaetere API-Anbindungen fuer YouTube, TikTok, Instagram und X

## Technischer Stand

### Python-Brain

Pfad: `content-engine/brain/`

- Python: `>=3.11`
- Paketname: `elementkonfluenz_brain`
- Hauptentrypoint: `python -m elementkonfluenz_brain.cli`
- Kern-Abhaengigkeiten: `pandas`, `numpy`, `yfinance`, `pydantic`

Beispielhafter Flow:

```bash
cd content-engine/brain
python -m elementkonfluenz_brain.cli \
  --tickers BTC-USD,^GSPC,GC=F \
  --days 1825 \
  --out ../renderer/scene_plan.json \
  --locale de \
  --fps 30 \
  --investment 1000 \
  --mode evergreen
```

### Remotion-Renderer

Pfad: `content-engine/renderer/`

Wichtige Scripts:

```bash
npm run dev
npm run build
npm run render -- --props=<scene_plan.json>
npm run typecheck
```

Der Renderer soll keine Businesslogik enthalten. Er liest nur den `ScenePlan` und rendert Frames.

## Wichtigste offene Punkte

1. Repo-Qualitaet absichern: GitHub Actions fuer Python-Brain und Remotion-Renderer anlegen.
2. Lokal/CI reproduzierbaren End-to-End-Render-Check definieren.
3. Trend Engine minimal implementieren: Themenkatalog + einfacher Scoring-Prototyp.
4. SEO Engine minimal implementieren: regelbasierte Metadaten pro Plattform.
5. Renderer auf Zielplattform-Format pruefen: aktuell ist die Root-Komposition auf 1920x1080 gesetzt; fuer Shorts/Reels/TikTok ist spaeter 1080x1920 relevant.
6. Weitere Video-Templates planen: Line Race, Pie-Morph, Map/Choropleth, Ranking-Tabelle.
7. Distribution als trockenen Export-/Scheduler-Prototyp starten, bevor echte API-Posts erfolgen.

## Naechster empfohlener Entwicklungsschritt

Als naechster sauberer Schritt sollte eine CI-Basis entstehen:

- Python: installierbares Brain-Paket pruefen und CLI importierbar machen.
- TypeScript: `npm ci` und `npm run typecheck` fuer den Renderer.
- Dokumentation: klarer `CONTRIBUTING`-/Run-Abschnitt fuer lokale Entwicklung.

Danach ist ein kleiner, sicher testbarer MVP fuer `trend-engine` sinnvoll.
