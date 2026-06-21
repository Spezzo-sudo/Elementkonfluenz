# ValueRacer seo-engine

Generiert Plattform-Metadaten aus einem ValueRacer Topic Brief. Die erste Implementierung ist bewusst ein sicherer YouTube-Dry-Run: keine API-Aufrufe, keine Secrets, kein Posting.

## Ziel der ersten Version

Aus einem vorhandenen Run-Ordner mit `topic_brief.json` und optional `sources.json` werden erzeugt:

```text
runs/<job_id>/metadata/youtube.json
runs/<job_id>/publish/youtube_publish_plan.json
```

## Quickstart

```bash
cd seo-engine
python -m pip install -e .
python -m valueracer_seo.cli \
  --dry-run \
  --run-dir ../runs/test-gold-sp500
```

Oder mit explizitem Topic Brief:

```bash
python -m valueracer_seo.cli \
  --dry-run \
  --topic-brief ../runs/test-gold-sp500/topic_brief.json \
  --sources ../runs/test-gold-sp500/sources.json \
  --out-dir ../runs/test-gold-sp500
```

## Sicherheitsregeln

- `--dry-run` ist Pflicht.
- `privacy_status` bleibt `private`.
- `requires_review` bleibt `true`.
- `ready_to_publish` bleibt `false`.
- Keine YouTube API wird aufgerufen.
- Keine Google Ads API wird aufgerufen.
- Keine Secrets werden gelesen oder geschrieben.

## Geplant

- YouTube Shorts: Keyword in den ersten 3 Wörtern des Titels, deskriptiver Titel, `#Shorts` als erstes Hashtag in der Beschreibung, 3–5 Hashtags gesamt.
- TikTok/Instagram/X: eigene, plattformtypische Tonalität statt 1:1-Kopie des YouTube-Texts.
- Google Ads Keyword Planner spaeter nur als Research-Schicht, nicht als Auto-Ad-System.

## Offen

- Regelbasierte Generierung vs. LLM-gestützt.
- Erweiterung auf TikTok, Instagram und X.
- Integration in den Orchestrator als `--with-youtube-seo`.
