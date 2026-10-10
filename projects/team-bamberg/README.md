# Team Bamberg – WordPress & Elementor

Eigenständige Neugestaltung von https://team-bamberg.de/ in CSU-Farben. Das Gaustadt-Projekt bleibt als eigenes Projekt erhalten.

**Installierbares Theme:** `releases/team-bamberg-elementor.zip`.
**Einfache Anleitung:** [ANLEITUNG.md](ANLEITUNG.md).

## Gestaltung und Inhalte

- Version 1.1: großes Bamberg-Foto über die volle Breite, dunkle Bildüberlagerung, warme Sand- und Cremetöne sowie echte Originalporträts direkt auf der Startseite.
- Bildgestützte Einstiege und ergänzte Textentwürfe auf allen Unterseiten, persönliche Profilkarten und neu gestaltete Kontaktseite mit separaten Kontaktwegen und Formular.
- Expliziter Update-Knopf für vorhandene Installationen: ersetzt die importierten Elementor-Vorlagen nach Sicherung, erhält Termine, Empfänger und Menü, schützt fremde Seiten und erlaubt die Wiederherstellung der bisherigen Inhalte. Ein normaler Import überschreibt weiterhin keine Bearbeitungen.
- Version 1.2: acht eigenständige Stadtteilseiten mit individuellen, quellenbasierten Einstiegen, Stadtteilbildern, vollständiger Originalvorstellung und identifizierbaren Kontaktkarten. Ortsverbandsübersicht verlinkt alle acht internen Seiten.
- Local-Vorschau direkt vor der Seitentabelle; Update bietet eine ausdrücklich beschriftete Checkbox zum Freigeben der Projektentwürfe und Aktivieren der Startseite. Normale Importe bleiben als Entwürfe erhalten, öffentliche Installationen bekommen keine Local-Freigabe.
- Offizielle CSU-Farben anhand von `https://www.csu.de/assets/css/csu.min.css`: Blau `#0080c8`, Dunkelblau `#112b4b`, Hellblau `#e5f2f8`, Grün `#a2c516`.
- 45 öffentliche Originalseiten aus Navigation und Seiten-Sitemap, darunter acht Ortsverbände, Kreisverband, Fachgruppen, ASP, Mandatsträger, Fraktion, elf Personenprofile, Mitgliedschaft, Spenden, Kontakt und Rechtstexte.
- Zusätzliches Archiv mit bestehenden Transparenzangaben zu politischen Anzeigen.
- 85 ausgewählte Originalbilddateien und 66 ursprüngliche PDF-Dateien als lokale WordPress-Medien. Größenvarianten und mehrfach verwendete Bilder werden passend ausgewählt; die übernommenen Dateien bleiben unverändert.
- Native Elementor-Free-Widgets für Texte, Überschriften, Bilder und Buttons. Eigene Widgets für Navigation, Termine, Anfragehilfe und Archivsuche. Kein Elementor Pro und keine kompletten Seiten als HTML-Widgets.
- Antragsarchiv mit Suchbegriff und Jahresfilter, zusätzliche WordPress-Suche.
- Import legt Seiten als Entwürfe an, läuft in kleinen Schritten und kann fortgesetzt werden. Wiederholen überschreibt keine bestehenden Bearbeitungen.
- Kopf- und Fußbereich zentral in Elementor bearbeiten. Kommende Termine werden zur Laufzeit von der Termineseite auf die Startseite übernommen.

Die ergänzten Einstiegstexte sind redaktionelle Entwürfe für die Gestaltungsvorschau. Sie behaupten keine unbekannten aktuellen Ämter, Veranstaltungen oder politischen Beschlüsse.

Die Quellen wurden am **10.10.2026** erfasst. Aktuelle Personen und Funktionen werden nicht allein durch die neue Gestaltung bestätigt. Die alte Datenschutzerklärung von Mai 2018, unvollständige IBAN, teilweise verschleierte E-Mail-Adressen, ein Termin ohne Jahr und zwei nicht erreichbare Originalbilder sind ausdrücklich dokumentiert. Das Antrags- und Anzeigenarchiv behält seine ursprünglichen Daten. Facebook, YouTube und externe Dokumente werden verlinkt. Die Anfragehilfe bereitet Text vor und sendet keine Nachrichten automatisch.

Die Original-Sitemap enthielt außerdem 267 Beitragsadressen mit vielen fachfremden Themen mit zahlreichen Casino-Themen. Zwei öffentliche Beispiele wurden inhaltlich geprüft. Diese Beiträge wurden nicht importiert. Der bisherige Betreiber sollte die Ursache untersuchen; eine Kompromittierung ist damit noch nicht abschließend diagnostiziert. Details der Erfassung stehen in [QUELLEN.json](QUELLEN.json).

## Entwickeln und prüfen

Eigene WordPress-Testinstallation starten:

```bash
cd /workspace/Website_BlaskapelleGaustadt
python3 projects/team-bamberg/tools/start-test-environment.py
```

Der Helfer verwendet verifizierte offizielle Docker-Images und Elementor Free 4.3.0 mit SHA-256-Prüfung. Die Testcontainer `team-bamberg-test-wp` und `team-bamberg-test-db` sind vom Gaustadt-Testprojekt getrennt. Sie verwenden Port 8089 und private Testdateien unter `/workspace/team-bamberg-wp-test`. Passwörter, Cookies, Datenbankdateien und WordPress-Core sind nicht im Theme. Bei einer frischen Datenbank den normalen Import im WordPress-Backend ausführen. Keine bestehenden fremden Container oder Benutzerinhalte überschreiben.

Geprüft mit WordPress 7.1.3, Elementor Free 4.3.0 und PHP 8.3.35: echter Backendimport und Fortsetzung, Schutz vorhandener Elementor-Daten, echte Bearbeitung/Veröffentlichung einer Überschrift, Startseitenaktivierung, alle 45 Seiten bei 1440/768/390/320 Pixeln, Archivfilter, lokales Original-PDF, WordPress-Suche, Formularvalidierung und Kopieren, mobiles Menü und Escape, geladene Originalbilder, eigene 404 und deaktivierte Formularfelder ohne JavaScript. Version 1.1 zusätzlich geprüft: echter Update-Knopf, 47 gesicherte Elementor-Dokumente, exakte Wiederherstellung, Schutz vor erneutem Überschreiben der Sicherung, Erhalt der Funktionswidget-Einstellungen und fremder Seiten. Token-Auflösung verwendet einen pro Request vorbereiteten URL-Index, damit das gesamte Update innerhalb der PHP-Laufzeitgrenze fertig wird. Keine Fehler im Frontend-JavaScript. team-bamberg.de wurde nicht verändert.

Originalquellen neu erfassen:

```bash
python3 projects/team-bamberg/tools/collect-source.py --output /workspace/team-bamberg-source-new
```

Dabei öffentliche Seiten-Sitemap und verlinkte Seiten erfassen; Posts getrennt inventarisieren und inhaltlich prüfen. Keine ungeprüften Fremdartikel übernehmen. Erfassungsfehler, externe Medien und Grenzen stehen in `inventory.json`; ein unvollständiger Abruf liefert Exit 1. Originaldateien liegen außerhalb des Git-Checkouts. Der Sammler führt keine Seitenskripte oder Formulare aus.

Vorlagen nur für beabsichtigte Änderungen neu erzeugen:

```bash
python3 -m pip install --target /workspace/team-bamberg-python beautifulsoup4==4.14.3 soupsieve==3.0 typing-extensions==4.16.0
PYTHONPATH=/workspace/team-bamberg-python python3 projects/team-bamberg/tools/build-theme.py --source /workspace/team-bamberg-source
python3 projects/team-bamberg/tools/package-theme.py
```

Der Build schreibt Vorlagendateien; im normalen Cloud-Setup nur Paketprüfung und Testumgebung starten. Der ZIP-Helfer prüft die SHA-256-Werte der Originalmedien und enthält ausschließlich das Theme. Neue Cloud-Wiederherstellung und der tatsächliche Vereinsserver wurden nicht unabhängig getestet.

Aktuelle Prüfungen und Grenzen stehen in [PRUEFBERICHT.md](PRUEFBERICHT.md).
