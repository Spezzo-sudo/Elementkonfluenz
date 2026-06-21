# Imperium-Recherche — Spezifikation für neue Episoden

Diese Datei ist die vollständige Arbeitsanweisung für die Recherche **einer einzelnen**
Imperium-Episode (`imperium/data/imperium_<id>.yaml`). Sie ist so geschrieben, dass jeder —
ein Mensch oder eine KI mit Web-Zugriff, intern oder extern — sie ohne weiteren Kontext
befolgen kann und am Ende eine Datei abliefert, die `qa.py` ohne Nacharbeit besteht.

Hintergrund: für „welche Marken gehören zu Konzern X" gibt es keine API. Jede Zahl/Tatsache in
dieser Vertical wird von Hand recherchiert und belegt. Ein falscher Fakt über ein echtes
Unternehmen kostet mehr als eine verzögerte Episode — im Zweifel weglassen, nicht raten.

## 1. Output

Eine Datei `content-engine/brain/value_racer_brain/imperium/data/imperium_<topic_id>.yaml`,
die exakt dem Schema in `research.py` (`CompanyResearch`) entspricht. `<topic_id>` ist der
Slug aus dem trend-engine-Katalog (`trend-engine/value_racer_trend/catalog_imperium.py`), falls
dort schon vorhanden — sonst `imperium_<firmenname_lowercase>`.

Validierung nach dem Schreiben (Pflicht, nicht optional):

```bash
python -m value_racer_brain.imperium.cli build \
  --data value_racer_brain/imperium/data/imperium_<topic_id>.yaml \
  --out /tmp/<topic_id>_scene_plan.json
python -m value_racer_brain.imperium.cli research-status
```

Ergebnis muss sein: `hard_fail=False`, `sources_verified=True`. Wenn nicht — Datei korrigieren,
nicht die Validierung umgehen.

## 2. Feld-für-Feld-Schema

### Kopf

| Feld | Typ | Pflicht | Regel |
|---|---|---|---|
| `topic_id` | string | ja | s.o., muss eindeutig im `data/`-Verzeichnis sein |
| `sector` | string | ja | einer aus: `consumer_goods`, `automotive`, `tech`, `finance`, `pharma`, `luxury` — neuer Sektor nur, wenn keiner der bestehenden passt (Cooldown/Rotation im trend-engine läuft über dieses Feld) |
| `region` | string | ja | `EU`, `US`, `APAC` — analog, neue Region nur bei echtem Bedarf |

### `owner` (genau 1)

| Feld | Regel |
|---|---|
| `display_name` | kurzer Konsumentenname, z.B. "Toyota" (nicht die Rechtsform) |
| `legal_name` | vollständiger Firmenname laut Börsenregistrierung/Wikipedia-Infobox |
| `hq_city` | `"Stadt, Land"`, Land auf Deutsch (z.B. "Toyota City, Japan") |
| `founded_year` | Gründungsjahr, kein Börsengangsjahr |
| `ticker` | Primäres Ticker-Symbol inkl. Börsen-Suffix, exakt im yfinance-Format (z.B. `7203.T`, `NESN.SW`, `MC.PA`) — wird 1:1 für den Live-Endcard-Stockpull verwendet, ein falsches Suffix bricht die Episode erst beim Rendern |

### `brands` (Liste, **6–12 Einträge**, hart durch `qa.py: MIN_BRANDS/MAX_BRANDS`)

Pro Eintrag:

| Feld | Regel |
|---|---|
| `name` | Markenname wie öffentlich bekannt |
| `category` | kurzes deutsches Substantiv/Kompositum, z.B. "Schokolade", "Lkw & Busse" — wird direkt unter dem Namen angezeigt, max. ~30 Zeichen, sonst Overflow-Risiko in der Kartenwand |
| `acquired_year` | Jahr der Übernahme/Gründung als Tochter — **nicht** das Gründungsjahr der Marke selbst, falls diese vorher unabhängig existierte (z.B. KitKat existierte vor 1988, aber `acquired_year: 1988` ist das Jahr, in dem sie zu Nestlé kam) |
| `color_primary` / `color_text` | Hex, idealerweise die echte Markenfarbe/Wordmark-Farbe; `color_text` so wählen, dass der Kontrast auf `color_primary` lesbar ist (helles Text auf dunklem Primary oder umgekehrt) |
| `surprise_factor` | Ganzzahl 1–10. **1 = jeder kennt diese Marke + die Zugehörigkeit ist erwartbar/bekannt. 10 = überraschend, dass das zum gleichen Konzern gehört.** Treibt die Sortierung in der Kartenwand (aufsteigend: bekannt zuerst, Überraschung zuletzt) — das ist der eigentliche Hook des Formats, also bewusst kalibrieren, nicht zufällig vergeben |
| `source_url` | Pflicht, siehe Abschnitt 4 |
| `source_date` | Pflicht, ISO-Datum, siehe Abschnitt 4 |

**Auswahlkriterium „gehört das wirklich dazu?" (Abschnitt 3 lesen, bevor Kandidaten gesammelt werden).**

Wenn der Konzern mehr als 12 plausible Marken hat: die 12 mit der größten Bekanntheits-/
Überraschungs-Spannweite wählen, nicht die 12 zuerst gefundenen. Wenn weniger als 6 echte
(siehe Abschnitt 3) Marken auffindbar sind: Konzern ist evtl. kein guter Kandidat für dieses
Format — Plan-Inhaber informieren statt künstlich aufzufüllen.

### `facts` (Liste, **≥3 Einträge**, hart durch `qa.py: MIN_FACTS`)

Pro Eintrag: `label`, `value` (float), `unit`, `as_of_year`, `description`, `source_url`,
`source_date`.

Empfohlene Standard-Facts (nicht zwingend, aber bewährt — bisher in jeder Episode verwendet):

1. **UMSATZ** — Konzernumsatz letztes abgeschlossenes Geschäftsjahr. `unit` ist normalerweise
   `"Mrd. <Währung>"`; bei sehr großen Zahlen (>~1000 Mrd. in der lokalen Währung, z.B.
   japanische Yen) `"Bio. <Währung>"` (10^12) verwenden, damit `value` einstellig/zweistellig
   bleibt statt eine 5-stellige Zahl zu zeigen (siehe Toyota: `45.1 Bio. JPY` statt `45095 Mrd.
   JPY`).
2. **MITARBEITER** — Beschäftigte weltweit, konsolidiert. `unit: "Mitarbeiter"`, `value` als
   Ganzzahl (z.B. `380793`).
3. Ein dritter, konzern-spezifischer Fact, der etwas Konkretes über das Geschäft zeigt
   (Beispiele aus bisherigen Episoden: `PRAESENZ` — Länder mit Geschäftstätigkeit;
   `VERKAUFT` — verkaufte Einheiten/Fahrzeuge; `GESCHAEFTE` — Anzahl eigener Boutiquen/Filialen;
   `ANDROID` — aktive Geräte). Wähle die Kennzahl, die für diesen Konzern am meisten
   Größenordnung vermittelt.

`description` ist ein kurzer deutscher Satz, der den Fact einordnet (z.B. "Konzernumsatz
Geschäftsjahr 2024 (zum 31. März)" — Geschäftsjahresende nennen, falls abweichend vom
Kalenderjahr).

### `scale_comparison` (genau 1, **≥3 Zeilen**, hart durch `qa.py: MIN_SCALE_ROWS`)

| Feld | Regel |
|---|---|
| `headline` | Deutscher Satz der Form `"Mehr wert als X"` oder `"Mehr wert als X und Y zusammen"`. **Vor dem Schreiben rechnen:** `rows[0].value` muss strikt größer sein als die Summe aller in der Headline genannten Vergleichsfirmen — sonst die Headline auf weniger Firmen oder eine andere Formulierung reduzieren. Es gibt dafür keinen Code-Check; das ist allein Recherche-Disziplin. |
| `unit` | einheitliche Einheit für alle `rows`, typischerweise `"Mrd. USD"` (Marktkapitalisierung), damit die Werte direkt vergleichbar sind — keine Mischung von Lokalwährungen |
| `rows` | `rows[0]` ist immer der Owner-Konzern selbst (wird vom Builder automatisch als `hero: true` markiert — in der YAML einfach als normale erste Zeile eintragen), danach ≥2 Vergleichsfirmen, jede mit eigenem `source_url`/`source_date` |

Quelle für Marktkapitalisierung: einheitlich von **derselben** Quelle für alle Zeilen ziehen
(z.B. alle von `companiesmarketcap.com` am selben Tag), nicht eine Zeile von dort und eine
andere von einer Finanznachrichtenseite — sonst sind Stichtage/Methodik inkonsistent und der
Vergleich wird angreifbar. Wenn eine Quelle die Werte direkt in USD ausweist, diese verwenden
statt selbst aus einer Lokalwährung umzurechnen (vermeidet eigene Wechselkurs-Fehler).

### Fußzeile

| Feld | Regel |
|---|---|
| `researched_at` | Datum der Recherche-Session (ISO) |
| `verified` | `true`, sobald alle Quellen tatsächlich geöffnet/geprüft wurden (nicht nur aus einer Such-Vorschau übernommen) |
| `verified_at` | i.d.R. identisch mit `researched_at` |
| `verify_interval_days` | `365`, außer eine Episode hat absehbar volatile Fakten (z.B. ein laufender, unbestätigter Verkaufsprozess einer Tochtermarke) — dann kürzer ansetzen oder die Marke vorerst ganz weglassen (siehe Abschnitt 3, LVMH/Fenty-Beispiel) |

## 3. Was zählt als „gehört dazu" — Ownership-Genauigkeit

Das Format heißt „Wem gehört das?" — die implizite Behauptung jeder Karte ist **vollständige
oder mehrheitliche Kontrolle**, nicht „wird in den Medien mit dem Konzern assoziiert". Vor
jeder Brand-Aufnahme konkret prüfen, in dieser Reihenfolge:

1. **Beteiligungshöhe.** Anteil <50 % → nicht aufnehmen, auch wenn die Beteiligung groß und
   bekannt ist (Beispiel: Toyota hält ~20 % an Subaru — ausgeschlossen).
2. **Equity-Method-Affiliate.** Wird die Beteiligung bilanziell nach der Equity-Methode
   geführt (typisch ab ~20–50 % ohne Kontrollmehrheit), ist es eine Beteiligung, keine
   Tochtergesellschaft (Beispiel: Toyota Tsusho, 23,5 % — ausgeschlossen).
3. **Joint Venture.** Auch ein 50/50- oder Minderheits-JV mit einem unabhängigen Partner ist
   keine alleinige Tochter, selbst wenn der Konzername im Produktnamen steckt (Beispiel: KINTO,
   JV mit Sumitomo Mitsui Auto Service — ausgeschlossen).
4. **Richtungsfehler in Konzernstrukturen (Keiretsu/Kreuzbeteiligungen).** Bei japanischen und
   manchen koreanischen Konzernen sind Beteiligungsrichtungen nicht immer „Mutter → Tochter" —
   prüfen, ob das vermeintliche „Tochterunternehmen" historisch/strukturell eigentlich
   *oberhalb* des Hauptkonzerns sitzt (Beispiel: Toyota Industries sitzt upstream von Toyota
   Motor in der Kreuzbeteiligungsstruktur — ausgeschlossen, sonst wäre die Karte sachlich
   falsch gepolt).
5. **Schwebende Transaktionen.** Ist eine Übernahme/ein Verkauf gemeldet, aber noch nicht
   abgeschlossen (Closing ausstehend, regulatorische Freigabe offen), entweder ganz weglassen
   oder nur aufnehmen, wenn der *aktuelle* Stand (vor der Transaktion) eindeutig ist — und dann
   `verify_interval_days` kürzer setzen, damit die Episode nicht über die Transaktion hinweg
   stillschweigend falsch wird (Beispiel: LVMH/Fenty-Beauty-Verkaufsgerüchte — Fenty bewusst
   nicht aufgenommen, Benefit Cosmetics mit stabiler Eigentümerschaft seit 1999 stattdessen
   verwendet).

Im Zweifel: Quelle explizit nach „wholly owned subsidiary" / "majority-owned" / Beteiligungsquote
durchsuchen, nicht nur nach „gehört zu". Eine Marke lieber weglassen als falsch zuordnen.

## 4. Quellenregeln

- **Jede** Zahl/Jahresangabe in `brands`, `facts`, `scale_comparison.rows` braucht ein eigenes
  `source_url` + `source_date` — `qa.py` prüft das maschinell (`_all_sourced`), eine fehlende
  URL lässt die ganze Episode durchfallen.
- `source_date` ist das Datum, an dem die Quelle *für diese Recherche-Session* geöffnet/geprüft
  wurde — nicht das Publikationsdatum des Artikels (das gehört, falls relevant, in
  `description`).
- Bevorzugte Quellentypen, in dieser Reihenfolge: (1) offizielle Geschäftsberichte/
  Pressemitteilungen des Konzerns oder SEC/Börsenfilings, (2) etablierte Marktdaten-Aggregatoren
  für Marktkapitalisierung (`companiesmarketcap.com`) bzw. Mitarbeiterzahlen
  (`macrotrends.net`, `statista.com`), (3) Wikipedia-Artikel zur Marke/zum Konzern (gut für
  Übernahmejahr, Markengeschichte), (4) seriöser Finanz-/Wirtschaftsjournalismus (Reuters,
  Bloomberg, CNBC, Handelsblatt) für aktuelle Ereignisse. SEO-Farmen, unbelegte
  Listicle-Seiten oder KI-generierte Zusammenfassungsseiten sind keine zulässige Quelle.
- Eine URL pro Quelle reicht; bei strittigen Zahlen (z.B. abweichende Mitarbeiterangaben
  zwischen zwei Quellen) die offiziellere/aktuellere wählen und nicht beide referenzieren.

## 5. Ablauf für eine neue Episode (Checkliste)

1. Kandidat aus `trend-engine/value_racer_trend/catalog_imperium.py` nehmen (Topic-ID, Ticker,
   Sektor, Region sind dort schon festgelegt) — oder, falls ein neuer Konzern gewünscht ist,
   dort zuerst einen `ImperiumTopic`-Eintrag ergänzen, bevor die YAML geschrieben wird.
2. Eigentümerstruktur recherchieren (Abschnitt 3) — Liste *echter* Töchter/Marken erstellen,
   bevor Details (Farben, Jahre) recherchiert werden. Bei <6 echten Treffern: Kandidat
   zurückstellen.
3. 6–12 Marken final auswählen, `surprise_factor` kalibrieren (1 = bekannt/erwartbar, 10 =
   überraschend), Farben/Kategorie/Jahr + Quelle je Marke eintragen.
4. 3 Facts recherchieren (Umsatz, Mitarbeiter, ein konzernspezifischer dritter Fact), inkl.
   Einheit-Entscheidung (Mrd. vs. Bio.).
5. Skalenvergleich: Marktkapitalisierung des Konzerns + ≥2 Wettbewerber von derselben
   Quelle/demselben Stichtag ziehen, Headline-Mathematik von Hand prüfen.
6. YAML nach diesem Schema schreiben, Kopf-Kommentar mit Recherche-Datum + ggf. bewusst
   ausgeschlossenen Kandidaten (wie in den bisherigen Episoden) ergänzen.
7. `build` + `research-status` laufen lassen (Abschnitt 1), grün bekommen.
8. Optional, aber empfohlen vor dem ersten Posting: Render aller sieben Phasen per
   `remotion still` visuell prüfen (Kartenwand-Overflow bei langen Namen, Headline-Umbruch,
   Balkenbreiten bei sehr großen/kleinen Werten).
9. Gegen den Distribution-Gate-CLI mit einer leeren Test-DB prüfen, dass eine neue Episode
   korrekt `pending_review` (`first_contact_requires_manual_review`) auslöst.

## 6. Offene Kandidaten im bestehenden Katalog

Aus `catalog_imperium.py` bereits angelegt, aber noch **nicht** recherchiert (Stand
2026-06-21): `imperium_mercedes` (automotive/EU), `imperium_jpmorgan` (finance/US),
`imperium_jnj` (pharma/US), `imperium_samsung` (tech/APAC). Das sind die naheliegenden nächsten
Ziele, falls/wenn die Recherche fortgesetzt wird — sie decken die noch nicht bedienten Sektoren
`finance`/`pharma` und die Region APAC zusätzlich zu Toyota ab.
