# YouTube API Contract

Stand: 2026-06-21

Dieses Dokument beschreibt den spaeteren YouTube-Publishing-Vertrag fuer **ValueRacer**. Es ist bewusst eine Spezifikation, kein Upload-Code. Die spaetere Implementierung muss sich daran halten, damit Hermes sicher, nachvollziehbar und ohne Datenverlust arbeiten kann.

## Offizielle Doku-Basis

- Videos upload: https://developers.google.com/youtube/v3/docs/videos/insert
- Resumable uploads: https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol
- Thumbnails: https://developers.google.com/youtube/v3/docs/thumbnails/set
- Captions: https://developers.google.com/youtube/v3/docs/captions
- Analytics reports: https://developers.google.com/youtube/analytics/reference/reports/query

## Was YouTube Publishing spaeter koennen soll

Die YouTube-Schicht soll spaeter diese Schritte unterstuetzen:

1. Publish Plan aus vorhandenen Run-Artefakten erzeugen.
2. Video-Datei pruefen.
3. Thumbnail-Datei pruefen.
4. Captions-Datei pruefen.
5. Upload vorbereiten.
6. Video initial immer `private` oder `unlisted` hochladen.
7. Thumbnail setzen.
8. Captions hochladen.
9. Upload-Ergebnis speichern.
10. Analytics-Snapshot spaeter abrufen.

## Wichtige YouTube Data API Fakten

### Video Upload

`videos.insert` laedt Videos hoch und kann Metadaten setzen. Relevante setzbare Felder sind unter anderem:

- `snippet.title`
- `snippet.description`
- `snippet.tags[]`
- `snippet.categoryId`
- `snippet.defaultLanguage`
- `status.privacyStatus`
- `status.publishAt`
- `status.selfDeclaredMadeForKids`
- `status.containsSyntheticMedia`

Wichtig: Laut YouTube werden Uploads ueber unverifizierte API-Projekte, die nach dem 28. Juli 2020 erstellt wurden, auf private Sichtbarkeit beschraenkt, bis das API-Projekt ein Audit bestanden hat. Deshalb darf ValueRacer nie davon ausgehen, dass ein API-Upload sofort oeffentlich werden kann.

### Resumable Uploads

Fuer VPS/Hermes ist resumable upload Pflicht, sobald echter Upload-Code gebaut wird. Das reduziert Risiko bei grossen Dateien und instabilen Netzwerken.

Contract-Regel:

- Upload-Session starten.
- Upload-Session-URI sicher im Run-Ordner speichern.
- Datei per `PUT` hochladen.
- Bei Unterbrechung Status abfragen.
- Bei `308 Resume Incomplete` fortsetzen.
- Bei permanentem Fehler `youtube_upload_result.json` mit `ok=false` schreiben.

### Thumbnail Upload

Custom Thumbnails werden ueber `thumbnails.set` gesetzt. Die API akzeptiert JPEG/PNG und hat eine maximale Dateigroesse von 2 MB.

Contract-Regel:

- Thumbnail muss vor Upload lokal validiert werden.
- Dateigroesse muss <= 2 MB sein.
- Erlaubte MIME-Typen: `image/jpeg`, `image/png`.
- Wenn zu gross: nicht hochladen, `requires_review=true`.

### Captions

YouTube Captions koennen ueber API gelistet, eingefuegt, aktualisiert, heruntergeladen und geloescht werden. Der `sync` Parameter fuer `captions.insert` und `captions.update` ist deprecated; Auto-Sync bleibt in Creator Studio verfuegbar.

Contract-Regel:

- ValueRacer soll eigene `.srt` oder `.vtt` mit Timing erzeugen.
- Keine Abhaengigkeit auf API-Auto-Sync.
- Captions bleiben bei Fehlern nicht stillschweigend weg, sondern erzeugen Warnung und Review-Pflicht.

### Analytics

YouTube Analytics API kann Reports fuer Channel oder Content Owner abrufen. Relevante Felder sind z. B. `views`, `likes`, `estimatedMinutesWatched`, `averageViewDuration`, `averageViewPercentage`, `subscribersGained`, Dimensionen wie `day`, `video`, `country` und Filter.

Contract-Regel:

- Analytics wird als Feedback-Schicht behandelt, nicht als Publishing-Voraussetzung.
- Analytics-Snapshots werden zeitversetzt abgerufen, z. B. nach 24h, 72h, 7d.
- Kein Video wird geloescht oder geaendert, nur weil ein Analytics-Wert schlecht ist.

## Publish Plan

Die Distribution darf nicht direkt hochladen. Sie muss zuerst einen Publish Plan erzeugen:

```json
{
  "contract_version": "0.1",
  "platform": "youtube",
  "mode": "dry_run",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "video_file": "render.mp4",
  "thumbnail_file": "thumbnail.jpg",
  "caption_file": "captions.de.srt",
  "metadata_file": "metadata/youtube.json",
  "privacy_status": "private",
  "publish_at": null,
  "notify_subscribers": false,
  "made_for_kids": false,
  "contains_synthetic_media": true,
  "requires_review": true,
  "ready_to_publish": false
}
```

## Privacy-Regeln

Default:

```text
private
```

Erlaubte Werte fuer spaetere Implementierung:

- `private`
- `unlisted`
- `public`

`public` darf nur erlaubt werden, wenn:

- Upload-Testlaeufe stabil sind,
- YouTube API Audit/Projektstatus geklaert ist,
- Content Review bestanden ist,
- `qa.hard_fail == false`,
- `advisory_check.flagged == false`,
- Nutzer Auto-Publishing ausdruecklich freigegeben hat.

## Scheduling

Wenn `publish_at` gesetzt wird:

- Video muss initial mit passendem Privacy-/Scheduling-Status vorbereitet werden.
- Zeitpunkt muss ISO 8601 sein.
- Hermes muss lokale Zeitzone und UTC-Konvertierung eindeutig loggen.
- Fehler beim Scheduling duerfen nicht zu sofortigem Public-Upload fuehren.

## Upload Result

Nach jedem echten oder simulierten Upload muss `youtube_upload_result.json` geschrieben werden.

Erfolg:

```json
{
  "contract_version": "0.1",
  "platform": "youtube",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "ok": true,
  "mode": "dry_run",
  "video_id": null,
  "privacy_status": "private",
  "uploaded_at": null,
  "thumbnail_set": false,
  "captions_uploaded": false,
  "requires_review": true,
  "ready_to_publish": false,
  "warnings": []
}
```

Fehler:

```json
{
  "contract_version": "0.1",
  "platform": "youtube",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "ok": false,
  "mode": "publish",
  "error_code": "YOUTUBE_UPLOAD_FAILED",
  "message": "Upload failed before YouTube returned a video id.",
  "retryable": true,
  "requires_review": true,
  "ready_to_publish": false,
  "warnings": ["No public video was created."]
}
```

## Fehlerklassen

Empfohlene Fehlercodes:

- `YOUTUBE_AUTH_MISSING`
- `YOUTUBE_AUTH_EXPIRED`
- `YOUTUBE_PROJECT_UNVERIFIED_PRIVATE_ONLY`
- `YOUTUBE_UPLOAD_SESSION_FAILED`
- `YOUTUBE_UPLOAD_INTERRUPTED`
- `YOUTUBE_UPLOAD_FAILED`
- `YOUTUBE_THUMBNAIL_TOO_LARGE`
- `YOUTUBE_THUMBNAIL_INVALID_TYPE`
- `YOUTUBE_CAPTION_UPLOAD_FAILED`
- `YOUTUBE_SCHEDULING_FAILED`
- `YOUTUBE_QUOTA_EXCEEDED`
- `YOUTUBE_RATE_LIMITED`

## Secrets und Environment

Keine YouTube Secrets im Repo. Vorhandene VPS-/Hermes-Secrets sollen gelesen werden, nicht neu erzeugt oder ueberschrieben.

Vorgesehene Environment-Variablen:

```text
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
YOUTUBE_CHANNEL_ID
YOUTUBE_DEFAULT_PRIVACY_STATUS=private
YOUTUBE_DRY_RUN=true
```

ValueRacer-spezifische Steuerung:

```text
VALUERACER_DRY_RUN=true
VALUERACER_RUNS_DIR=/srv/valueracer/runs
```

## Nicht-Ziele dieses Contracts

Dieser PR implementiert nicht:

- echten OAuth Flow,
- echten Video Upload,
- echte Thumbnail-Uploads,
- echte Captions-Uploads,
- echtes Scheduling,
- Auto-Publishing.

Diese Dinge kommen erst spaeter, wenn Contract, Dry-Run, Review und Migration stabil sind.
