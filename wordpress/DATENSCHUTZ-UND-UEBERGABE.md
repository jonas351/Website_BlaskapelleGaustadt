# Datenschutz und Übergabe an die Blaskapelle

Stand der technischen Prüfung: 11. Oktober 2026. Diese Hinweise beschreiben den Entwurf und die noch offenen Betriebspunkte. Sie sind keine Bestätigung der rechtlichen Konformität der späteren Website.

## Wer übernimmt welche Verantwortung?

Der Verein ist beim üblichen Betrieb seiner Vereinswebsite der datenschutzrechtlich Verantwortliche. Im Impressum und in der Datenschutzerklärung werden der vollständige rechtliche Name, eine ladungsfähige Anschrift und die vertretungsberechtigten Personen genannt. Der Vorstand sorgt dafür, dass Anfragen, Löschung, Auskunft und technische Betreuung geregelt sind. Ein benannter interner Ansprechpartner ist sinnvoll; das macht ihn noch nicht zum förmlich bestellten Datenschutzbeauftragten.

Ein Datenschutzbeauftragter ist für einen kleinen Verein nicht automatisch erforderlich. Nach § 38 BDSG ist in Deutschland insbesondere die regelmäßige automatisierte Verarbeitung personenbezogener Daten durch mindestens 20 Personen ein Auslöser. Das ist keine Grenze von 20 Vereinsmitgliedern. Unabhängig von dieser Zahl können Artikel 37 DSGVO und weitere gesetzliche Auslöser eine Benennung erfordern, etwa bestimmte umfangreiche Verarbeitungen besonders geschützter Daten oder Verarbeitungen, die eine Datenschutz-Folgenabschätzung verlangen. Die konkrete Vereinsorganisation muss das prüfen.

Wenn du nur das Theme erstellst und übergibst, wirst du dadurch nicht automatisch zum Datenschutzbeauftragten oder zum Verantwortlichen für den Vereinsbetrieb. Bei fortlaufender Administration mit Zugriff auf personenbezogene Daten muss eure tatsächliche Rolle geklärt werden; eine Auftragsverarbeitung und ein Vertrag nach Artikel 28 DSGVO können erforderlich sein. Der Vertrag über die Website sollte Umfang und Ende deiner Betreuung, Updates, Backups und Support festhalten. Der Verein braucht eigene Administratorzugänge. Testkonten und nicht benötigte Zugriffe bei der Übergabe entfernen.

## Was macht die Technik dieses Themes?

- Inhalte und Bilder liegen auf dem eigenen WordPress-Server. Schriftarten werden vom Gerät verwendet; externe Google Fonts durch Elementor werden unterbunden.
- Das Theme enthält keinen Analyse- oder Werbedienst und bindet Instagram nicht ein. Es gibt einen normalen Link zum Profil.
- Das Kontaktformular übermittelt beim Absenden E-Mail, Anliegen, Nachricht und optional einen Namen über den eigenen Server an das eingerichtete Vereins-Postfach. Der Besucher ist `Reply-To`, kein frei wählbarer Absender oder Empfänger.
- Das Theme speichert keine Kontakt-Nachrichten in einer WordPress-Nachrichten-Datenbank. Hosting, Mailanbieter, SMTP-Plugins oder deren Protokolle können dennoch personenbezogene Daten speichern.
- Eine versteckte Spamfalle und kurzlebige Zähler schützen vor wiederholten Versuchen. Der Zähler enthält einen mit geheimem Schlüssel abgeleiteten IP-Hash, keine rohe IP-Adresse und keinen Nachrichtentext. Der Hash ist pseudonymisiert, nicht automatisch anonym. Seine Gültigkeit beträgt eine Stunde ab dem letzten gezählten Versuch. Die tatsächliche Löschung abgelaufener WordPress-Transients erfolgt durch WordPress-Bereinigungsroutinen; deren Betrieb muss sichergestellt sein. Der Webserver verarbeitet unabhängig davon die Verbindungsdaten und kann IP-Adressen protokollieren.
- Ohne bestätigte Empfängeradresse bleibt der Versand deaktiviert. Ein positives `wp_mail`-Ergebnis bedeutet die Annahme durch den Mailtransport, nicht die nachgewiesene Zustellung im Postfach.
- Es werden keine externen CAPTCHA-Dienste benötigt. Für neue Dienste, zusätzliche Plugins oder geänderte Inhalte ist die Bewertung erneut notwendig.

## Brauchen wir ein Cookiebanner?

Nicht automatisch. Die technische Speicherung beziehungsweise der Zugriff auf Endgeräte ist insbesondere nach § 25 TDDDG zu bewerten. Für nicht notwendige Cookies, Tracking oder entsprechende Fremddienste kann vorherige Einwilligung erforderlich sein. Ein pauschales Banner macht eine Website nicht datenschutzkonform. Bei ausschließlich erforderlichen Funktionen kann ein Einwilligungsbanner entbehrlich sein. Die tatsächliche WordPress-Installation, Plugins, Hosting und neu hinzugefügte Einbettungen müssen dafür geprüft werden. In der geprüften anonymen Browser-Sitzung dieses Theme-Entwurfs wurden keine Besucher-Cookies oder externen Ressourcenhosts festgestellt; das ist keine Garantie für jede spätere Konfiguration oder jeden Browser.

## Was muss vor der Veröffentlichung feststehen?

1. **Verein und Kontakt:** rechtlicher Name, Vorstand/Vertretung, Anschrift, echte Kontaktadresse und interner Ansprechpartner für Datenschutzanliegen.
2. **Hosting und Mail:** Anbieter, Serverstandorte, Unterauftragnehmer und mögliche Drittlandübermittlungen klären. Erforderliche Verträge zur Auftragsverarbeitung abschließen. Serverprotokolle, SMTP-Protokolle, Postfächer und Backups in die Betrachtung aufnehmen.
3. **Datenschutzerklärung:** Platzhalter mit dem tatsächlichen Betrieb ersetzen. Zwecke, Rechtsgrundlagen, Empfänger und Speicherdauer beschreiben. Für Kontakt können je nach Anfrage Artikel 6 Absatz 1 Buchstabe b beziehungsweise f DSGVO einschlägig sein; keine pauschal erfundene Einwilligung annehmen. Betroffenenrechte und zuständige Aufsicht nennen. Rechtsgrundlage und Dauer auch für Spamabwehr und Protokolle prüfen. In Bayern kommt bei einem privaten Verein regelmäßig das Bayerische Landesamt für Datenschutzaufsicht in Betracht.
4. **Fotos und Inhalte:** Berechtigung zur Nutzung von Logo, Bildern und Texten klären. Bei erkennbaren Personen Bildnisrechte und Datenschutz berücksichtigen; Kinderbilder besonders sorgfältig behandeln. Die gelieferten Illustrationen sind keine tatsächlichen Kapellenfotos.
5. **Technischer Betrieb:** HTTPS aktivieren, aktuelle unterstützte WordPress-/PHP-/Pluginversionen nutzen, individuelle starke Zugangsdaten, möglichst Zwei-Faktor-Anmeldung, funktionierende Backups und Wiederherstellung vorsehen. Nur notwendige Plugins betreiben. In Mail-Plugins möglichst keine vollständigen Nachrichtentexte protokollieren.
6. **Praktischer Übergabetest:** mit eigenen Testdaten über die echte Serverdomain absenden, tatsächlichen Eingang und Antwortadresse prüfen. Auch Fehlerfall, Handyansicht, sämtliche Links und das Entfernen verbliebener Platzhalter kontrollieren. Löschung und Auskunft organisatorisch regeln. Bei Auskunft gilt grundsätzlich die gesetzliche Monatsfrist, vorbehaltlich der gesetzlichen Verlängerungsmöglichkeiten.

## Gesetzliche Grundlagen zum Nachlesen

- [DSGVO, insbesondere Artikel 6, 13, 28, 32 und 37](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32016R0679)
- [§ 38 BDSG – Datenschutzbeauftragte nichtöffentlicher Stellen](https://www.gesetze-im-internet.de/bdsg_2018/__38.html)
- [§ 25 TDDDG – Schutz der Privatsphäre bei Endeinrichtungen](https://www.gesetze-im-internet.de/tdddg/__25.html)

Die Gesetzeslinks sind Quellen zum Nachlesen. Ein aktueller Abruf dieser externen Domains war in der Cloud-Prüfumgebung durch den Netzwerkproxy blockiert. Die tatsächlichen Vereinsdaten, Verträge, produktive Mailzustellung und der spätere öffentliche Server wurden hier nicht geprüft.
