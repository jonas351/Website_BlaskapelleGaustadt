# Gaustadt-Website mit Elementor bearbeiten

Ihr bekommt eine WordPress-Website, die ihr direkt im Browser pflegt. Elementor Free genügt. Nach der einmaligen Einrichtung sind für die Pflege keine Terminalbefehle nötig.

## Einmalig einrichten

Voraussetzung: Auf dem Server ist WordPress installiert. Das kann der Serverbetreuer vorbereiten. Ihr benötigt einen WordPress-Administratorzugang.

1. **gaustadt-elementor.zip** aus `wordpress/releases/` herunterladen. Diese ZIP-Datei für den Upload **nicht entpacken**.
2. In WordPress: **Design → Themes → Theme hinzufügen → Theme hochladen**. ZIP auswählen, installieren und aktivieren. Auf einer bereits bestehenden Website zunächst in einer Testkopie einrichten: Das Aktivieren eines Themes ändert deren Darstellung.
3. Links **Gaustadt** öffnen. Falls Elementor noch fehlt, **Elementor installieren** und anschließend aktivieren. Dafür ist keine Pro-Lizenz nötig. Danach wieder **Gaustadt** öffnen.
4. Auf **Website-Seiten anlegen** klicken. Alle acht Seiten sind zunächst Entwürfe; vorhandene Seiten werden nicht überschrieben.
5. Unter **Gaustadt** bei einer Seite **Mit Elementor bearbeiten** anklicken, die Platzhalter ersetzen und die Seite **veröffentlichen**. Das für die übrigen Seiten wiederholen.
6. Unter **Gaustadt** auf **Gaustadt als Startseite aktivieren** klicken. Der Button erscheint, sobald die Startseite veröffentlicht wurde. Bei einer bestehenden Website ersetzt das ihre bisherige Startseiten-Zuordnung.

WordPress und Elementor führen für ihre Grundfunktionen gegebenenfalls eigene Einrichtungsdialoge vor. Eine Anmeldung bei Elementor oder ein kostenpflichtiges Upgrade ist für diese Vorlagen nicht erforderlich.

## Einen Text ändern

1. **Gaustadt → gewünschte Seite → Mit Elementor bearbeiten**.
2. Den Text anklicken. Links die Überschrift oder den Text ändern.
3. **Aktualisieren / Veröffentlichen** anklicken. Je nach Elementor-Version heißt der Speicherbutton auch **Publish**.

## Ein Foto ersetzen

1. Das Bild in Elementor anklicken.
2. Links auf das Bildfeld klicken und ein eigenes Foto aus der Mediathek auswählen oder hochladen.
3. Einen passenden Alternativtext hinterlegen und speichern.

Für die Galerie: Das Galerie-Element anklicken und **Bilder hinzufügen/bearbeiten** wählen. Ihr könnt Bilder hinzufügen, entfernen und die Reihenfolge ändern. Die mitgelieferten Grafiken sind deutlich gekennzeichnete Illustrationen, keine echten Vereinsfotos.

## Einen Auftritt eintragen

1. Die **Termineseite** mit Elementor öffnen.
2. Das Element **Gaustadt Termine** anklicken.
3. Links **Element hinzufügen** anklicken. Veranstaltung, Datum, Uhrzeit und Ort eintragen; weitere Infos und ein Link sind optional.
4. Speichern und die Termineseite veröffentlichen.

Der nächste bestätigte Auftritt erscheint automatisch auf der Startseite. Vergangene Termine wandern nach dem Datum in den Rückblick. Dafür ist kein erneuter Website-Build nötig. Die Website nutzt die in WordPress eingestellte Zeitzone; für den Verein unter **Einstellungen → Allgemein** „Berlin“ auswählen.

Auf der Startseite bleibt beim Termine-Element **Automatisch von der Termineseite** ausgewählt. Die Termine werden nur an einer Stelle gepflegt.

## Die Kontaktadresse ändern

1. Die **Kontaktseite** mit Elementor öffnen.
2. Das Element **Gaustadt Anfrage** anklicken.
3. Unter **Eure Kontakt-E-Mail** die echte Adresse eintragen und speichern.

Die Kontaktadresse wird nach Veröffentlichung auch im Kontaktbereich und in den gelieferten Rechtstext-Vorlagen angezeigt. Der kurze Platzhalter `[gaustadt_email]` in diesen Textfeldern bleibt dafür stehen.

Die Anfragehilfe erstellt eine Nachricht, die Besucher kopieren oder im eigenen E-Mail-Programm öffnen. Sie sendet keine E-Mail automatisch. Ohne hinterlegte Adresse führt der manuelle Kontaktweg zu Instagram. Ein klassisches Formular mit automatischem E-Mail-Versand müsste zusätzlich eingerichtet werden.

## Menü, Kopf- und Fußbereich ändern

Unter **Gaustadt** gibt es eigene Buttons **Kopfbereich & Menü bearbeiten** und **Fußbereich bearbeiten**. Beide öffnen Elementor. Änderungen gelten auf allen Seiten.

Für Menüpunkte das Element **Gaustadt Menü** anklicken. Beschriftungen, Reihenfolge und Links können links im Editor angepasst werden. Das mobile Menü funktioniert automatisch.

## Farben und Gestaltung ändern

Element auswählen → **Stil** → Farbe, Schrift oder Abstände anpassen. Die Startwerte Grün, Creme und Gold sind vorläufig, weil das Instagram-Profil in der Cloud nicht abrufbar war. Das `bg`-Textlogo ist ebenfalls ein Entwurf.

Die Schrift **Gaustadt Serif** verwendet vorhandene Schriften auf dem Gerät und benötigt keinen externen Schriftartendienst. Das Theme unterbindet das Laden externer Google Fonts durch Elementor. Andere zusätzliche Plugins können eigene externe Dienste mitbringen.

## Vor dem öffentlichen Start

- Kontaktadresse und Probenangaben vervollständigen.
- Kapellenvorstellung, Beiträge und Vereinsgeschichte durch bestätigte Angaben ersetzen.
- Eigene, freigegebene Fotos und gegebenenfalls das echte Logo einfügen.
- Impressum und Datenschutz mit den tatsächlichen Vereins-, Hosting- und Pluginangaben ergänzen und prüfen. Die gelieferten Texte sind ausdrücklich Vorlagen.
- Alle verlinkten Seiten veröffentlichen. Ein Link zu einem noch nicht veröffentlichten Entwurf ist für normale Besucher nicht verfügbar.
- Die Mobilansicht in Elementor und auf einem Smartphone prüfen.

Der Installer überschreibt beim erneuten Aufrufen keine bereits importierten Seiten. WordPress-, Hosting- oder Elementor-Einstellungen wie vorhandene Globale Farben werden nicht ersetzt. Das Theme **Gaustadt für Elementor** bleibt aktiv, damit Kopfbereich, Termine und Anfragehilfe zur Verfügung stehen.

## An den Serverbetreuer

Benötigt werden WordPress ab 6.8, PHP ab 8.1 und Elementor Free. Für den Server empfiehlt WordPress eine aktuelle unterstützte PHP-Version (z. B. 8.3+) und MySQL/MariaDB. Mediathek und Upload-Verzeichnis müssen schreibbar sein. HTTPS, Backups und reguläre WordPress-/Pluginupdates wie üblich einrichten. Die ZIP enthält nur das Theme; WordPress und Elementor werden regulär installiert und aktualisiert.

Es gibt keinen Zugriff auf euren Server in diesem Projekt; die Einrichtung dort ist noch nicht erfolgt.
