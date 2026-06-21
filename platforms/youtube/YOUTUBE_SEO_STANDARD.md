# YouTube SEO Standard

Stand: 2026-06-21

Dieses Dokument definiert, was die SEO Engine fuer YouTube liefern muss. Ziel ist ein starkes, klickbares Packaging, ohne die rote Linie des Projekts zu verletzen: wahrheitsgemaess, datenbasiert, einordnend, keine Anlageberatung.

## Grundsatz

```text
Titel und Thumbnail duerfen neugierig machen.
Das Video muss die Zuspitzung ehrlich aufloesen.
```

YouTube SEO ist hier kein Trick zum Ueberlisten des Algorithmus, sondern eine Verpackungsschicht fuer gute, verstaendliche Wirtschafts- und Finanzvideos.

## Output-Datei

Die SEO Engine soll pro Run schreiben:

```text
runs/<job_id>/metadata/youtube.json
```

Minimaler Inhalt:

```json
{
  "contract_version": "0.1",
  "platform": "youtube",
  "job_id": "2026-06-21_093000_gold-vs-sp500",
  "title": "Gold gegen Tech: Wer hat wirklich geliefert?",
  "description": "Wir vergleichen Gold, Nasdaq und S&P 500 ueber denselben Zeitraum. Keine Anlageberatung, nur eine datenbasierte Einordnung.",
  "tags": ["gold", "sp500", "nasdaq", "wirtschaft", "finanzen"],
  "hashtags": ["#Wirtschaft", "#Finanzen", "#Gold"],
  "thumbnail_text": "Gold vs Tech",
  "default_language": "de",
  "category_id": "25",
  "made_for_kids": false,
  "contains_synthetic_media": true,
  "source_disclaimer": "Datenstand und Quellen siehe Quellenmanifest im Run-Ordner.",
  "advisory_check": {
    "flagged": false,
    "matched_keywords": [],
    "suggestions": []
  },
  "clickbait_integrity_check": {
    "passed": true,
    "reason": "Titel stellt eine Frage und wird im Video datenbasiert eingeordnet."
  },
  "requires_review": true
}
```

## Titel-Regeln

Erlaubt:

- starke Frage
- klarer Vergleich
- neugieriger Gegensatz
- Zeithorizont im Video klar nennen
- keine sichere Prognose behaupten

Beispiele:

- "Gold gegen Tech: Wer hat wirklich geliefert?"
- "Der Dollar verliert Macht? Das zeigen die Daten"
- "Bitcoin vs. S&P 500: Der Vergleich ueberrascht"
- "Warum alle wieder ueber Rohstoffe reden"
- "Diese 3 Maerkte erzaehlen gerade dieselbe Geschichte"

Nicht erlaubt:

- "Kauf das jetzt"
- "Dieser Coin macht dich reich"
- "Der sichere Crash kommt"
- "100% Gewinnchance"
- "Banken verschweigen dir diese Wahrheit"

## Thumbnail-Regeln

Thumbnail darf kurz, stark und visuell sein.

Erlaubt:

- 2 bis 5 Woerter
- klare Gegensaetze: "Gold vs Tech", "Dollar schwach?", "Crash oder Chance?"
- Fragezeichen, wenn das Video die Frage beantwortet

Nicht erlaubt:

- absolute Behauptungen ohne Beleg
- Kaufaufforderungen
- Panikversprechen
- erfundene Zahlen

## Beschreibung

Die Beschreibung soll enthalten:

1. kurze Inhaltszusammenfassung,
2. Zeitraum/Datenbasis,
3. Quellenhinweis,
4. keine Anlageberatung,
5. optional Kapitel/Gliederung,
6. Hashtags am Ende.

Beispielstruktur:

```text
In diesem Video vergleichen wir Gold, den S&P 500 und den Nasdaq ueber denselben Zeitraum.
Ziel ist keine Prognose, sondern eine datenbasierte Einordnung: Welche Entwicklung sieht man, wenn man denselben Startpunkt nutzt?

Hinweis: Keine Anlageberatung. Datenstand und Quellen werden intern im Quellenmanifest des Runs gespeichert.

#Wirtschaft #Finanzen #Gold
```

## Tags vs. Hashtags

Tags sind technische Such-/Kontextsignale. Hashtags sind sichtbare Content-Signale.

Tags:

- `gold`
- `sp500`
- `nasdaq`
- `inflation`
- `wirtschaft`
- `finanzen`

Hashtags:

- `#Wirtschaft`
- `#Finanzen`
- `#Boerse`
- `#Makro`

## Clickbait Integrity Check

Jeder YouTube-Metadatensatz muss eine Pruefung enthalten:

```json
{
  "passed": true,
  "reason": "Der Titel ist zugespitzt, aber nicht irrefuehrend."
}
```

`passed` muss false sein, wenn:

- Titel eine sichere Zukunft behauptet,
- Titel eine Kauf-/Verkaufsempfehlung nahelegt,
- Thumbnail eine falsche Krise behauptet,
- Video-Inhalt die Hook nicht sauber einloest,
- Quellenlage zu schwach ist.

## Advisory Check

Die SEO Engine muss Anlageberatungs-Trigger erkennen.

Red-Flag-Woerter:

- kaufen
- verkaufen
- jetzt einsteigen
- garantierter Gewinn
- sichere Rendite
- kein Risiko
- All in
- reich werden

Wenn solche Begriffe vorkommen:

```json
{
  "advisory_check": {
    "flagged": true,
    "matched_keywords": ["kaufen"],
    "suggestions": ["Formuliere als Datenvergleich statt Handlungsempfehlung."]
  },
  "requires_review": true
}
```

## YouTube Shorts

Fuer Shorts sollen Titel besonders knapp sein, aber nicht irrefuehrend.

Gute Shorts-Titel:

- "Gold vs S&P 500 seit 2020"
- "Der Dollar-Check in 30 Sekunden"
- "Bitcoin gegen Aktien: der Verlauf"

Schwache Shorts-Titel:

- "Du musst das sehen!!!!"
- "Werde reich mit diesem Chart"
- "Alles bricht zusammen"

## Sprache

Default fuer deutschsprachigen Content:

```json
{
  "default_language": "de",
  "locale": "de-DE"
}
```

Spaeter koennen englische Varianten ueber `localizations` vorbereitet werden, aber nur wenn Inhalt und Quellen sauber uebersetzt wurden.

## Review-Pflicht

YouTube-Metadaten brauchen Review, wenn:

- `advisory_check.flagged == true`,
- `clickbait_integrity_check.passed == false`,
- Thumbnail besonders stark zugespitzt ist,
- politisch sensibles Thema beruehrt wird,
- Content Finanz-/Anlageentscheidungen nahelegt,
- Quellenmanifest fehlt.

Default bleibt fuer die Startphase:

```json
"requires_review": true
```
