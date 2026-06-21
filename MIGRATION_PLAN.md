# Migration Plan: VPS / Hermes

Stand: 2026-06-21

Dieses Dokument definiert, wie ein bestehendes VPS-Projekt spaeter vorsichtig durch **ValueRacer** ersetzt oder erweitert wird, ohne Datenverlust, ohne Secret-Leaks und ohne unkontrolliertes Auto-Posting.

## Naming

- Produktname: `ValueRacer`
- Empfohlener VPS-Zielpfad: `/srv/valueracer`
- Alter Arbeitsname: `Elementkonfluenz`

Der alte Name kann noch in historischen Commits, offenen PRs oder internen Paketnamen vorkommen. Das GitHub-Repository selbst muss separat in GitHub umbenannt werden, wenn der Repository-Name ebenfalls `ValueRacer` werden soll.

## Grundsatz

Keine direkte Ersetzung ohne Inventarisierung, Backup, Parallelbetrieb und Rollback-Pfad.

```text
backup first -> deploy parallel -> dry-run -> compare -> review -> switch gradually
```

## Was nicht passieren darf

- Kein Loeschen bestehender Produktionsdaten.
- Kein Ueberschreiben alter Runs.
- Kein Ueberschreiben von API-Keys oder `.env`-Dateien.
- Kein automatisches Posten, bevor Dry-Runs stabil sind.
- Kein Entfernen des alten Projekts, bevor Rollback getestet wurde.
- Keine Secrets im Git-Repo.
- Kein blindes Umbenennen produktiver VPS-Pfade ohne Symlink-/Rollback-Plan.

## Phase 1: Inventarisierung

Vor jeder Migration wird der Ist-Zustand des VPS dokumentiert.

Zu erfassen:

- Projektpfad des bestehenden Systems
- aktive Services/Systemd-Timer/Cronjobs
- verwendete Python-/Node-Versionen
- `.env`-/Secret-Dateien, ohne Inhalte ins Repo zu kopieren
- Datenordner
- Output-/Run-Ordner
- Log-Ordner
- genutzte API-Integrationen
- aktive Posting-Ziele
- vorhandene Hermes-Umgebungsvariablen

Ergebnisdatei auf dem VPS, nicht zwingend im Git-Repo:

```text
migration_inventory_<date>.md
```

## Phase 2: Backup

Vor Veraenderungen:

- Vollstaendiges Projektverzeichnis sichern.
- Daten-/Run-Ordner sichern.
- `.env` und Secret-Konfiguration separat sichern.
- Optional VPS-Snapshot erstellen, falls Provider das erlaubt.

Empfohlene Backup-Struktur:

```text
/backups/valueracer-migration/<date>/
├── project.tar.gz
├── data.tar.gz
├── runs.tar.gz
├── env-files.tar.gz
└── inventory.md
```

## Phase 3: Parallel-Deployment

ValueRacer wird zuerst parallel installiert, nicht ueber das alte Projekt gelegt.

Beispiel:

```text
/srv/old-content-project/        # bestehendes System, bleibt unangetastet
/srv/valueracer/                 # neues System
/srv/valueracer/runs/            # neue Runs
/srv/valueracer/logs/            # neue Logs
```

Falls Hermes bereits Pfade unter altem Namen erwartet, wird zuerst ein Symlink oder eine explizite ENV-Umstellung geplant, nicht spontan geloescht:

```text
/srv/elementkonfluenz -> /srv/valueracer   # nur falls noetig und bewusst gesetzt
```

## Phase 4: Dry-Run

Hermes startet ValueRacer zuerst nur im Dry-Run.

Dry-Run darf:

- Thema auswaehlen
- ScenePlan erzeugen
- Video rendern
- Metadaten erzeugen
- Posting-Plan vorbereiten
- Logs und QA schreiben

Dry-Run darf nicht:

- Plattform-APIs fuer echtes Posting nutzen
- alte Daten veraendern
- alte Jobs stoppen
- Secrets rotieren

## Phase 5: Vergleich

Dry-Run-Ausgaben werden manuell geprueft:

- Ist der Content wahrheitsgemaess?
- Sind Quellen/Datengrundlagen nachvollziehbar?
- Ist `qa.hard_fail` false?
- Ist die Video-Datei technisch brauchbar?
- Sind Titel/Thumbnails hooky, aber nicht irrefuehrend?
- Gibt es versehentliche Anlageberatung?

## Phase 6: Staging-Betrieb

Wenn Dry-Runs stabil sind, kann Hermes regelmaessig Staging-Jobs erzeugen.

Empfohlen:

- 3 bis 7 Tage Staging ohne Posting
- alle Outputs speichern
- Fehlerliste fuehren
- keine Produktionsjobs loeschen

## Phase 7: Kontrollierte Umschaltung

Erst wenn Staging stabil ist:

- eine Plattform auswaehlen
- manuelle Freigabe behalten
- niedrige Frequenz starten
- Logs eng beobachten
- Rollback-Pfad aktiv halten

## Phase 8: Rollback

Rollback muss einfach sein:

- alten Service wieder aktivieren
- neuen Service stoppen
- neue Cronjobs/Systemd-Timer deaktivieren
- keine Daten loeschen

Rollback-Checkliste:

```text
[ ] neue Scheduler deaktiviert
[ ] alte Scheduler aktiviert
[ ] neue Posting-Keys nicht veraendert
[ ] alte Daten vorhanden
[ ] Logs gesichert
[ ] Fehlgrund dokumentiert
```

## Hermes-Sicherheitsregeln

Hermes darf nur in seinem konfigurierten Arbeitsordner schreiben:

```text
VALUERACER_RUNS_DIR=/srv/valueracer/runs
VALUERACER_LOGS_DIR=/srv/valueracer/logs
```

Abwaertskompatible Legacy-Variablen duerfen fuer eine Uebergangszeit gelesen werden, aber neue Deployments sollen die `VALUERACER_*` Namen verwenden:

```text
ELEMENTKONFLUENZ_RUNS_DIR=/srv/elementkonfluenz/runs
ELEMENTKONFLUENZ_LOGS_DIR=/srv/elementkonfluenz/logs
```

Hermes darf keine Schreiboperationen ausserhalb dieser Pfade durchfuehren, ausser sie sind in einer expliziten Migration freigegeben.

## Produktionsfreigabe

Auto-Posting ist erst erlaubt, wenn alle Punkte abgehakt sind:

```text
[ ] Backups erstellt und wiederherstellbar
[ ] Parallel-Deployment laeuft
[ ] Dry-Runs mehrfach erfolgreich
[ ] Content-Review bestanden
[ ] API-Zugaenge dokumentiert
[ ] Rollback getestet
[ ] Nutzer hat Auto-Posting explizit freigegeben
```

Bis dahin gilt:

```text
VALUERACER_DRY_RUN=true
```

Legacy fuer Uebergang:

```text
ELEMENTKONFLUENZ_DRY_RUN=true
```
