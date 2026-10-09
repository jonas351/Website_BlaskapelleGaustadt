#!/usr/bin/env python3
"""Generate native Elementor widgets; no page-sized HTML widget or Pro dependency."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'gaustadt-elementor' / 'templates'
GREEN, CREAM, GOLD, PAPER, INK, MUTED = '#183c34', '#faf8f1', '#dbc18a', '#f0eee4', '#233c33', '#65716a'
counter = 0

def uid():
    global counter
    counter += 1
    return hashlib.sha256(f'gaustadt-element-{counter}'.encode()).hexdigest()[:8]

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

def H(text, tag='h2', size=42, color=INK, css='', label=''):
    small = tag == 'p'
    return W('heading', {'title':text,'header_size':tag,'title_color':color,'typography_typography':'custom','typography_font_family':'Arial' if small else 'Gaustadt Serif','typography_font_weight':'700' if small else '400','typography_font_size':{'unit':'px','size':size},'typography_font_size_tablet':{'unit':'px','size':min(size,48)},'typography_font_size_mobile':{'unit':'px','size':min(size,40 if tag == 'h1' else 32 if tag == 'h2' else size)},'typography_line_height':{'unit':'em','size':1.15},'_margin':dimensions()}, css, label)

def E(text, color=MUTED, size=14, css=''):
    if not text.startswith('<'): text='<p>'+text+'</p>'
    return W('text-editor', {'editor':text,'text_color':color,'typography_typography':'custom','typography_font_family':'Arial','typography_font_size':{'unit':'px','size':size},'typography_line_height':{'unit':'em','size':1.8},'_margin':dimensions()}, css)

def eyebrow(text, color=MUTED): return H(text, 'p', 10, color, 'bg-eyebrow')
def link(slug, suffix=''): return '@@link:'+slug+'@@'+suffix
def B(text, target, bg=GREEN, color=CREAM, external=False):
    return W('button', {'text':text,'link':{'url':target,'is_external':external},'background_color':bg,'button_text_color':color,'typography_typography':'custom','typography_font_family':'Arial','typography_font_size':{'unit':'px','size':12},'typography_font_weight':'600','border_radius':dimensions(3),'text_padding':dimensions(15,23),'align':'left','_margin':dimensions(),'_element_width':'auto'})

def I(asset, css=''):
    return W('image', {'image':{'bg_asset':asset},'image_size':'full','align':'center','width':{'unit':'%','size':100},'_margin':dimensions()}, css)

def C(children, direction='column', gap=22, bg=None, padding=0, width=100, boxed=False, css='', title='', **settings):
    defaults = {'content_width':'boxed' if boxed else 'full','flex_direction':direction,'flex_direction_mobile':'column','flex_gap':{'unit':'px','column':str(gap),'row':str(gap),'isLinked':True,'size':gap},'padding':padding if isinstance(padding,dict) else dimensions(padding),'padding_mobile':dimensions(0) if not boxed else dimensions(48,20),'width':{'unit':'%','size':width},'width_mobile':{'unit':'%','size':100},'flex_align_items':'stretch','_css_classes':css,'_title':title}
    if boxed:
        defaults['boxed_width']={'unit':'px','size':1240}
        defaults['padding_tablet']=dimensions(65,35)
    if bg: defaults.update(background_background='classic', background_color=bg)
    defaults.update(settings)
    return {'id':uid(),'elType':'container','isInner':False,'settings':defaults,'elements':children}

def section(children, bg=None, direction='column', gap=30, css='', **kwargs):
    padding = kwargs.pop('padding', dimensions(85,50))
    return C(children,direction,gap,bg,padding,boxed=True,css=css,**kwargs)

def row(children,gap=28,**kwargs): return C(children,'row',gap,**kwargs)
def col(children,width=100,**kwargs): return C(children,width=width,**kwargs)

def heading(label,title,text):
    return section([eyebrow(label),H(title,'h1',56),E(text)],PAPER,css='bg-section-title',gap=22,padding=dimensions(70,50),padding_mobile=dimensions(48,20))

def join(title='Zusammen klingt’s besser.',text='Du spielst ein Instrument oder möchtest anfangen? Lass uns ins Gespräch kommen.',button='Mitmachen →',target=None):
    return section([row([col([eyebrow('DEIN PLATZ IN DER KAPELLE',GOLD),H(title,'h2',36,CREAM),E(text,'#c1cdbc',13)],width=72),col([B(button,target or link('mitmachen'),CREAM,GREEN)],width=25,flex_justify_content='center')],gap=25)],GREEN,padding=dimensions(48,50),padding_mobile=dimensions(40,25))

def info(title,text,note=None):
    children=[H(title,'h3',26)]
    if note: children.append(E(note,'#7c6342',13,'bg-placeholder'))
    children.append(E(text))
    return col(children,width=31,bg=CREAM,padding=30,padding_mobile=dimensions(25),css='bg-card')

def save(slug,title,content):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(slug+'.json')).write_text(json.dumps({'version':'0.4','title':title,'type':'section' if slug in ('header','footer') else 'page','page_settings':{},'content':content},ensure_ascii=False,indent=2)+'\n')

def main():
    save('header','Kopfbereich & Menü',[
        C([row([E('BLASMUSIK AUS GAUSTADT. MIT HERZ.','#d7dccb',9),E('<p><a href="https://www.instagram.com/bk.gaustadt/" target="_blank" rel="noopener noreferrer">Instagram · @bk.gaustadt ↗</a></p>','#d7dccb',9)],gap=20)],bg='#123129',boxed=True,padding=dimensions(8,50),padding_tablet=dimensions(8,35),padding_mobile=dimensions(8,20)),
        C([col([row([W('heading',{'title':'bg','header_size':'p','title_color':GREEN,'typography_typography':'custom','typography_font_family':'Gaustadt Serif','typography_font_size':{'unit':'px','size':27},'_element_width':'auto'},'bg-roundmark'),H('<small>BLASKAPELLE</small>GAUSTADT','h3',23,GREEN,'bg-brand')],gap=13,flex_align_items='center',flex_direction_mobile='row')],width=30,width_mobile={'unit':'%','size':80}),col([W('gaustadt-navigation',{'items':[{'_id':uid(),'label':label,'link':{'url':link(slug)}} for slug,label in [('startseite','Startseite'),('kapelle','Die Kapelle'),('termine','Termine'),('galerie','Galerie'),('mitmachen','Mitmachen'),('kontakt','Kontakt')]]})],width=70,flex_justify_content='center',flex_align_items='flex-end',width_mobile={'unit':'%','size':20})],direction='row',gap=0,bg=CREAM,boxed=True,padding=dimensions(23,50),padding_tablet=dimensions(20,35),padding_mobile=dimensions(18,20),flex_direction_mobile='row',flex_align_items='center',title='Logo & Navigation')
    ])
    footer_columns=[]
    for title,links in [('Entdecken',[('kapelle','Die Kapelle'),('termine','Termine & Auftritte'),('galerie','Bilder & Eindrücke')]),('Zusammenkommen',[('mitmachen','Mitmachen'),('kontakt','Auftritt anfragen'),('kontakt','Kontakt')])]:
        footer_columns.append(col([eyebrow(title),E(''.join(f'<p><a href="{link(slug)}">{label}</a></p>' for slug,label in links),size=12)],width=21,css='bg-footer-links'))
    save('footer','Fußbereich',[
        section([row([col([H('<small>BLASKAPELLE</small>GAUSTADT','h3',23,GREEN,'bg-brand'),E('Heimat im Herzen.<br>Musik im Blut.')],width=25),*footer_columns,col([eyebrow('Immer in Verbindung'),E('Neuigkeiten und kleine Einblicke gibt’s auch auf Instagram.'),B('@bk.gaustadt ↗','https://www.instagram.com/bk.gaustadt/',GREEN,CREAM,True)],width=27)],gap=25),row([E('Blaskapelle Gaustadt',size=10),E(f'<p><a href="{link("impressum")}">Impressum</a> · <a href="{link("datenschutz")}">Datenschutz</a></p>',size=10),E('Mit ♡ für Gaustadt.',size=10)],gap=20)],'#eeeee3',padding=dimensions(55,50),padding_mobile=dimensions(40,20))
    ])
    save('startseite','Startseite',[
        section([col([eyebrow('WIR SIND DIE BLASKAPELLE GAUSTADT',GOLD),H('Heimat im Herzen.<br><em style="color:#dbc18a">Musik im Blut.</em>','h1',68,CREAM),E('Wenn aus vielen Tönen ein Miteinander wird.<br>Entdecke unsere Kapelle und die Freude an der Blasmusik.','#ccd4c9'),row([B('Unsere Kapelle →',link('kapelle'),GOLD,GREEN),B('Live erleben ↗',link('termine'),GREEN,CREAM)],gap=25),E('DAHEIM IN GAUSTADT · BAMBERG','#bbc8b7',10)],width=55,flex_justify_content='center'),col([I('brass','bg-art')],width=45,flex_justify_content='center')],GREEN,'row',gap=0,padding=dimensions(35,50),padding_mobile=dimensions(45,20),title='Start: Heimat & Musik'),
        section([E('♫ Musik, die Freude macht'),E('♡ Gemeinschaft, die bleibt'),E('⌖ Verwurzelt in Gaustadt')],PAPER,'row',gap=25,padding=dimensions(22,50),padding_mobile=dimensions(20),flex_direction_mobile='column'),
        section([col([I('together')],width=46),col([eyebrow('DIE MENSCHEN HINTER DER MUSIK'),H('Mehr als Musik.<br>Ein Stück Zuhause.'),E('Blasmusik lebt von den Menschen, die sie machen. Von der Freude am Zusammenspielen und von Momenten, die man miteinander teilt.'),E('Wir möchten dir zeigen, wer hinter der Blaskapelle Gaustadt steckt. Lerne uns kennen – oder finde selbst deinen Platz in der Kapelle.'),B('Mehr über uns →',link('kapelle'))],width=46,flex_justify_content='center')],direction='row',gap=80,_element_id='kennenlernen'),
        section([eyebrow('SEHEN. HÖREN. DABEI SEIN.'),H('Wir sehen uns vor der Bühne.'),W('gaustadt-events',{'source':'shared','single':'yes','empty_title':'Die nächsten Auftritte folgen.','empty_text':'Sobald Termine bestätigt sind, findest du sie hier. Bis dahin gibt’s Neuigkeiten auf Instagram.'}),B('Alle Termine →',link('termine'))],PAPER,padding=dimensions(65,50)),
        section([eyebrow('NOCH EIN BISSCHEN NÄHER DRAN'),H('Entdecke unsere Welt.'),row([
            col([I('illustration-1'),eyebrow('BILDER & EINDRÜCKE'),H('Ein Blick ins Kapellenleben.','h3',25),E('Unsere Bildergalerie und aktuelle Einblicke.'),B('Zur Galerie ↗',link('galerie'))],width=31,padding=22,padding_mobile=dimensions(22),css='bg-card'),
            col([I('illustration-2'),eyebrow('MITMACHEN'),H('Spiel mit. Sei dabei.','h3',25),E('Ein Instrument, viele Möglichkeiten, ein Miteinander.'),B('Mitmachen ↗',link('mitmachen'))],width=31,padding=22,padding_mobile=dimensions(22),css='bg-card'),
            col([I('illustration-3'),eyebrow('AUFTRITT ANFRAGEN'),H('Ihr feiert. Wir spielen?','h3',25),E('Erzählt uns von eurer Veranstaltung.'),B('Auftritt anfragen ↗',link('kontakt','?anliegen=auftritt'))],width=31,padding=22,padding_mobile=dimensions(22),css='bg-card')
        ],gap=25)]),join()
    ])
    save('kapelle','Die Kapelle',[
        heading('DIE KAPELLE','Viele Persönlichkeiten. Ein gemeinsamer Klang.','Musik verbindet. Hier lernst du die Menschen, die Geschichten und das Miteinander hinter der Blaskapelle Gaustadt kennen.'),
        section([col([I('brass','bg-art')],width=46,bg=GREEN),col([eyebrow('DAS MACHT UNS AUS'),H('Mit Herz dabei.<br>Mit Freude zusammen.'),E('Jedes Instrument bringt seine eigene Stimme mit. Erst zusammen entsteht der Klang einer Kapelle – und genau dieses Miteinander macht Blasmusik so besonders.'),E('Unsere Website gibt dir einen Einblick in die Blaskapelle Gaustadt. Du möchtest uns persönlich kennenlernen? Dann melde dich bei uns.'),B('Ins Gespräch kommen →',link('kontakt'))],width=46,flex_justify_content='center')],direction='row',gap=70),
        section([eyebrow('MUSIK & MENSCHEN'),H('Unsere Kapelle stellt sich vor.'),row([info('Unsere Musik','Hier ist Platz für die Musik, die euch begeistert – und für das, was euer Publikum bei einem Auftritt erwartet.','[Repertoire und musikalische Schwerpunkte ergänzen]'),info('Unsere Menschen','Stellt die Menschen vor, die eure Kapelle gestalten. Gerne mit Namen, Aufgaben und eigenen Bildern.','[Musikalische Leitung, Vorstand und Mitglieder ergänzen]'),info('Unsere Geschichte','Von den Anfängen bis heute: Hier finden die wichtigen Momente eurer Vereinsgeschichte ihren Platz.','[Gründungsjahr und Vereinsgeschichte ergänzen]')])],PAPER),join()
    ])
    save('termine','Termine & Auftritte',[
        heading('TERMINE & AUFTRITTE','Musik erlebt man am besten zusammen.','Ob vor der Bühne oder mittendrin: Hier findest du unsere kommenden Auftritte und alle Infos zum Dabeisein.'),
        section([H('Die nächsten Termine'),W('gaustadt-events',{'source':'this','events':[],'show_past':'yes','empty_title':'Hier ist bald Musik drin.','empty_text':'Unsere nächsten bestätigten Auftritte werden hier veröffentlicht. Schau wieder vorbei oder folge uns auf Instagram.'},title='Hier Termine eintragen')]),
        join('Ihr plant ein Fest?','Erzählt uns von eurer Veranstaltung. Wir besprechen gemeinsam, was möglich ist.','Auftritt anfragen →',link('kontakt','?anliegen=auftritt'))
    ])
    save('galerie','Bilder & Eindrücke',[
        heading('BILDER & EINDRÜCKE','Momente, die nachklingen.','Auf der Bühne, hinter den Kulissen und miteinander. Hier ist Platz für die kleinen und großen Momente aus unserem Kapellenleben.'),
        section([W('image-gallery',{'wp_gallery':[{'bg_asset':f'illustration-{i}'} for i in (1,2,3)],'gallery_columns':3,'thumbnail_size':'large','gallery_link':'file','open_lightbox':'yes','gallery_display_caption':'','image_spacing':'custom','image_spacing_custom':{'unit':'px','size':20}},'bg-gallery',title='Bilder auswählen und ersetzen'),E('Unsere Fotogalerie entsteht hier. Diese Bilder sind Illustrationen – echte Vereinsfotos folgen. Bis dahin findest du aktuelle Einblicke auf Instagram.')]),
        join('Kapellenleben zum Mitnehmen.','Direkt von uns. Auf Instagram: @bk.gaustadt','Zum Instagram-Profil ↗','https://www.instagram.com/bk.gaustadt/')
    ])
    faqs=[('Ich habe noch nie ein Instrument gespielt. Kann ich mich trotzdem melden?','Ja, melde dich gerne mit deinen Fragen. Welche Lern- und Einstiegsmöglichkeiten es gibt, besprechen wir persönlich. Ein konkretes Unterrichtsangebot ist hier noch nicht bestätigt.'),('Ich habe länger nicht gespielt. Ist ein Wiedereinstieg möglich?','Erzähl uns von deinem Instrument und deiner bisherigen Erfahrung. Gemeinsam klären wir, welcher Einstieg sinnvoll ist.'),('Welche Instrumente werden gesucht?','[Gesuchte Instrumente und aktuelle Besetzung ergänzen]<br>Du kannst uns unabhängig davon schreiben und dein Instrument nennen.'),('Gibt es einen Mitgliedsbeitrag?','[Mitgliedsbeitrag und Aufnahmebedingungen ergänzen]<br>Die aktuellen Bedingungen erfährst du direkt von der Kapelle.'),('Kann ich die Kapelle auch ohne mitzuspielen unterstützen?','Wenn du uns unterstützen möchtest, melde dich bei uns. Wir klären gemeinsam, welche Möglichkeiten es gibt.')]
    save('mitmachen','Mitmachen',[
        heading('MITMACHEN','Dein Ton fehlt noch.','Du spielst ein Instrument, möchtest wieder einsteigen oder bist neugierig auf Blasmusik? Lass uns herausfinden, wie du bei uns mitmachen kannst.'),
        section([eyebrow('DEIN WEG ZU UNS'),H('Der erste Schritt ist ganz einfach.'),row([info('01 · Melde dich.','Erzähl uns ein wenig von dir und deinem Instrument. Auch deine Fragen sind willkommen.'),info('02 · Lerne uns kennen.','Wir vereinbaren einen passenden Termin und besprechen, wie ein erstes Kennenlernen aussehen kann.'),info('03 · Finde deinen Platz.','Gemeinsam schauen wir, welche Möglichkeiten zu dir und deiner musikalischen Erfahrung passen.')])]),
        section([col([eyebrow('VOM ERSTEN TON AN'),H('Neugierig auf eine Probe?'),E('Schreib uns vor deinem Besuch, damit wir dir den aktuellen Termin und alle wichtigen Infos geben können.'),B('Kennenlernen anfragen →',link('kontakt','?anliegen=mitmachen'))],width=49),col([H('Unsere Proben','h3',28),eyebrow('WANN'),E('[Wochentag ergänzen]','#7c6342'),eyebrow('UM WIE VIEL UHR'),E('[Uhrzeit ergänzen]','#7c6342'),eyebrow('WO'),E('[Probenraum und Adresse ergänzen]','#7c6342')],width=43,bg=CREAM,padding=32,padding_mobile=dimensions(25))],PAPER,'row',gap=65),
        section([eyebrow('GUT ZU WISSEN'),H('Noch Fragen?'),W('accordion',{'tabs':[{'_id':uid(),'tab_title':title,'tab_content':'<p>'+text+'</p>'} for title,text in faqs],'title_color':GREEN,'tab_active_color':GREEN,'content_color':MUTED,'title_typography_typography':'custom','title_typography_font_family':'Gaustadt Serif','title_typography_font_size':{'unit':'px','size':21},'content_typography_typography':'custom','content_typography_font_family':'Arial','content_typography_font_size':{'unit':'px','size':14},'border_color':'#dedfd4','title_background':'#faf8f1'})])
    ])
    save('kontakt','Kontakt',[
        heading('KONTAKT','Der gute Ton beginnt mit einem Hallo.','Eine Frage, eine Idee oder ein Fest in Planung? Wir freuen uns, von dir zu hören.'),
        section([col([eyebrow('SO ERREICHST DU UNS'),H('Lass uns reden.'),E('Für Auftritte, fürs Mitspielen und für alles, was du uns gerne sagen möchtest.'),H('E-Mail','h3',22),E('[gaustadt_email]'),H('Instagram','h3',22),E('<p><a href="https://www.instagram.com/bk.gaustadt/" target="_blank" rel="noopener noreferrer">@bk.gaustadt ↗</a></p>'),H('Unser Probenraum','h3',22),E('[Probenraum und Adresse ergänzen]','#7c6342')],width=34),col([H('Was liegt dir auf dem Herzen?','h2',32),W('gaustadt-inquiry',{'email':'','privacy_link':{'url':link('datenschutz')}},title='Kontakt-E-Mail und Anfragehilfe')],width=59,bg='#fffefa',padding=35,padding_mobile=dimensions(25,18),css='bg-card')],direction='row',gap=65)
    ])
    legal=[eyebrow('VORLAGE – VOR VERÖFFENTLICHUNG VERVOLLSTÄNDIGEN','#7c6342'),E('Diese Angaben sind Platzhalter. Die zutreffenden Pflichtangaben müssen ergänzt und geprüft werden.','#7c6342'),H('Anbieter','h2',28),E('[Vollständiger Vereinsname und Rechtsform]<br>[Straße, Hausnummer, PLZ und Ort]'),H('Vertreten durch','h2',28),E('[Vertretungsberechtigte Person(en)]'),H('Kontakt','h2',28),E('[gaustadt_email]<br>[Weitere Möglichkeit zur unmittelbaren Kontaktaufnahme ergänzen]'),H('Registerangaben','h2',28),E('[Registergericht und Registernummer, falls zutreffend]'),H('Inhaltlich verantwortlich','h2',28),E('[Inhaltlich verantwortliche Person und Anschrift, falls erforderlich]'),H('Bildnachweise','h2',28),E('Die derzeit verwendeten Instrumenten- und Musikdarstellungen sind Illustrationen. Sie zeigen keine tatsächlichen Mitglieder oder Auftritte der Kapelle.<br>[Nach Ergänzung eigener Fotos: Fotografen und Bildnachweise ergänzen]')]
    save('impressum','Impressum',[heading('RECHTLICHES','Impressum','Angaben zum Anbieter dieser Website.'),section(legal,css='bg-legal',boxed_width={'unit':'px','size':850})])
    privacy=[eyebrow('ENTWURF – BETRIEB UND HOSTING ERGÄNZEN','#7c6342'),E('Diese Vorlage beschreibt den technischen Aufbau. Verantwortliche, Hosting, Datenverarbeitung und Rechtsgrundlagen müssen vor Veröffentlichung geprüft und vervollständigt werden.','#7c6342'),H('1. Verantwortlicher','h2',28),E('[Vollständiger Vereinsname und Rechtsform]<br>[Adresse und vertretungsberechtigte Personen]<br>Kontakt: [gaustadt_email]'),H('2. Hosting und WordPress','h2',28),E('Beim Aufruf der Website werden technisch erforderliche Verbindungsdaten, darunter die IP-Adresse, an den Server übermittelt. Der tatsächliche Hosting-Anbieter und seine Protokollierung sind zu ergänzen. WordPress und Elementor verarbeiten für Anmeldung, Verwaltung und Bearbeitung der Website Daten und können hierbei Cookies und lokale Browser-Speicher verwenden. Besucher benötigen für die hier angebotenen Inhalte kein Benutzerkonto.'),E('[Hosting-Anbieter, Serverstandort, Empfänger, Zwecke, Rechtsgrundlagen, Speicherdauer, eingesetzte Plugins und gegebenenfalls Auftragsverarbeitung ergänzen]','#7c6342'),H('3. Kontaktaufnahme','h2',28),E('Die Anfragehilfe stellt die Eingaben ausschließlich im Browser zur Nachricht zusammen. Sie übermittelt sie nicht an einen Formularserver und speichert sie nicht dauerhaft im Browser. Über die Kopierfunktion kann der Text in die Zwischenablage übernommen werden. Erst wenn du die Nachricht selbst per E-Mail oder Instagram sendest, wird sie über den gewählten Dienst übermittelt. Für die Bearbeitung eingehender Anfragen werden die mitgeteilten Angaben benötigt.'),E('[Rechtsgrundlagen, Empfänger und Löschfristen für eingehende Kontaktanfragen ergänzen]','#7c6342'),H('4. Instagram und externe Links','h2',28),E('Diese Website verlinkt auf das Instagram-Profil der Kapelle. Instagram-Beiträge werden nicht eingebettet. Wenn du dem Link folgst, gelten die Datenschutzinformationen des jeweiligen Anbieters.'),H('5. Schriftarten, Dienste und Cookies','h2',28),E('Die gelieferten Seiten verwenden die Systemschriften Georgia und Arial. Es ist kein Analyse- oder Werbedienst Bestandteil dieses Themes. WordPress-, Elementor-, Hosting- und Plugin-Einstellungen können zusätzliche Dienste oder Datenverarbeitung aktivieren; der tatsächliche Betrieb muss geprüft werden. Das Theme unterbindet das externe Laden von Google Fonts durch Elementor. Bei zusätzlichen Plugins oder eigenen Erweiterungen muss dies erneut geprüft werden.'),E('[Tatsächliche Cookies, lokale Speicher, Dienste und gegebenenfalls erforderliche Einwilligungen ergänzen]','#7c6342'),H('6. Deine Rechte','h2',28),E('Unter den gesetzlichen Voraussetzungen hast du insbesondere Rechte auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung und Datenübertragbarkeit. Du kannst einer Verarbeitung widersprechen und eine Einwilligung für die Zukunft widerrufen. Außerdem kannst du dich bei einer Datenschutzaufsichtsbehörde beschweren.'),E('[Zuständige Datenschutzaufsichtsbehörde und Kontaktweg ergänzen]','#7c6342')]
    save('datenschutz','Datenschutz',[heading('RECHTLICHES','Datenschutz','Informationen zum Umgang mit personenbezogenen Daten auf dieser Website.'),section(privacy,css='bg-legal',boxed_width={'unit':'px','size':850})])
    print('Generated 8 native Elementor pages and 2 shared sections.')

if __name__ == '__main__': main()
