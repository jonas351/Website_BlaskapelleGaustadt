# FireBow – persönlicher Elementor-Entwurf

Eigenständiges Projekt. Die Blaskapellen- und CSU-Projekte werden durch die Installation in einer separaten Local-Website nicht geändert.

- `releases/firebow-elementor.zip`: installierbares WordPress-Theme.
- `firebow-elementor/`: vollständiger Theme-Quelltext und 13 native Elementor-Vorlagen.
- `ANLEITUNG.md`: einfache Einrichtung und Bearbeitung.
- `vorschau/`: Screenshots der getesteten WordPress-Version.
- `PRUEFBERICHT.md`: tatsächliche Prüfungen und offene Punkte.

Die Inhalte sind aus den übermittelten Screenshots abgeleitet. Die direkte Website firebow.de konnte in dieser Umgebung wegen einer Proxy-Sperre nicht abgerufen werden. Die Original-Bilddateien fehlen noch.

Paket neu erstellen: `python projects/firebow/tools/package.py` aus dem Repository-Hauptverzeichnis. PHP ab 8.1, WordPress ab 6.8 und Elementor Free werden benötigt. Der Entwurf nutzt Systemschriften ohne externen Font-Abruf.
