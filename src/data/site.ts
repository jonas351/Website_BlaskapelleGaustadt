// Alle Platzhalter vor der Veröffentlichung durch bestätigte Vereinsangaben ersetzen.
export const site = {
  name: 'Blaskapelle Gaustadt',
  instagram: 'https://www.instagram.com/bk.gaustadt/',
  instagramHandle: '@bk.gaustadt',
  email: '', // z. B. kontakt@eure-domain.de
  phone: '',
  rehearsalDay: '[Wochentag ergänzen]',
  rehearsalTime: '[Uhrzeit ergänzen]',
  rehearsalPlace: '[Probenraum und Adresse ergänzen]',
  legalName: '[Vollständiger Vereinsname und Rechtsform]',
  legalAddress: '[Straße, Hausnummer, PLZ und Ort]',
  representative: '[Vertretungsberechtigte Person(en)]',
  register: '[Registergericht und Registernummer, falls zutreffend]',
  responsible: '[Inhaltlich verantwortliche Person und Anschrift, falls erforderlich]',
};

export type Event = {
  title: string;
  date: string; // YYYY-MM-DD
  time: string; // z. B. 18:00
  place: string;
  description: string;
  url?: string; // Optionaler Link zur Veranstaltung oder zu Tickets
};
// Nur bestätigte Veranstaltungen eintragen. Keine erfundenen Termine anzeigen.
export const events: Event[] = [];

export type GalleryPhoto = { src: string; alt: string; caption: string; category: string };
// Eigene, zur Veröffentlichung freigegebene Bilder unter public/images/ ablegen.
export const gallery: GalleryPhoto[] = [];
