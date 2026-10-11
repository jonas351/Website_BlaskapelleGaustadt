# Prüfung der Gaustadt-Version 1.1.0

Geprüft am 11. Oktober 2026 in einer eigenen WordPress-Testinstallation mit WordPress 7.1.3, Elementor Free 4.3.0 und PHP 8.3.

- Alle acht Seiten: HTTP 200, jeweils eine Hauptüberschrift und kein horizontaler Überlauf bei 1440, 768, 390 und 320 Pixeln. Bilder geladen, mobiles Menü einschließlich Escape geprüft. Unbekannte Adresse zeigt die eigene 404-Seite.
- Neues Farbschema, Startseite und Kontaktseite im anonymen Browser geprüft. Vorschauen unter `vorschau/`. In dieser Sitzung keine Besucher-Cookies, externen Ressourcenhosts oder JavaScript-Fehler festgestellt.
- Aktualisierung über die tatsächliche WordPress-Verwaltung geprüft. Die Sicherung stellt alle zehn Elementor-Dokumente und ihre Seiteneinstellungen exakt wieder her. Wiederholte Aktualisierung überschreibt die Sicherung nicht. Vorhandene Texte, Termine und Kontaktadresse bleiben beim Farbwechsel erhalten.
- Local-Vorschau veröffentlicht nur die acht Projektseiten und setzt deren Startseite; fremde Entwürfe bleiben erhalten. Vorschaufunktion auf einer Produktionsdomain abgewiesen. Ungültige Verwaltungs-Nonces abgewiesen.
- Kontaktformular im Browser einschließlich Erfolg, Versandfehler mit Erhalt der Eingaben, fehlender Empfängeradresse und Alternative ohne JavaScript geprüft. Ungültige Eingaben, Header-Injection, Spamfalle, ungültige Nonce und Versuchslimit serverseitig geprüft.
- E-Mails wurden ausschließlich in der isolierten Testinstallation abgefangen. Kein Testversand an echte Empfänger; tatsächliche Postfachzustellung ist noch offen.
- PHP-Syntax, JavaScript-Syntax und ZIP-Integrität geprüft. Das ZIP wurde mit dem echten WordPress-Theme-Installer installiert.

Das Originalwappen muss aus der eigenen Bilddatei im neuen Logo-Widget ausgewählt werden. Die mitgelieferten Illustrationen sind Platzhalter. Echte Vereinsdaten, Bildfreigaben, Hosting, Mailtransport und Rechtstexte bleiben vor der Veröffentlichung zu ergänzen und zu prüfen. Diese Prüfung ist keine DSGVO-Zertifizierung. Siehe [Datenschutz und Übergabe](DATENSCHUTZ-UND-UEBERGABE.md).
