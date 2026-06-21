# YouTube Platform Contract

Stand: 2026-06-21

Dieser Ordner beschreibt die YouTube-Schicht von **ValueRacer**. Ziel ist noch kein Upload-Code, sondern ein sauberer Vertrag fuer SEO, Hermes, spaetere Distribution und Analytics.

## Warum eine eigene YouTube-Schicht?

YouTube ist nicht nur ein Upload-Ziel. Fuer ValueRacer besteht YouTube aus vier getrennten Ebenen:

1. Content Packaging: Titel, Thumbnail-Text, Beschreibung, Tags, Hashtags, Quellenhinweis, Disclaimer.
2. Publishing: Upload, Privacy-Status, Scheduling, Thumbnail, Captions, Fehlerbehandlung.
3. Analytics Feedback: Views, Watch Time, Retention-nahe Signale, Likes, neue Subscriber.
4. Keyword Research: Google Ads Keyword Planner als Input fuer Themencluster und SEO, nicht als Auto-Ad-System.

## Dateien

- `YOUTUBE_API_CONTRACT.md` beschreibt, was die spaetere Distribution technisch vorbereiten muss.
- `YOUTUBE_SEO_STANDARD.md` beschreibt, was die SEO Engine fuer YouTube liefern soll.
- `GOOGLE_ADS_RESEARCH.md` beschreibt, wie Google Ads / Keyword Planner als Research-Schicht genutzt wird.

## Grundsatz

YouTube darf spaeter automatisiert vorbereitet werden, aber nicht blind veroeffentlicht werden.

Default bleibt:

```text
privacy_status = private
requires_review = true
ready_to_publish = false
```

Erst nach manueller Freigabe, stabilen Dry-Runs, geklaertem API-Audit-Status und sauberem Content-Review darf eine spaetere Implementierung `public` oder geplante Veroeffentlichung erlauben.

## Beziehung zu Hermes

Hermes soll spaeter nicht direkt die YouTube API erraten. Hermes liest pro Run:

```text
runs/<job_id>/metadata/youtube.json
runs/<job_id>/publish/youtube_publish_plan.json
runs/<job_id>/publish/youtube_upload_result.json
runs/<job_id>/analytics/youtube_snapshot.json
```

Hermes entscheidet dann anhand der maschinenlesbaren Felder, ob gestoppt, reviewed, erneut versucht oder spaeter gepublished wird.

## Keine Secrets im Repo

OAuth Credentials, Refresh Tokens, Client Secrets, API Keys und Google Ads Developer Tokens gehoeren niemals ins Git-Repo. Sie muessen auf dem VPS ueber vorhandene Hermes-/ValueRacer-Environment-Variablen oder einen Secret-Store bereitgestellt werden.
