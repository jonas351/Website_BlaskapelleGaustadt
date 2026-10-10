# Prüfung der Version 1.2

Geprüft am 10. Oktober 2026 in der isolierten WordPress-Testinstallation mit WordPress 7.1.3, Elementor Free 4.3.0 und PHP 8.3.35. Die bestehende Website team-bamberg.de und die private Local-Installation des Nutzers wurden nicht verändert.

## Behobene Probleme

- Die Stadtteilseiten verwendeten bisher viele getrennte Originalabschnitte mit einzelnen Überschriften und unruhigen Kontaktbereichen. Alle acht Seiten haben jetzt eine eigene, quellenbasierte Einführung, Stadtteilbild, Orientierung, zusammenhängende Geschichte und Kontaktkarten.
- Die Ortsverbandsübersicht führte bei Wunderburg auf die externe Originalwebsite. Die neue Übersicht und die Startseite verlinken alle acht internen Stadtteilseiten.
- Projektseiten starten als Entwürfe und sind dadurch ohne Anmeldung nicht erreichbar. Die vorherigen Tests hatten bereits veröffentlichte Seiten benutzt und diese Lücke im Local-Ablauf nicht erkannt. Die Vorschau ist jetzt vor der Seitentabelle sichtbar; beim Update kann sie ausdrücklich mit einer Checkbox für alle Projektseiten eingerichtet werden.
- Sprungziele für Stadtteil und Ansprechpartner verwenden den von Elementor tatsächlich unterstützten Container-ID-Schlüssel. Die gerenderten Ziele und ein tatsächlicher Klick mit sichtbarem Ziel wurden geprüft.
- Verschleierte und teilweise beschädigte E-Mail-Fragmente werden als verständliche Kontaktinformation angezeigt; Adressen werden nicht erraten. Vollständig veröffentlichte Adressen bleiben als Kontaktweg verfügbar. Originalangaben bleiben in der Quellendokumentation erhalten.
- Ein alter Mitgliedsantrag-Link lieferte bei der Prüfung HEAD 404 und GET 500. Er wurde mit passender Beschriftung durch die erreichbare offizielle Mitgliedschaftsseite ersetzt. Zwei fehlerhafte CSU-Präfixe vor Google-Adressen im historischen Datenschutztext wurden entfernt; der alte Rechtstext bleibt ausdrücklich zur Aktualisierung markiert.

## Funktionsprüfung

- Alle 45 eigenen Seiten bei 1440, 768, 390 und 320 Pixeln: HTTP 200, eine Hauptüberschrift, kein horizontaler Überlauf.
- Alle acht Stadtteilseiten durch tatsächliche Klicks von der Startseite und von der Ortsverbandsübersicht erreicht: 16 Navigationswege ohne WordPress-Anmeldung.
- Auf jeder Stadtteilseite vollständige Geschichte, vorgestellte Personen und beide Sprungziele geprüft; Desktop- und Handyansichten als echte WordPress-Screenshots gespeichert.
- Die zuletzt korrigierten Übersichtsbilder füllen ihre Karten bei allen vier Bildschirmgrößen aus; Bildbreite, geladene Bilder und fehlenden horizontalen Überlauf am endgültig installierten Paket erneut kontrolliert.
- Alle 119 unterschiedlichen internen Linkziele überprüft; keine leeren oder nicht unterstützten Links. Sämtliche dargestellten Bilder auf allen Seiten geladen und auf gültige Bildabmessungen geprüft: 82 unterschiedliche Bildadressen.
- Archivsuche nach Text und Jahr, leeres Suchergebnis, lokales Original-PDF, WordPress-Suche, mobiles Menü mit Escape, eigene 404, Formularvalidierung, Vorbereitung und Kopieren der Nachricht, Formular ohne JavaScript geprüft. Die Kontaktvorschau versendet keine E-Mails.
- Echte Elementor-Bearbeitung, Veröffentlichung und Wiederherstellung der Startseitenüberschrift. Zusätzlich alle acht Stadtteilüberschriften einzeln mit tatsächlichen Tastatureingaben bearbeitet, gespeichert, im Frontend kontrolliert und wiederhergestellt.
- Update sichert alle 47 Elementor-Dokumente. Exakte Wiederherstellung, erneutes Update ohne Verlust der Sicherung, Erhalt von Termineinstellungen, Kontakt-Empfänger und Menü geprüft.
- Local-Ablauf mit nur veröffentlichter Startseite und Gaustadt sowie 43 weiteren Projektentwürfen nachgestellt. Der Update-Knopf richtet die vollständige lokale Vorschau ein; ein fremder Entwurf bleibt unveröffentlicht. Auf einem öffentlichen Produktionshost wird die Local-Vorschau verweigert. Falsche Update-Nonce wird abgewiesen.
- PHP-Syntax, Python-Kompilierung, ZIP-Integrität und Installation über den echten WordPress-Theme-Upgrader geprüft. Alle 151 ursprünglichen Medien und deren SHA-256-Werte bleiben erhalten.

## Grenzen der Prüfung

Externe Original-Links wurden ebenfalls angefragt. Der Netzwerkzugang dieser Cloud-Umgebung ist auf die bisherigen erlaubten Domains beschränkt. Zahlreiche Stadtratsdokumente auf stadt.bamberg.de sowie weitere fremde Websites werden bereits vom Netzwerkproxy blockiert. Diese Links sind **nicht als funktionierend bestätigt und nicht allein aufgrund dieser Blockierung als defekt bewertet**. Sie bleiben als Originalreferenzen erhalten und müssen außerhalb dieser Umgebung überprüft werden.

Die Prüfung aktualisiert keine Ämter, Kontaktdaten, Bankangaben oder Rechtstexte. Die bereits dokumentierten sachlichen Prüfpunkte gelten weiterhin. Eine neue Cloud-Wiederherstellung oder Installation auf dem späteren öffentlichen Server wurde hier nicht durchgeführt.
