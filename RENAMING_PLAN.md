# Renaming Plan: Elementkonfluenz -> ValueRacer

Stand: 2026-06-21

Dieses Dokument legt fest, wie der alte Arbeitsname `Elementkonfluenz` sicher durch den neuen Produktnamen `ValueRacer` ersetzt wird.

## Ziel

Der neue Name lautet:

```text
ValueRacer
```

Er soll gelten fuer:

- Produktkommunikation
- README und Dokumentation
- VPS-Zielverzeichnis
- Hermes-Konfiguration
- neue Module und neue Environment-Variablen

## Warum schrittweise?

Ein Big-Bang-Rename kann Importpfade, CI, offene PRs, VPS-Skripte und Hermes-Jobs brechen. Deshalb wird umbenannt in kontrollierten Phasen.

## Phase 1: Produktidentitaet

Status: dieses PR.

- README auf `ValueRacer` setzen.
- Projektstatus auf `ValueRacer` setzen.
- Hermes Contract auf `ValueRacer` setzen.
- Migration Plan auf `/srv/valueracer` setzen.
- Alte Namen als Legacy markieren, nicht als neuen Standard verwenden.

## Phase 2: Offene PRs pruefen

Offene PRs, die noch `Elementkonfluenz` verwenden, duerfen nicht blind gemerged werden.

Zu pruefen:

- PR fuer Hermes Dry-Run-Orchestrator
- PR fuer YouTube Publishing und SEO Contract
- eventuelle doppelte/alte Roadmap-PRs

Regel:

```text
kein Merge, wenn neue Dokumentation wieder den alten Produktnamen als Standard einfuehrt
```

## Phase 3: GitHub-Repository umbenennen

Der Repository-Name selbst kann nicht durch diese Datei geaendert werden. Er muss in GitHub manuell oder mit GitHub-CLI/API umbenannt werden.

Ziel:

```text
Spezzo-sudo/ValueRacer
```

Vorher pruefen:

- offene PRs
- lokale Clones
- Claude Code / Hermes Remote URLs
- GitHub Actions
- externe Webhooks

Nach GitHub-Rename:

```bash
git remote set-url origin git@github.com:Spezzo-sudo/ValueRacer.git
```

oder per HTTPS:

```bash
git remote set-url origin https://github.com/Spezzo-sudo/ValueRacer.git
```

## Phase 4: VPS-Verzeichnis umstellen

Zielpfad:

```text
/srv/valueracer
```

Sicherer Ablauf:

```text
1. bestehenden Pfad inventarisieren
2. Backup erstellen
3. /srv/valueracer parallel anlegen
4. neues Repo dort auschecken
5. vorhandene Hermes/.env Secrets nur lesen, nicht kopieren ins Repo
6. Dry-Run testen
7. optional Legacy-Symlink setzen
8. alten Pfad erst spaeter entfernen
```

Optionaler Legacy-Symlink:

```text
/srv/elementkonfluenz -> /srv/valueracer
```

Nur setzen, wenn Hermes oder alte Cronjobs den alten Pfad noch erwarten.

## Phase 5: Environment-Variablen

Neue Variablen:

```text
VALUERACER_ENV
VALUERACER_RUNS_DIR
VALUERACER_LOGS_DIR
VALUERACER_DRY_RUN
```

Legacy-Variablen duerfen uebergangsweise gelesen werden:

```text
ELEMENTKONFLUENZ_ENV
ELEMENTKONFLUENZ_RUNS_DIR
ELEMENTKONFLUENZ_LOGS_DIR
ELEMENTKONFLUENZ_DRY_RUN
```

Regel:

```text
lesen ja, automatisch veraendern nein
```

## Phase 6: Python-Paketnamen

Aktuell existiert noch:

```text
elementkonfluenz_brain
```

Spaetere Zieloptionen:

1. Paket direkt auf `valueracer_brain` umbenennen.
2. `valueracer_brain` neu einfuehren und `elementkonfluenz_brain` als Kompatibilitaets-Alias behalten.

Empfohlen:

```text
erst Alias, dann Umstellung, dann Legacy entfernen
```

Damit brechen CI, Hermes und Claude Code nicht sofort.

## Nicht-Ziele dieses PRs

Dieses PR benennt nicht sofort um:

- GitHub-Repository selbst
- alle Python-Packages
- alle historischen Branches
- alle offenen PR-Dateien

Diese Schritte brauchen eigene kleine PRs oder manuelle GitHub-/VPS-Aktionen.

## Akzeptanzkriterien

- Neue Dokumentation nennt `ValueRacer` als Produktnamen.
- VPS-Zielpfad ist `/srv/valueracer`.
- Alte Namen sind als Legacy markiert.
- Keine Secrets werden bewegt.
- Keine Run-Daten werden geloescht.
- Offene PRs werden vor Merge auf alte Namensreste geprueft.
