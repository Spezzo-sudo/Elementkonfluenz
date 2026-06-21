# Content Standard

Stand: 2026-06-21

Elementkonfluenz soll ein Social-Content-Label fuer kurze, visuell starke Wirtschafts- und Finanzvideos werden. Der Content darf neugierig machen und aufmerksamkeitsstark verpackt sein. Die rote Linie ist aber: Der Inhalt bleibt wahrheitsgemaess, datenbasiert, einordnend und frei von Anlageberatung.

## Positionierung

Wir machen keine Trading-Signale, keine Guru-Versprechen und keine Panikvideos. Wir erklaeren wirtschaftliche und finanzielle Entwicklungen so, dass Menschen Zusammenhaenge schneller verstehen.

Ziel:

```text
starke Hook + ehrliche Daten + verstaendliche Einordnung
```

Nicht-Ziel:

```text
Kaufempfehlungen, Crash-Prophezeiungen, garantierte Gewinne, manipulatives Angst-Marketing
```

## Ethical Clickbait

Titel und Thumbnail duerfen scroll-stoppend sein. Sie duerfen Spannung erzeugen, Kontraste zeigen und neugierig machen. Sie duerfen aber keine falsche Aussage, falsche Sicherheit oder unbelegte Prognose behaupten.

Erlaubt:

- "Gold gegen Tech: Wer hat wirklich geliefert?"
- "Der Dollar verliert Macht? Das zeigen die Daten"
- "Warum alle wieder ueber Rohstoffe reden"
- "Bitcoin vs. S&P 500: Der Vergleich ueberrascht"
- "Diese 3 Maerkte erzaehlen gerade dieselbe Geschichte"

Nicht erlaubt:

- "Kauf das jetzt"
- "Dieser Coin macht dich reich"
- "Der Crash kommt sicher morgen"
- "Banken verschweigen dir diese Wahrheit"
- "100% sichere Strategie"
- "Garantierter Gewinn"

## Inhaltliche rote Linie

Jedes Video muss:

1. klar zwischen Daten, Einordnung und Meinung trennen,
2. keine Kauf- oder Verkaufsempfehlung enthalten,
3. keine garantierten Ergebnisse versprechen,
4. Zeitraeume sichtbar oder im Script eindeutig benennen,
5. Unsicherheiten oder Datenluecken markieren,
6. Datenquellen intern im Run-Ordner speichern,
7. vereinfachen, aber nicht verfaelschen,
8. bei finanznahen Aussagen besonders vorsichtig formulieren.

## Tonalitaet

Gewuenscht:

- kurz
- klar
- visuell
- neugierig
- serioes
- zugespitzt, aber fair
- informativ statt belehrend

Nicht gewuenscht:

- Finanzguru-Ton
- Insider-Verschwoerungs-Ton
- Panikmache
- Hoehnisches Framing
- politische Propaganda
- falsche Eindeutigkeit bei komplexen Daten

## Quellenstandard

Videos muessen nicht selbst als wissenschaftliche Primaerquelle dienen. Intern muss aber nachvollziehbar sein, wo Daten und Aussagen herkommen.

Jeder Run soll ein `sources.json` enthalten mit:

- Datenquelle
- Abrufzeitpunkt
- verwendeter Zeitraum
- betroffene Ticker/Indikatoren/Themen
- optionaler Hinweis auf bekannte Einschraenkungen

Wenn Daten automatisiert geladen werden, soll die Pipeline so viel Herkunft wie moeglich speichern.

## Finanz- und Anlageberatungsgrenze

Verbotene Formulierungen:

- "kaufen"
- "verkaufen"
- "jetzt einsteigen"
- "garantiert"
- "sicherer Gewinn"
- "kein Risiko"
- "muss man haben"
- "All in"

Besser:

- "historisch betrachtet"
- "in diesem Zeitraum"
- "die Daten zeigen"
- "ein moegliches Risiko ist"
- "das ist keine Prognose"
- "dieser Vergleich zeigt nur einen Ausschnitt"

## Script-Struktur

Empfohlene Kurzvideo-Struktur:

1. Hook: starke, aber nicht falsche These oder Frage.
2. Kontext: Zeitraum und Datenbasis nennen.
3. Vergleich: visuell zeigen, was passiert ist.
4. Einordnung: Warum koennte das relevant sein?
5. Caveat: Was zeigt der Vergleich nicht?
6. Abschluss: neutrale Erkenntnis statt Handlungsempfehlung.

Beispiel:

```text
Hook: Gold gegen Tech: Der Vergleich ueberrascht.
Kontext: Wir vergleichen die Entwicklung seit 2020.
Daten: Gold, Nasdaq und S&P 500 im selben Zeitraum.
Einordnung: Je nach Zeitraum sieht die Rangliste anders aus.
Caveat: Das ist keine Prognose fuer die Zukunft.
Abschluss: Der Zeitraum entscheidet, welche Geschichte die Daten erzaehlen.
```

## Thumbnail-/Titel-Regel

Ein Titel darf zugespitzt sein, wenn das Video die Zuspitzung ehrlich aufloest.

Erlaubt:

```text
"Der Dollar verliert Macht?"
```

Nur wenn das Video danach sauber erklaert:

- welche Daten betrachtet werden,
- ob es um Wechselkurs, Reservewaehrung, Kaufkraft oder Handel geht,
- welche Einschraenkungen gelten.

Nicht erlaubt:

```text
"Der Dollar ist tot"
```

wenn das Video diese absolute Aussage nicht belegen kann.

## Review-Pflicht

Ein Video benoetigt manuelle Review, wenn:

- die Hook sehr stark zugespitzt ist,
- ein politisch sensibles Thema beruehrt wird,
- Datenquellen unvollstaendig sind,
- die Advisory-Pruefung anschlaegt,
- `qa.hard_fail == true`,
- die Distribution erstmals fuer eine Plattform aktiviert wird.

## Label-Versprechen

Elementkonfluenz steht fuer:

```text
Aufmerksamkeitsstarke Wirtschafts- und Finanzvideos mit ehrlicher, datenbasierter Einordnung.
```

Das Label wird nicht ueber perfekte Vorhersagen verdient, sondern ueber verlaessliche Haltung: nichts erfinden, nichts versprechen, nichts verstecken.
