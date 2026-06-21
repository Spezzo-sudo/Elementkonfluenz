# Google Ads Research

Stand: 2026-06-21

Dieses Dokument definiert, welche Rolle Google Ads fuer Elementkonfluenz spielen soll. Wichtig: Google Ads ist in der Startphase keine Auto-Werbe-Engine, sondern eine Research-Schicht fuer SEO, Themencluster und Keyword-Priorisierung.

## Offizielle Doku-Basis

- Keyword ideas: https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas
- Historical metrics: https://developers.google.com/google-ads/api/docs/keyword-planning/generate-historical-metrics
- Video campaign limitations: https://developers.google.com/google-ads/api/docs/video/overview

## Ziel

Google Ads / Keyword Planner kann spaeter helfen, bessere YouTube-Metadaten vorzubereiten:

- Keyword-Ideen finden
- Suchvolumen einschaetzen
- Wettbewerbsniveau einschaetzen
- Keyword-Cluster bauen
- Titelvarianten priorisieren
- Themenideen mit Nachfrage-Signalen anreichern

## Nicht-Ziel

Google Ads ist zunaechst nicht fuer automatische Kampagnen gedacht.

Nicht erlaubt in der Startphase:

- automatische Kampagnen-Erstellung
- automatische Budget-Freigabe
- automatische Anzeigenbuchung
- automatische Zielgruppen-Expansion
- automatische Aenderung bestehender Kampagnen

## Warum vorsichtig?

Google Ads API kann Keyword-Ideen und historische Metriken liefern, aber klassische Video-Kampagnen sind eingeschraenkt: Die Google Ads API unterstuetzt laut offizieller Doku nur Abruf und Reporting bestehender Video-Kampagnen; neue Video-Kampagnen erstellen oder bestehende aktualisieren geht darueber nicht. Fuer programmatisches Video-Campaign-Management nennt Google Alternativen wie Google Ads Scripts oder Demand Gen.

## Research Output

Spaetere Research-Ergebnisse sollen in den Run-Ordner geschrieben werden:

```text
runs/<job_id>/research/google_ads_keywords.json
```

Beispiel:

```json
{
  "contract_version": "0.1",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "source": "google_ads_keyword_planner",
  "mode": "dry_run",
  "query_seed": ["gold", "s&p 500", "nasdaq"],
  "geo_targets": ["DE"],
  "language": "de",
  "keyword_ideas": [
    {
      "text": "gold vs aktien",
      "avg_monthly_searches": null,
      "competition": null,
      "competition_index": null,
      "low_top_of_page_bid_micros": null,
      "high_top_of_page_bid_micros": null,
      "use_for": ["tags", "title_variant"]
    }
  ],
  "warnings": [
    "Keyword Planner values may be approximate and should not be treated as factual market data."
  ],
  "requires_review": true
}
```

## SEO-Nutzung

Die SEO Engine darf Google Ads Signale nutzen fuer:

- Tag-Auswahl
- Hashtag-Ideen
- Titelvarianten
- Beschreibungsschwerpunkte
- Themencluster

Die SEO Engine darf Google Ads Signale nicht nutzen fuer:

- Marktprognosen
- Anlageaussagen
- Performance-Versprechen
- Garantien
- automatische Trading- oder Investment-Tipps

## Keyword-Qualitaet

Nicht jedes Keyword mit Suchvolumen passt zu unserem Label. Keywords muessen gefiltert werden.

Ausschliessen:

- "schnell reich werden"
- "kaufen jetzt"
- "garantierter gewinn"
- "geheimtipp aktie"
- Clickbait ohne Datenbezug

Bevorzugen:

- "inflation einfach erklaert"
- "gold vs s&p 500"
- "was ist eine rezession"
- "dollar index erklaert"
- "zinswende auswirkungen"

## Ads Safety Gate

Falls spaeter echte Ads geplant werden, muss ein eigenes Modul entstehen:

```text
ads-engine/
```

Dieses Modul braucht eigene Sicherheitsregeln:

- Budget-Limit
- Kampagnen-Freigabe
- Plattform-Freigabe
- kein Auto-Start
- kein Auto-Budget-Increase
- Review vor jeder Kampagne

Bis dahin gilt:

```text
GOOGLE_ADS_RESEARCH_ONLY=true
```

## Hermes-Regel

Hermes darf Google Ads Research spaeter starten, aber keine Kampagne freigeben.

Erlaubt:

```text
research keywords -> write google_ads_keywords.json -> inform seo-engine
```

Nicht erlaubt:

```text
create campaign -> set budget -> publish ad
```

## Vertrauensniveau

Google Ads Keyword-Metriken sind Nachfrage-/Werbemarkt-Signale. Sie sind keine Beweise fuer wirtschaftliche Realitaet. Ein Video darf also nicht behaupten:

```text
"Dieses Thema ist wichtig, weil das Suchvolumen hoch ist."
```

Besser:

```text
"Dieses Thema hat Suchinteresse und passt zu unserer wirtschaftlichen Einordnung."
```
