# Projektstatus: ValueRacer

Stand: 2026-06-21

## Kurzfassung

**ValueRacer** ist aktuell als automatisierte Pipeline fuer datengetriebene Short-Videos angelegt. Ziel ist eine taegliche Produktion von Bar-/Line-Race-Charts, Rankings und Maps fuer YouTube Shorts, TikTok, Instagram Reels und X. Die Themenwahl soll spaeter ueber aktuelle gesellschaftliche und finanzielle Trends erfolgen, nicht zufaellig.

Der alte Arbeitsname `Elementkonfluenz` wurde abgeloest. Er kann in historischen Commits, offenen PRs oder internen Paketnamen noch vorkommen, soll aber nicht mehr fuer Produktkommunikation, VPS-Zielpfade oder neue Dokumentation verwendet werden.

Das urspruengliche Unreal-/Tower-Defense-Konzept wurde mit PR #1 zurueckgesetzt und durch die neue Pipeline-Struktur ersetzt.

## Aktueller Architekturstand

```text
ValueRacer/
├── content-engine/     # Video-Erzeugung: Python-Brain + Remotion-Renderer
├── trend-engine/       # Themenfindung und Trend-Scoring, derzeit Konzept
├── seo-engine/         # Titel, Hashtags, Beschreibungen, derzeit Konzept
└── distribution/       # Exporte und Posting-Scheduler, derzeit Konzept
```

## Naming-Status

- Produktname: `ValueRacer`
- Empfohlener VPS-Zielpfad: `/srv/valueracer`
- Alter Arbeitsname: `Elementkonfluenz`
- GitHub-Repo-Name: kann noch `Elementkonfluenz` sein, bis er manuell in GitHub umbenannt wurde.
- Interner Python-Brain-Paketname: aktuell noch `elementkonfluenz_brain`, spaetere Umbenennung geplant.

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
- Paketname: `elementkonfluenz_brain` (Legacy; spaeter auf ValueRacer-Namespace migrieren)
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

1. Offene PRs mit altem Namen pruefen und nachziehen, bevor sie gemerged werden.
2. Repo-Name und VPS-Verzeichnis auf `ValueRacer` umstellen, aber mit Backup und Rollback.
3. Python-Brain-Namespace spaeter kontrolliert umbenennen oder Kompatibilitaets-Alias bereitstellen.
4. Lokal/CI reproduzierbaren End-to-End-Render-Check definieren.
5. Trend Engine minimal implementieren: Themenkatalog + einfacher Scoring-Prototyp.
6. SEO Engine minimal implementieren: regelbasierte Metadaten pro Plattform.
7. Renderer auf Zielplattform-Format pruefen: aktuell ist die Root-Komposition auf 1920x1080 gesetzt; fuer Shorts/Reels/TikTok ist spaeter 1080x1920 relevant.
8. Weitere Video-Templates planen: Line Race, Pie-Morph, Map/Choropleth, Ranking-Tabelle.
9. Distribution als trockenen Export-/Scheduler-Prototyp starten, bevor echte API-Posts erfolgen.

## Naechster empfohlener Entwicklungsschritt

Als naechster sauberer Schritt sollte die Namensmigration abgeschlossen werden:

- Doku und VPS-Pfade auf `ValueRacer` setzen.
- Offene PRs auf alten Namen pruefen.
- Altes GitHub-Repository optional in GitHub selbst umbenennen.
- Interne Paketnamen nur mit CI und Kompatibilitaetsplan umstellen.

Danach ist ein kleiner, sicher testbarer MVP fuer `seo-engine` sinnvoll.
