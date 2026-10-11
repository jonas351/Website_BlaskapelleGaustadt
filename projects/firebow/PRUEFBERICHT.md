# FireBow – Prüfbericht

Geprüft am 11. Oktober 2026 in einer **eigenen, frischen Testinstallation** mit WordPress 7.1.3, Elementor Free 4.3.0 und PHP 8.3.35. Die bestehende Website firebow.de sowie die Local-Projekte von Jonas wurden nicht verändert. Die bisherigen Blaskapellen- und CSU-Quelltexte bleiben unverändert.

## Installation und Inhalte

- Die Theme-ZIP wurde mit dem tatsächlichen WordPress-Theme-Installer installiert und mit dem Installer aktualisiert.
- Einrichtung über die echte WordPress-Admin-Oberfläche: **elf Seiten als Entwürfe** und zwei gemeinsame Elementor-Bereiche angelegt, anschließend über den Local-Button freigeschaltet.
- Wiederholter Import behält bestehende Inhalte. Auch ein tatsächlich veränderter Elementor-Text wurde beim erneuten Import nicht überschrieben.
- Die vorherige Startseiten-Zuordnung konnte über die Oberfläche wiederhergestellt und die FireBow-Vorschau anschließend erneut aktiviert werden.
- 13 native Elementor-Dokumente mit eindeutigen Element-IDs. Texte, Überschriften, Buttons und Layoutcontainer sind eigene Elemente; keine ganze Seite als HTML-Widget. Menü, Logo, Teamfoto, Formular und FAQ haben eigene Elementor-Bedienfelder. Elementor Pro ist nicht erforderlich.

## Darstellung und Navigation

- Alle elf Seiten bei **1440, 768, 390 und 320 Pixeln** geprüft: HTTP 200, genau eine Hauptüberschrift im Inhalt, kein horizontaler Überlauf.
- Alle gefundenen internen Linkziele erreichbar; keine unaufgelösten Vorlagenlinks. Die Anfragebuttons öffnen die Kontaktseite mit passendem Anliegen.
- Mobiles Menü geöffnet, echten Seitenwechsel ausgelöst, mit Escape geschlossen und Fokus geprüft.
- FAQ aufgeklappt; auch ohne JavaScript bedienbar.
- Ohne JavaScript bleiben Navigation und direkter E-Mail-Link nutzbar. Das mobile Menü wurde auch ohne JavaScript bei 390 und 320 Pixeln ohne horizontalen Überlauf geprüft.
- Nicht existierende URL liefert eine echte HTTP-404-Seite mit Weg zurück zur Startseite.
- In der geprüften anonymen Frontend-Konfiguration: keine JavaScript-Fehler, keine externen Browser-Netzwerkziele und keine Cookies. Eingebettete Daten-URLs sind lokale Darstellungsdaten. Diese Aussage gilt nicht pauschal für zusätzliche Plugins oder das spätere Hosting.

## Tatsächliche Elementor-Bearbeitung

- Eine native Hauptüberschrift direkt im Editor geändert, gespeichert und auf der Website geprüft; danach den Originaltext wiederhergestellt.
- FAQ über die echten Felder im Editor geändert und gespeichert. Die Startseite übernahm die Änderung automatisch. Originalfrage anschließend wiederhergestellt.
- Der schwebende Elementor-Bereich **Struktur** kann das Bleistiftsymbol eines Widgets verdecken. Nach Schließen dieses Fensters ist die Bedienung zugänglich; die Anleitung beschreibt das.
- Mit einem nur intern angelegten WordPress-Testbild geprüft: Kopf- und Fußbereich verwenden dasselbe Logo; die Startseite übernimmt das Foto aus „Über uns“. Bilddatei geladen und Alternativtext geprüft. Testmedium und Testzuordnungen anschließend entfernt.

## Kontaktformular

- Vier Anfragekontexte geprüft: Website, Buchungssystem, Formular und SEO.
- Echten Formularaufruf im Browser durchgeführt. WordPress-Mailaufruf wurde **ausschließlich intern abgefangen**; an das echte Postfach wurde nichts gesendet.
- Empfänger aus dem veröffentlichten Elementor-Widget, Betreff, Nachricht und Reply-To geprüft. Ein mitgeschickter anderer Empfänger beeinflusst den Versand nicht.
- Versandfehler wird im Formular angezeigt; Nachricht bleibt erhalten und erneute Bearbeitung ist möglich.
- Ungültige Nonce, falsche Feldtypen, Mail-Header-Injektion, unbekanntes Anliegen, zu kurze/lange Nachricht und ausgefülltes Spamfeld werden abgewiesen.
- Nach fünf Versuchen innerhalb einer Stunde greift die Begrenzung. Der Zähler enthält einen HMAC-Schlüssel statt einer unveränderten Netzwerkadresse und keinen Nachrichtentext.
- Eine unveröffentlichte Kontaktseite liefert keine Versandkonfiguration. Ohne JavaScript sind die Formularfelder deaktiviert und der E-Mail-Link bleibt sichtbar.

## Paket

PHP-Syntax aller Theme-Dateien, JavaScript-Syntax, JSON-Dokumente, ZIP-Integrität und Dateileserechte geprüft. Das Paket enthält keine Testinstallation, Testzugangsdaten oder privaten Mailmitschnitte.

## Noch zu ergänzen

Original-Logo und Teamfoto fehlen als eigenständige Bilddateien. Die neuen FAQ-Antworten und Leistungsbeschreibungen sind freizugebende Textentwürfe. Preise und feste Umsetzungstermine werden nicht behauptet. Impressum und Datenschutz sind markierte Vorlagen. Für eine echte Veröffentlichung müssen Betreiberangaben, Nutzungsrechte, Hosting und Mailanbieter ergänzt bzw. geprüft werden; SMTP und tatsächliche Postfachzustellung sind erst auf dem echten Server zu testen. Es wurde keine allgemeine rechtliche Zertifizierung vorgenommen.
