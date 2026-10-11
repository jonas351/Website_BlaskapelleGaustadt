#!/usr/bin/env python3
"""Generate native Elementor widgets; no page-sized HTML widget or Pro dependency."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'firebow-elementor' / 'templates'
BROWN, CREAM, COPPER, SAND, INK, MUTED = '#30251f', '#f8f4ed', '#a44720', '#eee5d8', '#30251f', '#6e5f54'
counter = 0

def uid():
    global counter
    counter += 1
    return hashlib.sha256(f'firebow-element-{counter}'.encode()).hexdigest()[:8]

def dimensions(top=0, right=None, bottom=None, left=None):
    right = top if right is None else right
    bottom = top if bottom is None else bottom
    left = right if left is None else left
    return {'unit':'px', 'top':str(top), 'right':str(right), 'bottom':str(bottom), 'left':str(left), 'isLinked': top == right == bottom == left}

def W(kind, settings=None, css='', title=''):
    settings = settings or {}
    settings['__globals__'] = {key: '' for key in ('typography_typography', 'title_color', 'text_color', 'background_color', 'button_text_color', 'title_typography_typography', 'content_typography_typography') if key in settings}
    if css: settings['_css_classes'] = css
    if title: settings['_title'] = title
    return {'id':uid(), 'elType':'widget', 'widgetType':kind, 'settings':settings, 'elements':[]}

def H(text, tag='h2', size=46, color=INK, css='', label=''):
    text = text.replace('\n', '<br>')
    return W('heading', {'title':text,'header_size':tag,'title_color':color,'typography_typography':'custom','typography_font_family':'Arial','typography_font_weight':'700','typography_font_size':{'unit':'px','size':size},'typography_font_size_tablet':{'unit':'px','size':min(size,54)},'typography_font_size_mobile':{'unit':'px','size':min(size,42 if tag == 'h1' else 32 if tag == 'h2' else size)},'typography_line_height':{'unit':'em','size':1.07},'typography_letter_spacing':{'unit':'px','size':-1.6 if size>28 else -0.5},'_margin':dimensions()}, css, label)

def E(text, color=MUTED, size=16, css=''):
    if not text.startswith('<'): text='<p>'+text+'</p>'
    return W('text-editor', {'editor':text,'text_color':color,'typography_typography':'custom','typography_font_family':'Arial','typography_font_size':{'unit':'px','size':size},'typography_line_height':{'unit':'em','size':1.7},'_margin':dimensions()}, css)

def eyebrow(text, color=MUTED): return H(text, 'p', 11, color, 'fb-eyebrow')
def link(slug, suffix=''): return '@@link:'+slug+'@@'+suffix
def B(text, target, bg=BROWN, color=CREAM, external=False):
    arrow = '↗' in text or '→' in text
    text = text.replace(' ↗','').replace(' →','')
    return W('button', {'text':text,'link':{'url':target,'is_external':external},'background_color':bg,'button_text_color':color,'typography_typography':'custom','typography_font_family':'Arial','typography_font_size':{'unit':'px','size':14},'typography_font_weight':'700','border_radius':dimensions(7),'text_padding':dimensions(15,23),'align':'left','_margin':dimensions(),'_element_width':'auto'}, 'fb-arrow-link' if arrow else '')

def C(children, direction='column', gap=22, bg=None, padding=0, width=100, boxed=False, css='', title='', **settings):
    defaults = {'content_width':'boxed' if boxed else 'full','flex_direction':direction,'flex_direction_mobile':'column','flex_gap':{'unit':'px','column':str(gap),'row':str(gap),'isLinked':True,'size':gap},'padding':padding if isinstance(padding,dict) else dimensions(padding),'padding_mobile':dimensions(0) if not boxed else dimensions(48,20),'width':{'unit':'%','size':width},'width_mobile':{'unit':'%','size':100},'flex_align_items':'stretch','css_classes':css,'_title':title}
    if boxed:
        defaults['boxed_width']={'unit':'px','size':1160}
        defaults['padding_tablet']=dimensions(65,35)
    if bg: defaults.update(background_background='classic', background_color=bg)
    if css in ('fb-service-card', 'fb-browser'): defaults['border_radius'] = dimensions(15)
    defaults.update(settings)
    return {'id':uid(),'elType':'container','isInner':False,'settings':defaults,'elements':children}

def section(children, bg=None, direction='column', gap=30, css='', **kwargs):
    padding = kwargs.pop('padding', dimensions(90,45))
    return C(children,direction,gap,bg,padding,boxed=True,css=css,**kwargs)

def row(children,gap=28,**kwargs): return C(children,'row',gap,**kwargs)
def col(children,width=100,**kwargs): return C(children,width=width,**kwargs)

def save(slug,title,content):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(slug+'.json')).write_text(json.dumps({'version':'0.4','title':title,'type':'section' if slug in ('header','footer') else 'page','page_settings':{},'content':content},ensure_ascii=False,indent=2)+'\n')

SERVICES = [
    ('websites','01','Websites & Onepager','Ein guter erster Eindruck. Ein klarer nächster Schritt.','Ein neuer Auftritt oder ein frischer Blick auf eure bestehende Website: Wir verbinden Gestaltung, verständliche Inhalte und einfache Bedienung.','website'),
    ('buchungssysteme','02','Buchungs- & Terminsysteme','Weniger Abstimmung. Mehr Zeit fürs Tagesgeschäft.','Wir prüfen, welche Buchungslösung zu euch passt, und binden sie in eure Website ein – für Dienstleister, Studios, Coaches und Praxen.','buchung'),
    ('formulare','03','Formulare & Kontakt','Aus Interesse wird eine konkrete Anfrage.','Kontakt, Rückfragen oder Bewerbungen: Wir gestalten Formulare, die verständlich sind und die benötigten Angaben strukturiert übermitteln.','formular'),
    ('sichtbarkeit','04','SEO & Google-Einträge','Damit man euch nicht nur sieht, sondern findet.','Mit sauberer Seitenstruktur, verständlichen Texten und einem passenden Google-Unternehmensprofil schaffen wir Grundlagen für eure Auffindbarkeit.','seo'),
]
FAQ = [
    ('Was kostet eine Website bei euch?','Das hängt davon ab, was ihr braucht: etwa einen Onepager, mehrere Unterseiten oder eine Terminbuchung. Nach einem Gespräch über Inhalte und Funktionen erstellen wir ein individuelles Angebot. Umfang und Kosten stimmen wir vor dem Start gemeinsam ab.'),
    ('Wie lange dauert die Umsetzung?','Der Zeitplan hängt vom Umfang und davon ab, wann Texte, Bilder und Rückmeldungen vorliegen. Wir besprechen die einzelnen Schritte vor Projektbeginn und legen einen realistischen Ablauf fest.'),
    ('Könnt ihr Buchungssysteme wie Doctolib oder Bookly einbauen?','Wir prüfen für euren konkreten Anbieter, welche Einbindung technisch möglich ist und welche Lizenz-, Datenschutz- und Vertragsbedingungen gelten. Nicht jedes System bietet dieselben Schnittstellen. Eine verbindliche Zusage gibt es nach dieser Prüfung.'),
    ('Kann ich Texte und Bilder später selbst ändern?','Ja, die neue FireBow-Website lässt sich mit WordPress und dem kostenlosen Elementor bearbeiten. Für Kundenprojekte stimmen wir ebenfalls ab, welche Inhalte ihr selbst pflegen möchtet, und richten die Bedienung entsprechend ein.'),
    ('Muss ich mich selbst um Updates und Pflege kümmern?','Das klären wir gemeinsam. Regelmäßige Updates, Sicherungen und technische Pflege müssen eingeplant werden. Ob ihr das selbst übernimmt oder eine Betreuung vereinbart, wird Teil der Projektabsprache; eine laufende Betreuung ist nicht automatisch enthalten.'),
    ('Was braucht ihr, bevor wir starten?','Hilfreich sind euer Angebot, eure Zielgruppe, das Logo sowie vorhandene Texte und Bilder. Wenn noch etwas fehlt, gehen wir die Inhalte gemeinsam durch. Auch die Frage, wer Hosting und Domain betreut, klären wir frühzeitig.'),
    ('Könnt ihr eine bestehende Website überarbeiten?','Ja. Wir schauen uns den vorhandenen Auftritt an und besprechen, welche Inhalte bleiben sollen und was sich verbessern lässt. Danach entscheiden wir gemeinsam zwischen gezielter Überarbeitung und einem neuen Aufbau.'),
    ('Wie gehen wir mit Datenschutz um?','Wir berücksichtigen Datenschutz bei technischen Entscheidungen, etwa bei Formularen, Schriften und externen Diensten. Welche Rechtstexte, Verträge oder Einwilligungen erforderlich sind, hängt vom tatsächlichen Betrieb ab. Eine individuelle rechtliche Prüfung wird dadurch nicht ersetzt.'),
]

def title(label, text, intro):
    return section([eyebrow(label,COPPER),H(text,'h1',64),E(intro,size=18)],SAND,gap=22,padding=dimensions(75,45),css='fb-page-title')

def buttonrow(primary='Projekt besprechen ↗',secondary='Leistungen entdecken'):
    return row([B(primary,link('kontakt'),COPPER,CREAM),B(secondary,link('leistungen'),SAND,INK)],gap=12,css='fb-buttons',flex_wrap='wrap',flex_direction_mobile='row')

def cta():
    return section([row([col([eyebrow('EUER NÄCHSTER SCHRITT','#e4b88a'),H('Eine Idee?\nLass uns darüber sprechen.','h2',43,CREAM),E('Ob neue Website oder eine konkrete Funktion: Erzählt uns, was euch im Alltag helfen würde.','#dfd1c3')],width=68),col([B('Projekt besprechen ↗',link('kontakt'),'#e8b27b',INK),E('Unverbindlich anfragen. Gemeinsam den Umfang klären.','#dfd1c3',13)],width=28,flex_justify_content='center')],gap=40)],BROWN,padding=dimensions(65,45),css='fb-cta')

def servicecard(service):
    slug,number,name,promise,description,topic=service
    return col([eyebrow(number+' / FIREBOW',COPPER),H(name,'h3',28),E(promise,INK,17),E(description),row([B('Mehr erfahren ↗',link(slug),BROWN,CREAM),E('Individuelles Angebot',MUTED,12)],gap=15,flex_wrap='wrap',flex_align_items='center',flex_direction_mobile='row')],width=48,bg='#fffcf7',padding=32,padding_mobile=dimensions(26,22),css='fb-service-card')

def services():
    return [row([servicecard(s) for s in SERVICES[:2]],gap=28),row([servicecard(s) for s in SERVICES[2:]],gap=28)]

def steps():
    return row([col([eyebrow('01 / VERSTEHEN',COPPER),H('Erst euer Alltag.','h3',27),E('Was soll die Website leisten? Wer nutzt sie? Und welche Aufgabe kostet euch heute unnötig Zeit?')],width=31,css='fb-step'),col([eyebrow('02 / GESTALTEN',COPPER),H('Dann die Lösung.','h3',27),E('Wir strukturieren Inhalte, gestalten den Auftritt und stimmen Funktionen und Bedienung mit euch ab.')],width=31,css='fb-step'),col([eyebrow('03 / ÜBERGEBEN',COPPER),H('Bereit für euch.','h3',27),E('Vor dem Start prüfen wir die vereinbarten Funktionen. Anschließend zeigen wir euch, wie ihr eure Inhalte selbst pflegt.')],width=31,css='fb-step')],gap=32)

def questions(entries, shared=False):
    return [W('firebow-faq', {'source':'shared' if shared else 'this','limit':len(entries) if shared else 0,'items':[{'_id':uid(),'question':q,'answer':'<p>'+a+'</p>'} for q,a in entries]}, title='Hier Fragen und Antworten bearbeiten')]

def main():
    save('header','Kopfbereich & Menü',[
        C([col([W('firebow-logo')],width=24,css='fb-header-brand'),col([W('firebow-navigation',{'items':[{'_id':uid(),'label':label,'link':{'url':link(slug)}} for slug,label in [('startseite','Start'),('leistungen','Leistungen'),('ueber-uns','Über uns'),('faq','FAQ'),('kontakt','Projekt besprechen')]]})],width=76,flex_align_items='flex-end',flex_justify_content='center',css='fb-header-nav')],direction='row',gap=0,boxed=True,bg=CREAM,padding=dimensions(23,45),padding_tablet=dimensions(20,30),padding_mobile=dimensions(20),flex_direction_mobile='row',flex_align_items='center',css='fb-header-row')
    ])
    save('footer','Fußbereich',[
        section([row([col([W('firebow-logo'),E('Digitale Lösungen mit Präzision.<br>Persönlich gedacht. Für euren Alltag gemacht.')],width=40),col([eyebrow('ENTDECKEN'),E(''.join(f'<p><a href="{link(s)}">{n}</a></p>' for s,n in [('leistungen','Leistungen'),('ueber-uns','Jonas & Benedikt'),('faq','Fragen & Antworten')]))],width=23),col([eyebrow('LASST UNS SPRECHEN'),E('[firebow_email]'),B('Kontakt aufnehmen ↗',link('kontakt'),BROWN,CREAM)],width=33)],gap=30),row([E('FireBow · Jonas & Benedikt',size=12),E(f'<p><a href="{link("impressum")}">Impressum</a> · <a href="{link("datenschutz")}">Datenschutz</a></p>',size=12)],gap=30,css='fb-footer-bottom',flex_justify_content='space-between')],SAND,gap=45,padding=dimensions(60,45))
    ])
    browser = col([
        row([E('● ● ●',COPPER,12),E('GESTALTUNGSBEISPIEL',MUTED,10)],gap=15,padding=dimensions(14,22),bg='#e9dfd1',flex_direction_mobile='row',flex_justify_content='space-between',css='fb-browser-top'),
        col([eyebrow('EUER UNTERNEHMEN',COPPER),H('Ein klarer Auftritt.\nEin gutes Gefühl.','h3',32),E('Hier finden eure Kunden, was sie suchen.'),B('Termin entdecken ↗',link('buchungssysteme'),COPPER,CREAM),row([col([eyebrow('EINFACH'),E('Anfragen')],width=48,bg=SAND,padding=18,padding_mobile=dimensions(18)),col([eyebrow('ÜBERSICHTLICH'),E('Buchen')],width=48,bg=SAND,padding=18,padding_mobile=dimensions(18))],gap=12,flex_direction_mobile='row')],padding=32,padding_mobile=dimensions(25),gap=22)
    ],width=45,bg='#fffcf7',gap=0,css='fb-browser')
    save('startseite','Startseite',[
        section([col([eyebrow('FIREBOW / WEBDESIGN & DIGITALE LÖSUNGEN',COPPER),H('Websites, die euch\n<em>Arbeit abnehmen.</em>','h1',68),E('Ein Auftritt, der zu euch passt. Und Funktionen, die euren Alltag leichter machen – von der ersten Anfrage bis zum gebuchten Termin.',size=18),buttonrow(),E('Persönlich begleitet von Jonas & Benedikt.',MUTED,13)],width=51,gap=25,flex_justify_content='center'),browser],CREAM,direction='row',gap=48,padding=dimensions(65,45),css='fb-hero'),
        section([E('01 / KLARER AUFTRITT',INK,12),E('02 / DURCHDACHTE FUNKTIONEN',INK,12),E('03 / PERSÖNLICHER KONTAKT',INK,12)],SAND,direction='row',gap=30,padding=dimensions(23,45),padding_mobile=dimensions(22),css='fb-value-strip',flex_justify_content='space-between'),
        section([row([col([eyebrow('WAS WIR FÜR EUCH TUN',COPPER),H('Digital darf sich\neinfach anfühlen.')],width=53),col([E('Vier Bausteine, ein Ziel: Euer Unternehmen bekommt einen verständlichen Auftritt und passende digitale Abläufe.')],width=43,flex_justify_content='center')],gap=35),*services()],gap=28),
        section([col([W('firebow-teamphoto')],width=47),col([eyebrow('DIE MENSCHEN HINTER FIREBOW',COPPER),H('Zwei Perspektiven.\nEin gemeinsames Ziel.'),E('Wir sind Jonas und Benedikt. Wir verbinden Wissen aus der Wirtschaftsinformatik mit Erfahrung aus dem unternehmerischen Alltag.'),E('Wir möchten zuerst verstehen, was ihr braucht. Dann entwickeln wir gemeinsam einen Auftritt, der zu eurem Unternehmen und euren Kunden passt.'),B('Lernt uns kennen ↗',link('ueber-uns'),BROWN,CREAM)],width=47,flex_justify_content='center')],SAND,direction='row',gap=65,css='fb-team-section'),
        section([eyebrow('VON DER IDEE ZUM START',COPPER),H('Ein guter Plan.\nEin persönlicher Draht.'),steps()],gap=35),
        section([row([col([eyebrow('GUT ZU WISSEN',COPPER),H('Noch Fragen?'),E('Hier sind die ersten Antworten. Alles Weitere besprechen wir gemeinsam.'),B('Alle Fragen & Antworten ↗',link('faq'),BROWN,CREAM)],width=35),col(questions(FAQ[:3],True),width=61,gap=0)],gap=45)],SAND),cta()
    ])
    save('leistungen','Leistungen',[
        title('UNSERE LEISTUNGEN','Die passende Lösung\nfür euren Alltag.','Eine Website muss mehr können als gut aussehen. Wir verbinden euren Auftritt mit den Funktionen, die ihr wirklich braucht.'),
        section([eyebrow('VIER BAUSTEINE / INDIVIDUELL KOMBINIERBAR',COPPER),*services()],gap=28),
        section([eyebrow('KEINE LÖSUNG VON DER STANGE',COPPER),H('Was braucht ihr wirklich?'),E('Nicht jedes Projekt braucht jede Funktion. Wir schauen gemeinsam auf eure Ziele und wählen einen passenden Umfang – vom kompakten Onepager bis zum Auftritt mit mehreren Unterseiten und Buchungssystem.'),steps()],SAND,gap=32),cta()
    ])
    details = {
        'websites': ('Ein Auftritt, der\nzu euch passt.','Ein Onepager für den schnellen Überblick oder eine Website mit mehreren Unterseiten: Wir strukturieren eure Inhalte so, dass Besucher sich zurechtfinden.',[
            ('Verständliche Struktur','Angebot, Ansprechpartner und nächster Schritt: Wichtige Informationen bekommen ihren Platz und eine klare Reihenfolge.'),('Gestaltung mit Charakter','Farben, Bilder und Typografie greifen eure Marke auf. Der Auftritt soll zu eurem Unternehmen passen und sich auf kleinen und großen Bildschirmen gut bedienen lassen.'),('Inhalte selbst pflegen','Wir stimmen ab, welche Texte und Bilder ihr selbst ändern möchtet. Bedienung und Übergabe werden darauf ausgerichtet.')],
            ['Welche Zielgruppe möchtet ihr erreichen?','Welche Inhalte und Funktionen sollen bleiben oder neu dazukommen?','Gibt es bereits Domain, Hosting, Logo und Fotos?']),
        'buchungssysteme': ('Termine buchen.\nAbstimmung reduzieren.','Menschen möchten Termine oft dann vereinbaren, wenn euer Telefon gerade nicht besetzt ist. Eine passende Onlinebuchung kann diesen Weg vereinfachen.',[
            ('Das passende System','Wir prüfen Anforderungen wie Leistungen, Mitarbeiter, Kalender und Erinnerungen, bevor wir einen Anbieter auswählen.'),('In eure Website integriert','Je nach System sind ein Buchungslink, eine eingebettete Ansicht oder eine weitergehende Anbindung möglich. Die konkrete Umsetzung prüfen wir mit dem Anbieter.'),('Kosten und Daten im Blick','Lizenzen, laufende Anbietergebühren und die Verarbeitung von Kundendaten gehören zur Entscheidung. Wir stimmen diese Punkte vor der Umsetzung ab.')],
            ['Welche Termine oder Leistungen sollen buchbar sein?','Welchen Kalender oder Anbieter verwendet ihr bisher?','Welche Bestätigungen und Erinnerungen werden benötigt?']),
        'formulare': ('Einfach fragen.\nStrukturiert ankommen.','Ein Kontaktformular sollte sich angenehm ausfüllen lassen und genau die Informationen abfragen, die ihr für eine gute Rückmeldung braucht.',[
            ('Klare Fragen und Felder','Wir unterscheiden notwendige und optionale Angaben und gestalten Formulare für den jeweiligen Anlass.'),('Nachrichten zuverlässig verarbeiten','Empfänger, Absenderkonfiguration und Versand werden eingerichtet und getestet. Ein erfolgreicher Techniktest allein bestätigt noch keine tatsächliche Postfachzustellung.'),('Datensparsam planen','Wir vermeiden unnötige Angaben und stimmen Speicherort, Aufbewahrung und verwendete Dienstleister mit euch ab. Besondere Daten benötigen eine gesonderte Prüfung.')],
            ['Welche Informationen braucht ihr für die erste Rückmeldung?','Wer soll die Anfragen erhalten und bearbeiten?','Soll etwas nur per E-Mail übermittelt oder auch gespeichert werden?']),
        'sichtbarkeit': ('Eine gute Grundlage.\nBesser gefunden werden.','Ein klar aufgebauter Webauftritt hilft Menschen und Suchmaschinen, euer Angebot zu verstehen. Wir kümmern uns um die Grundlagen und besprechen die lokale Auffindbarkeit.',[
            ('Saubere Seitenstruktur','Verständliche Überschriften, passende Seitentitel und nachvollziehbare interne Links geben euren Inhalten Orientierung.'),('Lokale Informationen','Wir prüfen Angaben wie Standort, Angebot und Erreichbarkeit. Ein Google-Unternehmensprofil kann ergänzt oder gepflegt werden, sofern euer Unternehmen dafür berechtigt ist.'),('Realistische Erwartungen','Suchplatzierungen hängen von vielen Faktoren ab. Wir versprechen keine feste Position und klären, welche Maßnahmen zum Umfang gehören.')],
            ['Welche Leistungen und welchen Einzugsbereich habt ihr?','Gibt es bereits ein Google-Unternehmensprofil?','Welche bestehenden Inhalte sollen überarbeitet werden?']),
    }
    for slug,number,name,promise,description,topic in SERVICES:
        headline,intro,features,checklist=details[slug]
        save(slug,name,[
            title('LEISTUNGEN / '+name.upper(),headline,intro),
            section([eyebrow('SO GEHEN WIR ES AN',COPPER),H(promise),row([col([eyebrow(f'0{i+1}',COPPER),H(label,'h3',27),E(text)],width=31,css='fb-step') for i,(label,text) in enumerate(features)],gap=30)],gap=35),
            section([col([eyebrow('FÜR UNSER ERSTES GESPRÄCH',COPPER),H('Drei Fragen\nzum Start.'),E('Damit wir eine Lösung vorschlagen können, die zu euch passt.')],width=43),col([E('<p><strong>'+f'0{i+1} · '+question+'</strong></p>',INK,18) for i,question in enumerate(checklist)],width=53,gap=27,css='fb-checklist')],SAND,direction='row',gap=45),
            section([H('Den passenden Umfang finden.','h2',38),E('Preis auf Anfrage. Wir besprechen Anforderungen und erstellen ein individuelles Angebot. Lizenzen und laufende Kosten externer Anbieter werden dabei gesondert geklärt.'),B(name+' anfragen ↗',link('kontakt','?anliegen='+topic),COPPER,CREAM),E(f'<p><a href="{link("leistungen")}">← Alle Leistungen</a></p>',size=14)],gap=24),cta()
        ])
    save('ueber-uns','Über uns',[
        title('JONAS & BENEDIKT','Technik verstehen.\nUnternehmen verstehen.','Hinter FireBow stehen zwei Menschen mit unterschiedlichen Hintergründen und einem gemeinsamen Ziel: Unternehmen digital zu entlasten.'),
        section([col([W('firebow-teamphoto')],width=48),col([eyebrow('PERSÖNLICH STATT ANONYM',COPPER),H('Lernt uns kennen.'),E('Jonas bringt seine Perspektive aus dem Studium der Wirtschaftsinformatik ein. Benedikt kennt als Leiter eines eigenen EDEKA-Marktes die Fragen und Herausforderungen aus dem unternehmerischen Alltag.'),E('Diese Verbindung prägt unsere Arbeit: Wir schauen auf Gestaltung und Technik – und ebenso darauf, ob eine Lösung im täglichen Betrieb hilfreich ist.')],width=46,flex_justify_content='center')],direction='row',gap=65),
        section([row([col([eyebrow('TECHNIK & GESTALTUNG',COPPER),H('Jonas','h2',39),E('Wirtschaftsinformatik-Student. Beschäftigt sich mit digitalen Abläufen und der Frage, wie aus einer Idee ein verständlicher, funktionierender Webauftritt wird.')],width=48,bg='#fffcf7',padding=32,padding_mobile=dimensions(25),css='fb-service-card'),col([eyebrow('UNTERNEHMERISCHE PERSPEKTIVE',COPPER),H('Benedikt','h2',39),E('Leiter eines eigenen EDEKA-Marktes. Bringt Erfahrungen aus dem Geschäftsalltag ein und den Blick darauf, was Unternehmen und ihre Kunden wirklich brauchen.')],width=48,bg='#fffcf7',padding=32,padding_mobile=dimensions(25),css='fb-service-card')],gap=28)],SAND),
        section([eyebrow('WAS UNS WICHTIG IST',COPPER),H('Eine Lösung muss\nim Alltag funktionieren.'),steps()],gap=35),cta()
    ])
    save('faq','Fragen & Antworten',[
        title('FRAGEN & ANTWORTEN','Gut zu wissen.\nEinfach erklärt.','Hier findet ihr Antworten auf die häufigsten Fragen rund um Zusammenarbeit, Technik und Pflege.'),
        section([col(questions(FAQ),gap=0,css='fb-faq-list')],padding=dimensions(65,45)),cta()
    ])
    save('kontakt','Kontakt',[
        title('KONTAKT','Erzählt uns,\nwas ihr vorhabt.','Eine neue Website, eine Terminbuchung oder erst einmal eine Frage? Jonas und Benedikt freuen sich auf eure Nachricht.'),
        section([col([eyebrow('EIN DIREKTER DRAHT',COPPER),H('Der erste Schritt\nist ein Hallo.','h2',39),E('Beschreibt kurz euer Unternehmen und eure Idee. Was soll leichter werden? Was fehlt euch heute? Gemeinsam klären wir den nächsten Schritt.'),eyebrow('E-MAIL'),E('[firebow_email]',INK),H('So geht es danach weiter.','h3',26),E('Wir lesen eure Anfrage, klären offene Fragen und besprechen mit euch den passenden Umfang. Es wird erst beauftragt, wenn Angebot und Vorgehen abgestimmt sind.')],width=37),col([H('Was können wir für euch tun?','h2',30),W('firebow-inquiry',{'email':'jonas.bogensperger@firebow.net','privacy_link':{'url':link('datenschutz')}},title='Kontaktadresse und Formular')],width=57,bg='#fffcf7',padding=35,padding_mobile=dimensions(25,20),css='fb-service-card')],direction='row',gap=60)
    ])
    save('impressum','Impressum',[
        title('RECHTLICHES','Impressum','Angaben zum Betreiber dieser Website.'),
        section([E('<p><strong>Entwurf – vor Veröffentlichung vervollständigen und prüfen.</strong></p>',COPPER),H('Anbieter','h2',28),E('FireBow<br>[Vollständiger Name bzw. Firmenname und Rechtsform]<br>[Straße, Hausnummer]<br>[Postleitzahl, Ort]'),H('Kontakt','h2',28),E('[firebow_email]<br>[Weitere unmittelbare Kontaktmöglichkeit]'),H('Vertretung und Register','h2',28),E('[Vertretungsberechtigte Personen, soweit erforderlich]<br>[Registergericht und Registernummer, soweit zutreffend]<br>[Umsatzsteuer-Identifikationsnummer, soweit vorhanden]'),H('Weitere Angaben','h2',28),E('[Weitere für das konkrete Unternehmen erforderliche Pflichtangaben ergänzen, einschließlich ggf. berufsrechtlicher Angaben und Angaben zur Verbraucherschlichtung.]'),H('Bildnachweise','h2',28),E('[Nutzungsrechte und erforderliche Urheberangaben für Logo, Teamfoto und später ergänzte Bilder prüfen.]')],css='fb-legal',gap=24)
    ])
    save('datenschutz','Datenschutz',[
        title('RECHTLICHES','Datenschutz','Informationen zur Verarbeitung personenbezogener Daten.'),
        section([E('<p><strong>Bearbeitbare Vorlage – keine fertige Datenschutzerklärung. Vor Veröffentlichung an den tatsächlichen Betrieb anpassen und prüfen lassen.</strong></p>',COPPER),H('Verantwortlicher','h2',28),E('[Betreiber/Firmenname und vollständige Anschrift]<br>[firebow_email]<br>[Weitere Datenschutz-Kontaktangaben, soweit zutreffend]'),H('Hosting und Serverprotokolle','h2',28),E('[Hosting-Anbieter, Standort, Auftragsverarbeitung, tatsächlich protokollierte Daten, Zwecke, Rechtsgrundlagen und Aufbewahrungsdauer ergänzen. Die Angaben können aus einem Screenshot nicht ermittelt werden.]'),H('Kontakt per E-Mail und Formular','h2',28),E('Das Formular fragt eine E-Mail-Adresse, ein Anliegen und eine Nachricht ab. Der Name ist optional. Die Angaben werden über WordPress an die konfigurierte Kontaktadresse zum Versand übergeben. Dieses Theme legt keine zusätzliche Nachrichtendatenbank an. Mailserver, Postfach und zusätzlich installierte Plugins können weitere Kopien oder Protokolle erzeugen.<br>[Verwendeten Mail-/SMTP-Anbieter, Empfänger, Zwecke, zutreffende Rechtsgrundlagen, Aufbewahrung und Löschung ergänzen.]'),H('Schutz vor Missbrauch','h2',28),E('Das Theme verwendet ein verstecktes Prüffeld und eine kurzlebige Begrenzung von Versandversuchen. Hierfür wird ein mit einem geheimen Schlüssel erzeugter Hash der serverseitig erkannten Netzwerkadresse gezählt. Der Zähler wird für eine Stunde gespeichert; der Nachrichtentext wird dort nicht gespeichert. In Hosting-Umgebungen mit einem gemeinsamen Proxy ist die Konfiguration gesondert zu prüfen.<br>[Zweck, zutreffende Rechtsgrundlage und tatsächliche Hosting-Konfiguration ergänzen.]'),H('Schriften, Cookies und weitere Dienste','h2',28),E('Der mitgelieferte Entwurf verwendet Systemschriften und bindet keine Analyse-, Karten- oder Videodienste von Drittanbietern ein. Beim Aufruf ohne Anmeldung setzt das Theme selbst keine Cookies. WordPress, Plugins oder später ergänzte Dienste können das ändern.<br>[Tatsächlich verwendete Cookies, Dienste, Rechtsgrundlagen, Empfänger, eventuelle Drittlandübermittlungen und erforderliche Einwilligungen prüfen und beschreiben.]'),H('Rechte betroffener Personen','h2',28),E('[Informationen zu Auskunft, Berichtigung, Löschung, Einschränkung, Datenübertragbarkeit, Widerspruch und ggf. Widerruf einer Einwilligung entsprechend den gesetzlichen Voraussetzungen ergänzen.]'),H('Beschwerdemöglichkeit','h2',28),E('[Zuständige Datenschutzaufsichtsbehörde und Beschwerderecht ergänzen.]')],css='fb-legal',gap=24)
    ])

if __name__ == '__main__':
    main()
