# Entwicklung und Tests

Für die Vereinsmitglieder gilt `ANLEITUNG.md`. Die folgenden Schritte sind für technische Arbeit am Paket.

- `gaustadt-elementor/`: installierbares WordPress-Theme mit Starterimport, Elementor-Layouts und drei Elementor-Free-Widgets.
- `tools/build-templates.py`: erzeugt acht Seiten und zwei gemeinsame Bereiche aus nativen Elementor-Containern und Widgets. Keine seitenfüllenden HTML-Widgets, keine Elementor-Pro-Abhängigkeit.
- `tools/package-theme.py`: erzeugt `releases/gaustadt-elementor.zip` mit genau einer Theme-Wurzel und WordPress-geeigneten Dateirechten.
- `tools/start-test-environment.py`: lokale WordPress-/MariaDB-Testumgebung über Docker auf Port 8088. Lädt eine gepinnte offizielle Elementor-Release mit SHA-256-Prüfung. Keine Bereitstellung auf dem Vereinsserver.

```sh
cd /workspace/Website_BlaskapelleGaustadt
python3 wordpress/tools/build-templates.py
python3 wordpress/tools/package-theme.py
python3 wordpress/tools/start-test-environment.py
```

Danach intern in der Testinstallation anmelden und unter „Gaustadt“ Starterseiten importieren. Der Helfer erzeugt einen lokalen Testbenutzer `gaustadt_test_admin` mit zufälligem Passwort; dieses liegt ausschließlich außerhalb des Checkouts unter `/workspace/gaustadt-wp-test/wp.env`. Werte nicht ausgeben, committen oder veröffentlichen. Server, Datenbank und Zugangsdaten dieser Testumgebung sind keine produktiven Vereinsdienste. Die Testumgebung blockiert externe WordPress-API-Aufrufe; lokale Elementor-Funktionen werden mit den offiziell heruntergeladenen Dateien geprüft.

Vorhandene Container werden nur weiterverwendet, wenn ihre IDs mit der lokal gespeicherten Eigentumsdatei übereinstimmen. Wiederholter Start erhält Testdaten. Die Docker-Datenbank liegt im Testcontainer; ein Umgebungs-Snapshot darf ihren Fortbestand nicht voraussetzen. Bei einem frischen Start Seiten erneut über den regulären Installer importieren. Der importiert Entwürfe; für anonyme Funktionstests nur in dieser lokalen Testinstallation die Beispielseiten veröffentlichen.

Prüfungen für Änderungen:

1. PHP-Syntaxprüfung aller Theme-PHP-Dateien im WordPress-Testcontainer.
2. Starterimport im Backend; acht Seiten als Entwürfe, zwei gemeinsame Vorlagen, wiederholter Import ohne Duplikate oder Überschreiben von Bearbeitungen.
3. Im echten Elementor-Editor eine Überschrift ändern, speichern/veröffentlichen und das Ergebnis im Frontend prüfen. Auch Kopf-/Fußvorlagen öffnen.
4. Im Termine-Widget einen zukünftigen Auftritt eintragen; er erscheint auf der Termineseite und automatisch auf der Startseite. Vergangene und ungültige Datumsangaben getrennt prüfen.
5. Kontaktadresse in Elementor ändern. Servervalidierung, festen Empfänger, Reply-To, ungültige Nonces, Header-Injection, Honeypot, Rate-Limit und fehlende Empfängeradresse prüfen. `wp_mail` in der isolierten Prüfung abfangen; keine echten Nachrichten senden. Im Browser tatsächlichen POST, Erfolg und Mailfehler mit erhaltenen Eingaben prüfen. Ohne JavaScript bleiben die Formularfelder deaktiviert; der direkte E-Mail-Link ist verfügbar. Tatsächliche Zustellung gesondert beim Hoster testen.
6. Galerie-Vergrößerung, internes Menü, HTTP-Status der Seiten, 404-Seite, Desktop und schmale Mobilansicht prüfen.
7. Upload-ZIP mit WordPress installieren und den Inhalt prüfen; keine Testdaten, Geheimnisse, Abhängigkeiten oder WordPress-Core-Dateien einpacken.

Der Starterimport arbeitet nur mit den von ihm gespeicherten Seiten-IDs. Vorhandene Vereinsseiten, bestehende Elementor-Kit-Einstellungen und eigene Bearbeitungen werden beim Wiederholen erhalten. Die Startseiten-Zuordnung wird ausschließlich durch den separaten Button im Backend geändert. Alle schreibenden Backendaktionen benötigen Administratorrechte und einen gültigen WordPress-Nonce.

Die Astro-Dateien im Repository bleiben als ursprünglicher Design-Prototyp erhalten; die eigentliche Elementor-Auslieferung liegt unter `wordpress/`.

Version 1.1 ergänzt Wappenfarben, ein frei bearbeitbares Logo-Widget, gesicherten Farbwechsel vorhandener Dokumente und direkten Kontaktversand. Private Test-Mail-Abfänger oder Test-Empfänger dürfen nie im Theme-Paket stehen. Der Kontakt benutzt weder Nachrichtenspeicherung in WordPress noch externe CAPTCHA-Dienste. [Datenschutz und Übergabe](DATENSCHUTZ-UND-UEBERGABE.md) beschreibt offene Betriebspunkte.
