# FireBow in Local anschauen

Die ZIP ist ein **WordPress-Theme**. Elementor Free genügt. Es sind elf Seiten enthalten: Start, Leistungen, vier Leistungsdetails, Über uns, FAQ, Kontakt, Impressum und Datenschutz. Kopf- und Fußbereich sind ebenfalls mit Elementor bearbeitbar.

## Einmal einrichten

1. In **Local** auf **+** klicken und eine **neue Website** namens FireBow anlegen. Deine anderen Local-Projekte bleiben erhalten.
2. **WP Admin** öffnen und anmelden.
3. Unter **Plugins → Installieren** das kostenlose Plugin **Elementor Website Builder** installieren und aktivieren. Falls es bereits vorhanden ist, nur aktivieren.
4. **Design → Themes → Neues Theme hinzufügen → Theme hochladen** öffnen.
5. **firebow-elementor.zip** auswählen, installieren und aktivieren. Die ZIP vorher nicht entpacken.
6. Links auf **FireBow** klicken, dann **FireBow-Seiten anlegen**.
7. **Alle FireBow-Seiten in Local anschauen** anklicken.
8. In Local **Open Site** öffnen. Die gesamte Website einschließlich Unterseiten ist jetzt erreichbar.

## Etwas ändern

Bei Logo, Teamfoto, Formular und FAQ bewegst du die Maus über das Element und klickst oben rechts auf dessen kleines **Bleistiftsymbol**. Falls das schwebende Fenster **Struktur** den Bleistift verdeckt, dieses Fenster zuerst mit dem **×** schließen.

- **Text oder Überschrift:** FireBow → passende Seite → Mit Elementor bearbeiten. Text anklicken und links ersetzen. Mit Veröffentlichen/Aktualisieren speichern.
- **FAQ:** FAQ-Seite → Mit Elementor bearbeiten → Maus über den Fragenbereich bewegen → oben rechts auf das kleine Bleistiftsymbol klicken. Links öffnet sich FireBow Fragen & Antworten. Einen Eintrag öffnen und die separaten Felder Frage und Antwort ändern. Über „Element hinzufügen“ weitere Fragen anlegen. Die Startseite übernimmt die ersten drei Fragen automatisch. Es muss kein HTML bearbeitet werden.
- **Teamfoto:** Über uns → Mit Elementor bearbeiten → Platzhalterfoto anklicken → FireBow Teamfoto → Foto auswählen. Nach dem Speichern übernimmt die Startseite das Foto automatisch. Auf der Startseite kann bei Bedarf ein anderes Foto ausgewählt werden.
- **Logo:** Der neue Bogen mit brennendem Pfeil ist bereits eingebaut. Für ein anderes vollständiges Logo: FireBow → Kopfbereich & Menü bearbeiten → FireBow Logo → Eigenes vollständiges Logo. PNG/WebP mit transparentem Hintergrund verwenden. Der Fußbereich übernimmt das Logo. Das Bildfeld leeren, um wieder den mitgelieferten Bogen und den FireBow-Schriftzug zu verwenden.
- **Menü:** Im Kopfbereich das Widget FireBow Menü anklicken. Beschriftungen und Links sind einzeln bearbeitbar.
- **E-Mail:** Kontakt → FireBow Anfrage → Kontakt-E-Mail. Eingetragen ist **jonas.bogensperger@firebow.net**, wie von Jonas bestätigt. Nach dem Speichern verwenden die anderen Seiten dieselbe Adresse.
- **Farben:** Gewünschtes Element wählen → Stil. Die voreingestellten Farben sind Creme `#f8f4ed`, Dunkelbraun `#30251f`, Kupferorange `#a44720` und Sand `#eee5d8`.

## Was im Entwurf noch fehlt

Das echte Teamfoto fehlt noch als eigene Bilddatei. Das Logo ist jetzt ein neu gestalteter, leicht comicartiger Bogen mit brennendem Pfeil auf transparentem Hintergrund. Der kleine Website-Ausschnitt auf der Startseite ist ein eigenes **Gestaltungsbeispiel**, keine behauptete Kundenreferenz.

Die Beschreibungen beruhen auf den beiden Screenshots und Jonas’ Bestätigung von Team, Kontaktadresse und Farben. Die neuen FAQ-Antworten und Leistungsbeschreibungen sind **Textentwürfe**. Preise, Termine, garantierte Suchplatzierungen, Kundenstimmen oder Referenzfreigaben wurden nicht erfunden. Angaben zum Studium und EDEKA-Markt stammen aus dem Screenshot und sollten vor Veröffentlichung auf Aktualität geprüft werden.

## Kontaktformular

Das Formular übergibt Nachrichten an WordPress `wp_mail`. In Local werden diese normalerweise im dortigen **Mailpit** aufgefangen; sie kommen dadurch nicht automatisch im echten Postfach an. Für den echten Server muss der Mailversand/SMTP eingerichtet und die tatsächliche Zustellung geprüft werden. Es wird kein kostenpflichtiges Elementor-Formular benötigt.

Das Theme speichert keine eigene Nachrichtensammlung. Hosting, Mailanbieter oder zusätzlich installierte Plugins können Nachrichten und Protokolle speichern. Ohne JavaScript bleiben die Formularfelder deaktiviert; der direkte E-Mail-Link ist weiterhin nutzbar.

## Später veröffentlichen

Erst Texte, Nutzungsrechte, Kontaktdaten, Impressum und Datenschutz prüfen und vervollständigen. Die rechtlichen Seiten sind **sichtbar markierte Vorlagen**. Im neuen Hosting die gesamte WordPress-Website samt Datenbank und Uploads migrieren; eine Theme-ZIP allein enthält keine späteren Änderungen aus Elementor. Danach Domain/HTTPS und tatsächlichen Mailversand prüfen.

Die lokale Vorschaufunktion ist nur für `localhost`, Loopback-Adressen sowie `.local`- und `.test`-Adressen verfügbar. Auf einem echten Server werden die Projektseiten zunächst als Entwürfe angelegt. Freigegebene Seiten einzeln veröffentlichen und anschließend in FireBow die Startseite einstellen.

Eine bestehende FireBow-Installation kann das Theme aktualisieren. **Seiten erneut anlegen ersetzt keine schon bearbeiteten Inhalte.** Änderungen an mitgelieferten JSON-Dateien werden deshalb nicht automatisch über ältere importierte Seiten geschrieben.

## Bereits installiert? Auf Version 1.1 aktualisieren

1. Die neue **firebow-elementor.zip** herunterladen.
2. In WordPress **Design → Themes → Neues Theme hinzufügen → Theme hochladen** öffnen und die ZIP auswählen.
3. **Installieren** und anschließend **Aktuelles durch hochgeladenes ersetzen** anklicken.
4. Die Website neu laden. Das neue Logo und der korrigierte Startseitenlink werden automatisch übernommen; Elementor-Inhalte bleiben erhalten. **Die Seiten nicht erneut anlegen.**

Wenn bereits ein eigenes Logo im Elementor-Widget ausgewählt ist, bleibt es erhalten. Für den neuen Bogen dieses Bildfeld leeren. Das Logo im Kopf- und Fußbereich führt zur tatsächlich angelegten FireBow-Startseite, auch wenn WordPress momentan eine andere Startseite oder eine Beitragsliste verwendet.
