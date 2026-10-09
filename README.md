# Blaskapelle Gaustadt

Responsive, statische Vereinswebsite mit Astro. Seiten: Startseite, Kapelle, Termine, Galerie, Mitmachen, Kontakt, Impressum und Datenschutz; eigene 404-Seite. Keine Datenbank, kein Tracking, keine extern geladenen Schriftarten und keine Instagram-Einbettung.

## Lokal entwickeln

Voraussetzung: Node.js 22.12+ oder Node.js 24 LTS und npm. In dieser Cloud-Umgebung ist Node.js 24 vorhanden.

```sh
cd /workspace/Website_BlaskapelleGaustadt
npm ci --cache /workspace/.npm-cache
ASTRO_TELEMETRY_DISABLED=1 npm run dev -- --port 4321
```

Produktionsbuild: `ASTRO_TELEMETRY_DISABLED=1 npm run build`.
Build lokal prüfen: `ASTRO_TELEMETRY_DISABLED=1 npm run preview -- --port 4322`.
Der Ausgabeordner `dist/` kann bei einem statischen Hosting-Anbieter bereitgestellt werden. Entwicklungs- und Vorschauprozesse müssen in neuen Cloud-Aufgaben neu gestartet werden. Den vorhandenen Checkout verwenden; kein zusätzliches Git-Worktree erforderlich.

## Inhalte ändern

- `src/data/site.ts`: Vereinsangaben, Kontakt-E-Mail, Probenort/-zeit, rechtliche Angaben, bestätigte Termine und Galerieeinträge.
- `src/pages/`: Seitentexte, insbesondere Vorstellung der Kapelle und Antworten zum Mitmachen. Mit `[ … ]` markierte Inhalte sind Platzhalter.
- `src/styles/global.css`: Farben über `--green`, `--cream`, `--gold` usw. am Anfang. Grün, Creme und Gold sind eine **vorläufige Gestaltung**, da das Instagram-Profil in der Cloud nicht zugänglich war. Es wurde kein offizielles Logo übernommen: `bg` ist eine vorläufige Wortmarke.
- `public/images/`: eigene freigegebene Fotos ablegen; in `gallery` eintragen. Die Galerie zeigt dann Fotos und bietet per Klick eine Vergrößerung. Die derzeitigen Musikgrafiken sind Illustrationen, keine Vereinsfotos.

### Termine

In `events` beispielsweise folgenden Eintrag mit **echten, bestätigten Angaben** ergänzen:

```ts
{
  title: 'Titel der Veranstaltung',
  date: '2027-06-20', // Beispiel, kein tatsächlicher Auftritt
  time: '18:00',
  place: 'Veranstaltungsort',
  description: 'Informationen für Besucherinnen und Besucher.',
  url: 'https://example.org/veranstaltung', // optional
}
```

Termine werden sortiert, zukünftige und vergangene Auftritte getrennt angezeigt; die Startseite zeigt den nächsten Auftritt. Da diese Website statisch gebaut wird, nach Inhaltsänderungen und für einen aktuellen Terminüberblick neu bauen. Die Trennung erfolgt anhand des Build-Datums.

### Fotos

```ts
{
  src: '/images/konzert.jpg',
  alt: 'Sachliche Beschreibung des tatsächlichen Bildes',
  caption: 'Titel oder Veranstaltung',
  category: 'Auftritte',
}
```

Nur Bilder mit gesicherten Nutzungsrechten und erforderlichen Einwilligungen veröffentlichen. Keine automatisch eingebundenen Instagram-Bilder.

### Kontakt

Die Anfragehilfe validiert Name, E-Mail und Nachricht und erstellt Text **nur im Browser**. Es gibt keinen Formularserver und keinen automatischen Versand. Ohne `site.email` wird der Text kopiert und manuell über Instagram versendet. Mit hinterlegter E-Mail wird zusätzlich das E-Mail-Programm über `mailto:` geöffnet. Personenbezogene Daten werden nicht in Browser-Speichern abgelegt.

Für einen direkten Formularversand wäre ein separat eingerichteter Backend-/Formulardienst mit Datenschutzkonfiguration nötig. Die aktuelle Oberfläche behauptet keinen erfolgten Versand.

## Vor Veröffentlichung

1. Instagram-Farben, Original-Logo, Texte und Bilder mit der Kapelle abstimmen.
2. Alle Platzhalter ersetzen: Kontakte, Proben, Besetzung, Repertoire, Vereinsgeschichte und Beiträge.
3. Impressum und Datenschutzerklärung mit tatsächlichen Vereins- und Hostingangaben vervollständigen und prüfen. Beide Seiten sind ausdrücklich Vorlagen, keine fertigen Rechtstexte.
4. `npm run build` ausführen und den Produktionsbuild auf Mobilgerät und Desktop prüfen.
5. `dist/` auf dem gewählten Hosting veröffentlichen. Eigene Fehlerseite `404.html` nutzen. Unterseiten benötigen übliche Verzeichnisindex-Unterstützung (`/kapelle/index.html`).

Der Quellcode kann über GitHub heruntergeladen werden. Die Website ist noch nicht auf einem öffentlichen Webhosting veröffentlicht.
