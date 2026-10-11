#!/usr/bin/env python3
"""Build editable native Elementor pages from the captured public originals."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import urllib.parse

from bs4 import BeautifulSoup, Comment

PROJECT = Path(__file__).resolve().parents[1]
THEME = PROJECT / 'team-bamberg-elementor'
BLUE, NAVY, PALE, INK, MUTED, WHITE, LIME = '#0080c8', '#112b4b', '#e5f2f8', '#142b43', '#566779', '#ffffff', '#a2c516'
PAPER, SAND = '#f1ede5', '#e5ddce'
counter = 0
assets = {}
missing = []
masked = []
source_root = None
media_by_url = {}
pages = {}
DISTRICTS = json.loads(Path(__file__).with_name('districts.json').read_text())
TOPICS = json.loads(Path(__file__).with_name('district-topics.json').read_text())
LEFT_FRACTION = {'michael-kalb', 'stefan-kuhn', 'peter-neller', 'anna-niedermaier', 'anne-rudel'}
DEAD_MEMBERSHIP_PDF = 'https://www.csu.de/common/csu/content/csu/hauptnavigation/dialog/mitmachen/SP-494_CSU_BL_Mitgliedsantrag_6-seiter_210x100_quer_01_2020_RO_150_2_innen.pdf'


def uid():
    global counter
    counter += 1
    return hashlib.sha256(f'team-bamberg-{counter}'.encode()).hexdigest()[:8]


def dims(t=0, r=None, b=None, l=None):
    r = t if r is None else r
    b = t if b is None else b
    l = r if l is None else l
    return {'unit': 'px', 'top': str(t), 'right': str(r), 'bottom': str(b), 'left': str(l), 'isLinked': t == r == b == l}


def W(kind, settings=None, css='', title=''):
    s = dict(settings or {})
    s['__globals__'] = {key: '' for key in ('typography_typography', 'title_color', 'text_color', 'background_color', 'button_text_color') if key in s}
    s['_margin'] = dims()
    if css: s['_css_classes'] = css
    if title: s['_title'] = title
    return {'id': uid(), 'elType': 'widget', 'widgetType': kind, 'settings': s, 'elements': []}


def H(text, tag='h2', size=44, color=INK, css=''):
    return W('heading', {'title': text, 'header_size': tag, 'title_color': color,
        'typography_typography': 'custom', 'typography_font_family': 'Arial', 'typography_font_weight': '800',
        'typography_font_size': {'unit': 'px', 'size': size},
        'typography_font_size_tablet': {'unit': 'px', 'size': min(size, 56)},
        'typography_font_size_mobile': {'unit': 'px', 'size': min(size, 46 if tag == 'h1' else 30)},
        'typography_line_height': {'unit': 'em', 'size': 1.08},
        'typography_letter_spacing': {'unit': 'px', 'size': -1.6 if size > 35 else -0.3}}, css)


def E(text, color=MUTED, size=16, css=''):
    if not text.startswith('<'): text = '<p>' + html.escape(text) + '</p>'
    return W('text-editor', {'editor': text, 'text_color': color, 'typography_typography': 'custom',
        'typography_font_family': 'Arial', 'typography_font_size': {'unit': 'px', 'size': size},
        'typography_line_height': {'unit': 'em', 'size': 1.75}}, css)


def eye(text, color=BLUE):
    if color == BLUE: color = '#006da9'
    return H(html.escape(text), 'p', 11, color, 'tb-eyebrow')


def link(slug): return '@@link:' + slug + '@@'


def B(text, target, bg=BLUE, color=WHITE, external=False):
    if bg == BLUE and color == WHITE: bg = '#006da9'
    return W('button', {'text': text, 'link': {'url': target, 'is_external': external},
        'background_color': bg, 'button_text_color': color, 'typography_typography': 'custom',
        'typography_font_family': 'Arial', 'typography_font_weight': '700', 'typography_font_size': {'unit': 'px', 'size': 14},
        'text_padding': dims(18, 25), 'border_radius': dims(50), 'align': 'left', '_element_width': 'auto'})


def C(children, direction='column', css='', bg=None, width=100, pad=0, gap=24, **extra):
    s = {'content_width': 'full', 'flex_direction': direction, 'flex_direction_mobile': 'column',
         'width': {'unit': '%', 'size': width}, 'width_mobile': {'unit': '%', 'size': 100},
         'padding': pad if isinstance(pad, dict) else dims(pad), 'padding_mobile': dims(0),
         'flex_gap': {'unit': 'px', 'size': gap, 'column': str(gap), 'row': str(gap), 'isLinked': True},
         'flex_align_items': 'stretch', 'css_classes': css}
    if bg: s.update(background_background='classic', background_color=bg)
    if any(name in css.split() for name in ('tb-person-card', 'tb-contact-form-card', 'tb-contact-addresses', 'tb-feature-card', 'tb-content-card', 'tb-content-block', 'tb-profile-link')):
        s['border_radius'] = dims(18)
    s.update(extra)
    return {'id': uid(), 'elType': 'container', 'isInner': False, 'settings': s, 'elements': children}


def section(children, bg=None, css='', pad=80, **extra):
    settings = {'content_width': 'boxed', 'boxed_width': {'unit': 'px', 'size': 1240},
                'padding_tablet': dims(60, 30), 'padding_mobile': dims(42, 20)}
    settings.update(extra)
    return C(children, bg=bg, css=css, pad=dims(pad, 40), **settings)


def row(children, css='', **extra): return C(children, direction='row', css=css, **extra)


def url_key(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.unquote(p.path)


def add_asset(url, alt=''):
    item = media_by_url.get(url) or media_by_url.get(url_key(url))
    if not item:
        if url and url not in missing: missing.append(url)
        return None
    key = item['sha256'][:20]
    if key not in assets:
        suffix = Path(item['file']).suffix.lower()
        file = key + suffix
        shutil.copyfile(source_root / item['file'], THEME / 'assets/media' / file)
        assets[key] = {'file': file, 'source_url': item['url'], 'sha256': item['sha256'],
                       'alt': alt or item.get('alt_as_published') or 'Bild aus der bisherigen Website',
                       'title': urllib.parse.unquote(Path(urllib.parse.urlsplit(item['url']).path).name),
                       'mime': item['mime']}
    elif alt and assets[key]['alt'] == 'Bild aus der bisherigen Website':
        assets[key]['alt'] = alt
    return key


def I(key, css='', target=None):
    if not key: return E('Das Originalbild ist auf der bisherigen Website nicht abrufbar.', css='tb-source-note')
    settings = {'image': {'team_asset': key}, 'image_size': 'full', 'width': {'unit': '%', 'size': 100}, 'align': 'center'}
    if target: settings.update(link_to='custom', link={'url': target})
    return W('image', settings, css)


def image_source(img, hero=False):
    options = []
    for entry in (img.get('srcset') or '').split(','):
        bits = entry.strip().split()
        if len(bits) == 2 and bits[1].endswith('w'):
            try: options.append((int(bits[1][:-1]), bits[0]))
            except ValueError: pass
    max_width = 2048 if hero else 1024
    options = [x for x in options if x[0] <= max_width]
    return max(options)[1] if options else img.get('src', '')


def rewrite(url):
    if not url: return ''
    if url == DEAD_MEMBERSHIP_PDF: return 'https://www.csu.de/jetzt-mitmachen/'
    malformed = re.match(r'^https?://(?:www\.)csu\.de/\((https?://.+)$', url)
    if malformed: url = malformed.group(1).rstrip(')')
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme == 'mailto' and ('<' in parsed.path or '*' in parsed.path or 'data-original-string' in parsed.path): return ''
    if parsed.scheme not in {'http', 'https', 'mailto', 'tel', ''}: return ''
    if parsed.scheme == 'mailto' and '*' in url: return ''
    if parsed.hostname in {'team-bamberg.de', 'www.team-bamberg.de'}:
        slug = parsed.path.strip('/') or 'startseite'
        if slug in pages:
            return link(slug) + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
        if Path(parsed.path).suffix.lower() in {'.pdf', '.jpg', '.jpeg', '.png', '.webp'}:
            key = add_asset(url)
            if key: return '@@asset:' + key + '@@'
    return url


def sanitise(value):
    soup = BeautifulSoup(value, 'html.parser')
    for comment in soup.find_all(string=lambda node: isinstance(node, Comment)): comment.extract()
    for bad in soup.select('script,style,iframe,form,input,button,object,embed,noscript'): bad.decompose()
    for element in list(soup.find_all(True)):
        if element.name in {'h1', 'h2'}: element.name = 'h3'
        allowed = {'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'a', 'ul', 'ol', 'li', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'abbr', 'span'}
        if element.name not in allowed:
            element.unwrap(); continue
        old = dict(element.attrs)
        element.attrs = {}
        if element.name == 'a':
            target = rewrite(old.get('href', ''))
            if old.get('href') == DEAD_MEMBERSHIP_PDF:
                element.clear(); element.append('Mitgliedschaft auf der CSU-Website')
            if old.get('href', '').lower().startswith('mailto:') and not target:
                masked.append(element.get_text('', strip=True))
            if not target:
                element.unwrap(); continue
            element['href'] = target
            if target.startswith(('https://', 'http://')) and '@@' not in target:
                element['target'] = '_blank'; element['rel'] = 'noopener noreferrer'
        elif element.name == 'abbr' and old.get('title'): element['title'] = old['title']
    return str(soup).strip()


def save(slug, title, content):
    (THEME / 'templates' / (slug + '.json')).write_text(json.dumps({
        'version': '0.4', 'title': title, 'type': 'section' if slug in {'header', 'footer'} else 'page',
        'page_settings': {}, 'content': content}, ensure_ascii=False, indent=2) + '\n')


def heading(slug, title, description=''):
    children = [E(f'<p><a href="{link("startseite")}">Startseite</a> <span aria-hidden="true">/</span> {html.escape(title)}</p>', size=12),
                eye('CSU BAMBERG-STADT'), H(html.escape(title), 'h1', 62)]
    if description: children.append(E(description))
    picture = page_picture(slug)
    if picture:
        children = [row([C(children, width=62, flex_justify_content='center'),
                         C([I(picture, 'tb-page-photo tb-page-portrait' if slug in PROFILE_SLUGS else 'tb-page-photo')], width=38)], gap=65)]
    return section(children, SAND, css='tb-page-title', pad=48)


PROFILE_SLUGS = ['andeas-dechant', 'dr-franz-wilhelm-heller', 'michael-kalb', 'stefan-kuhn', 'dr-christian-lange', 'peter-neller', 'anna-niedermaier', 'dr-ursula-redler', 'anne-rudel', 'prof-dr-gerhard-seitz', 'you-xie']


def page_picture(slug):
    if not pages[slug].get('file'):
        return add_asset('https://team-bamberg.de/wp-content/uploads/2020/12/AdobeStock_193611934-11-scaled-1536x1025.jpg', 'Bamberg an der Regnitz')
    soup = BeautifulSoup((source_root / pages[slug]['file']).read_text(), 'html.parser')
    root = soup.select_one('[data-elementor-type="wp-page"]')
    if root:
        for part in root.select('header,nav,footer'): part.decompose()
        for img in root.select('img'):
            if 'CSU_Logo' in img.get('src', ''): continue
            url = image_source(img)
            if media_by_url.get(url) or media_by_url.get(url_key(url)):
                key = add_asset(url, pages[slug]['title'])
                if slug != 'kontakt': return key
                break  # Keep the original contact banner in the media library; show Bamberg here.
    if slug in PROFILE_SLUGS: return None
    return add_asset('https://team-bamberg.de/wp-content/uploads/2020/12/AdobeStock_193611934-11-scaled-1536x1025.jpg', 'Bamberg an der Regnitz')


def note(text): return E(text, color='#75571c', size=13, css='tb-source-note')


def convert_widget(widget, slug):
    kind = widget.get('data-widget_type', '').split('.')[0]
    body = widget.select_one('.elementor-widget-container') or widget
    if kind == 'image':
        img = body.find('img')
        if not img or 'CSU_Logo' in img.get('src', ''): return []
        url = image_source(img)
        key = add_asset(url, img.get('alt') or pages[slug]['title'])
        if key and key == page_picture(slug): return []  # Display once, in the page introduction.
        anchor = img.find_parent('a')
        destination = rewrite(anchor.get('href', '')) if anchor else None
        style = 'tb-banner' if 'Header' in url or 'Header' in img.get('alt', '') else 'tb-original-image'
        return [I(key, style, destination)]
    if kind == 'image-box':
        img = body.find('img'); out = []
        if img: out.append(I(add_asset(image_source(img), body.get_text(' ', strip=True)), 'tb-portrait'))
        title = body.select_one('.elementor-image-box-title')
        text = body.select_one('.elementor-image-box-description')
        if title: out.append(H(sanitise(title.decode_contents()), 'h3', 25))
        if text: out.append(E(sanitise(text.decode_contents())))
        return out
    if kind == 'heading':
        title = body.select_one('.elementor-heading-title') or body
        text = html.escape(title.get_text(' ', strip=True))
        return [H(text, 'h3', 26)] if title.get_text(strip=True) else []
    if kind == 'text-editor':
        text = sanitise(body.decode_contents())
        clean = BeautifulSoup(text, 'html.parser')
        if slug == 'kreisvorstand-2':
            for paragraph in clean.find_all('p'):
                if 'Fraktionsvorsitzender auf Grund des Amtes' in paragraph.get_text(' ', strip=True) and 'Peter Neller' in paragraph.get_text(' ', strip=True):
                    paragraph.decompose()
        for block in clean.find_all(['p', 'h3', 'h4', 'h5', 'h6']):
            if block.find(['p', 'h3', 'h4', 'h5', 'h6']): continue
            raw = block.get_text(' ', strip=True)
            if len(raw) < 400 and '*' in raw and '@' in raw:
                prefix = re.split(r'(?:E-Mail|Mail)\s*:', raw, maxsplit=1)[0] if re.search(r'(?:E-Mail|Mail)\s*:', raw) else ''
                block.clear()
                if prefix: block.append(prefix); block.append(clean.new_tag('br'))
                block.append('E-Mail-Adresse wird noch bestätigt. Kontakt über die Geschäftsstelle.')
        text = str(clean)
        return [E(text)] if body.get_text(strip=True) else []
    if kind == 'button':
        a = body.find('a')
        return [B(a.get_text(' ', strip=True), rewrite(a.get('href', '')))] if a else []
    if kind == 'video':
        settings = json.loads(widget.get('data-settings') or '{}')
        url = settings.get('youtube_url', '')
        return [B('Video auf YouTube ansehen →', url, external=True)] if url else []
    return []


def generic_content(slug):
    record = pages[slug]
    soup = BeautifulSoup((source_root / record['file']).read_text(), 'html.parser')
    root = soup.select_one('[data-elementor-type="wp-page"]')
    result = []
    if root is None:
        return [section([E('Die ursprüngliche Seite enthält keine öffentlichen Inhaltsangaben.')], pad=35)]
    if slug in PROFILE_SLUGS:
        body, aside = [], []
        contact = False
        for widget in root.select('.elementor-widget'):
            if widget.find_parent(['header', 'nav', 'footer']): continue
            for item in convert_widget(widget, slug):
                settings = item['settings']
                text = settings.get('editor', settings.get('title', ''))
                if item.get('widgetType') == 'heading' and 'kontakt' in text.lower(): contact = True
                side = contact or item.get('widgetType') == 'button' or ('href=' in text and len(text) < 1800) or ('@' in text and len(text) < 450)
                (aside if side else body).append(item)
        columns = []
        if body: columns.append(C([eye('PERSÖNLICHE VORSTELLUNG')] + body, css='tb-content-block tb-profile-story', width=65, gap=22))
        if aside: columns.append(C([eye('KONTAKT & WEITERE EINBLICKE')] + aside, css='tb-content-block tb-profile-details', width=35, gap=20))
        return [section([row(columns, css='tb-profile-layout', gap=30)], pad=35)] if columns else []
    for original_section in root.find_all(recursive=False):
        if original_section.name in {'header', 'nav', 'footer'}: continue
        groups = {}
        for widget in original_section.select('.elementor-widget'):
            if widget.find_parent(['header', 'nav', 'footer']): continue
            contents = convert_widget(widget, slug)
            if not contents: continue
            parent = widget.find_parent(class_='elementor-column')
            group = parent.get('data-id', 'body') if parent else 'body'
            groups.setdefault(group, []).extend(contents)
        if not groups: continue
        children = []
        for content in groups.values():
            # Original panorama images are separated from portrait/text cards.
            banners = [w for w in content if w['settings'].get('_css_classes') == 'tb-banner']
            if banners: result.append(section(banners, css='tb-source-banner', pad=25))
            content = [w for w in content if w not in banners]
            if content:
                style = 'tb-content-card' if len(groups) > 1 else 'tb-content-block'
                if all(w.get('widgetType') == 'heading' for w in content): style += ' tb-section-heading'
                children.append(C(content, css=style))
        if children:
            result.append(section([C(children, css='tb-grid tb-grid-' + str(min(len(children), 4)))], pad=30))
    return result


def district_content(slug):
    """Build a district article and identifiable contact cards, instead of copying empty rows."""
    info = DISTRICTS[slug]
    soup = BeautifulSoup((source_root / pages[slug]['file']).read_text(), 'html.parser')
    root = soup.select_one('[data-elementor-type="wp-page"]')
    for part in root.select('header,nav,footer'): part.decompose()
    widgets = root.select('.elementor-widget')
    story = [w for w in widgets if w.get('data-widget_type') == 'text-editor.default' and len(w.get_text(' ', strip=True)) > 500]
    assert story, 'District story missing: ' + slug
    photographs = []
    for w in widgets:
        if w.get('data-widget_type') == 'heading.default' and w.get_text(' ', strip=True) == 'Kontakt': break
        if w.get('data-widget_type') == 'image.default':
            img = w.select_one('img'); key = add_asset(image_source(img), 'Bamberg – ' + info['label'])
            if key and key != page_picture(slug): photographs.append(key)
    contact_cards = []
    for name in info['people']:
        matches = [w for w in widgets if w.get('data-widget_type') == 'text-editor.default' and name in w.get_text(' ', strip=True) and len(w.get_text(' ', strip=True)) < 500]
        assert matches, 'District contact missing: ' + slug + ': ' + name
        widget = matches[0]; column = widget.find_parent(class_='elementor-column')
        texts = [w for w in column.select('.elementor-widget-text-editor') if len(w.get_text(' ', strip=True)) < 500]
        raw = ' '.join(w.get_text(' ', strip=True) for w in texts)
        plain = ' '.join(w.get_text('', strip=True) for w in texts)
        role = 'ORTSVERBAND · BISHERIGER AUFTRITT' if 'vorsitz' in raw.lower() else 'PERSÖNLICHE VORSTELLUNG'
        details = raw.replace(name, '', 1).strip(' ,')
        details = re.sub(r'^(?:Ortsvorsitzender|Vorsitzender)\s*', '', details)
        details = re.split(r'(?:E-Mail|Mail)\s*:', details, maxsplit=1)[0].strip()
        details = html.escape(details).replace('Tel.:', '<br>Telefon:')
        email = re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', plain.replace('(at)', '@')) if '*' not in plain else None
        photo = next((w.select_one('img') for w in column.select('.elementor-widget-image') if w.select_one('img')), None)
        if photo is None:
            # Some original layouts put the portrait in a separate column before the name.
            for preceding in reversed(widgets[:widgets.index(widget)]):
                kind = preceding.get('data-widget_type')
                if kind == 'heading.default' and preceding.get_text(' ', strip=True) == 'Kontakt': break
                if kind == 'text-editor.default': break
                if kind == 'image.default': photo = preceding.select_one('img'); break
        key = add_asset(image_source(photo), name) if photo else None
        portrait = I(key, 'tb-district-person-photo') if key else H(''.join(word[0] for word in name.split() if word[0].isupper())[:2], 'p', 28, NAVY, 'tb-person-initials')
        items = [row([C([portrait], width=27), C([eye(role), H(name, 'h3', 24)], width=73, flex_justify_content='center')], gap=18, flex_direction_mobile='row')]
        if details: items.append(E('<p>' + details + '</p>', INK, 15))
        if email: items.append(B('E-Mail schreiben →', 'mailto:' + email.group(), PAPER, NAVY))
        else: items.append(B('Kontakt über die Geschäftsstelle →', link('kontakt') + '?anliegen=' + slug, PAPER, NAVY))
        profile = next((p for p in PROFILE_SLUGS if pages[p]['title'] == name), None)
        if profile: items.append(B('Persönliches Profil →', link(profile), PAPER, NAVY))
        contact_cards.append(C(items, css='tb-content-card tb-district-contact', gap=18))
    menu = [('ortsverband', 'Unser Ortsverband'), ('themen-vor-ort', 'Gesprächsfelder'), ('meldungen', 'Meldungen'), ('veranstaltungen', 'Termine'), ('ansprechpartner', 'Kontakt')]
    result = [section([row([B(label + ' ↓', '#' + target, PAPER, NAVY) for target, label in menu], gap=12)], PAPER, 'tb-district-shortcuts', pad=20),
        section([row([C([eye('MITTEN IN ' + info['label'].upper()), H('Ein Ortsverband.<br>Viele Perspektiven.', 'h2', 46), E(info['intro'], INK, 19), E('Hier finden Sie Informationen zum Stadtteil, persönliche Kontaktwege und Platz für die nächsten Meldungen und Veranstaltungen des Ortsverbands.'), B('Kontakt zum Ortsverband →', '#ansprechpartner', NAVY, WHITE)], width=60),
                      C([eye('DAS GEHÖRT ZU UNS')] + [H(place, 'p', 24) for place in info['places']], css='tb-district-facts', bg=SAND, width=40, pad=32)], gap=55)], PAPER, _element_id='ortsverband', pad=58),
        section([eye('FRAGEN AUS DEM STADTTEIL'), H('Was bewegt ' + info['label'] + '?'), E('Gesprächsfelder als redaktioneller Entwurf. Konkrete Positionen und Vorhaben werden vom Ortsverband ergänzt.'),
                 C([C([eye('0' + str(i + 1)), H(topic['title'], 'h3', 27), E(topic['text']), B('Dazu ins Gespräch kommen →', link('kontakt') + '?anliegen=' + slug, PAPER, NAVY)], css='tb-local-topic', bg='#f8f5ee', pad=30) for i, topic in enumerate(TOPICS[slug])], css='tb-grid tb-grid-3')], SAND, _element_id='themen-vor-ort', pad=55),
        section([row([C([eye('NEUIGKEITEN VOR ORT'), H('Aus ' + info['label'] + '.'), E('Veröffentlichte Meldungen dieses Ortsverbands erscheinen hier automatisch.')], width=70), C([B('Alle Meldungen →', link('aktuelles') + '?ort=' + slug, PAPER, NAVY)], width=30, flex_justify_content='center')], gap=30),
                 W('team-bamberg-news', {'area': slug, 'limit': 3, 'empty_title': 'Die nächsten Einblicke folgen.', 'empty_text': 'Hier ist Platz für Nachrichten aus dem Ortsverband. Für ein persönliches Anliegen können Sie sich schon jetzt an die Geschäftsstelle wenden.'})], PAPER, _element_id='meldungen', pad=55),
        section([row([C([eye('BEGEGNEN & AUSTAUSCHEN', '#c5dfef'), H('Wir sehen uns<br>in ' + info['label'] + '.', 'h2', 42, WHITE), E('Ob Stadtteilgespräch oder Veranstaltung: Hier erscheinen bestätigte Termine des Ortsverbands.', '#d8e4e9'), B('Alle Termine →', link('termine'), LIME, NAVY)], width=50),
                      C([W('team-bamberg-events', {'source': 'shared', 'area': slug, 'show_past': '', 'empty_title': 'Neue Termine werden angekündigt.', 'empty_text': 'Datum und Ort finden Sie hier, sobald eine Veranstaltung feststeht.'})], width=50)], gap=50)], NAVY, _element_id='veranstaltungen', pad=55),
        section([eye('DER PERSÖNLICHE KONTAKT'), H('Menschen in ' + info['label'] + '.'), E('Kontaktangaben aus dem bisherigen Auftritt. Aktuelle Funktionen und Erreichbarkeit werden vor Veröffentlichung bestätigt.', size=14),
                 C(contact_cards, css='tb-grid tb-grid-' + str(min(len(contact_cards), 2)))], PAPER, _element_id='ansprechpartner', pad=55)]
    if photographs:
        result.append(section([I(photographs[0], 'tb-district-panorama')], PAPER, pad=15))
    history = ''.join(sanitise((w.select_one('.elementor-widget-container') or w).decode_contents()) for w in story)
    result.append(section([C([eye('UNSER STADTTEIL HAT GESCHICHTE'), H('Wie ' + info['label'] + ' geworden ist.', 'h2', 35),
        E('<details class="tb-history"><summary>Die vollständige Stadtteilgeschichte lesen →</summary><div>' + history + '</div></details>'),
        E('Historische Vorstellung aus der bisherigen Website. Zeitgebundene Aussagen bleiben als Originaltext dokumentiert.', size=12)], css='tb-content-block tb-district-story', gap=22)], SAND, _element_id='stadtteil', pad=45))
    return result


def original_text(slug):
    soup = BeautifulSoup((source_root / pages[slug]['file']).read_text(), 'html.parser')
    return [w for w in soup.select('[data-elementor-type="wp-page"] .elementor-widget')
            if w.get('data-widget_type') == 'text-editor.default' and not w.find_parent(['header', 'nav', 'footer'])]


def main():
    global source_root, media_by_url, pages
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('/workspace/team-bamberg-source'))
    args = parser.parse_args(); source_root = args.source.resolve()
    inventory = json.loads((source_root / 'inventory.json').read_text())
    for item in inventory['media']:
        media_by_url[item['url']] = item
        media_by_url[url_key(item['url'])] = item
    for item in sorted(inventory['pages'], key=lambda p: not p['url'].startswith('https://')):
        slug = urllib.parse.urlsplit(item['url']).path.strip('/') or 'startseite'
        if slug in pages: continue
        title = item['title'].split(' – ')[0]
        if slug == 'startseite': title = 'Startseite'
        if slug == 'andeas-dechant': title = 'Andreas Dechant'
        if slug == 'aktuelles-2': title = 'Archiv & Transparenz'
        pages[slug] = {**item, 'title': title}
        soup = BeautifulSoup((source_root / item['file']).read_text(), 'html.parser')
        root = soup.select_one('[data-elementor-type="wp-page"]')
        if root:
            for irrelevant in root.select('header,nav,footer,script,style'): irrelevant.decompose()
            pages[slug]['text'] = root.get_text(' ', strip=True)
        else: pages[slug]['text'] = ''
    if not {'startseite', 'kreisvorstand-2', 'ortsverbaende', 'fraktion', 'kontakt', 'impressum', 'datenschutz'} <= pages.keys():
        raise SystemExit('Essential source pages are missing; review the inventory before rebuilding.')
    for slug, title in [('aktuelles', 'Aktuelles'), ('themen', 'Themen für Bamberg')]:
        pages[slug] = {'title': title, 'url': '', 'file': '', 'text': title}
    THEME.joinpath('assets/media').mkdir(parents=True, exist_ok=True)
    THEME.joinpath('templates').mkdir(parents=True, exist_ok=True)
    previous_manifest = THEME / 'manifest.json'
    if previous_manifest.exists():
        for asset in json.loads(previous_manifest.read_text())['media'].values():
            add_asset(asset['source_url'], asset['alt'])
    logo_url = 'https://team-bamberg.de/wp-content/uploads/2020/11/CSU_Logo_1c_neg-300x69.png'
    logo = add_asset(logo_url, 'CSU – Christlich-Soziale Union')
    hero = add_asset('https://team-bamberg.de/wp-content/uploads/2020/11/AdobeStock_97121734-11-2048x1041.jpg', 'Altes Rathaus in Bamberg an der Regnitz')
    city = add_asset('https://team-bamberg.de/wp-content/uploads/2020/12/AdobeStock_193611934-11-scaled-1536x1025.jpg', 'Bamberg – Foto aus der bisherigen Website')
    main_menu = [('kreisvorstand-2', 'CSU Bamberg'), ('ortsverbaende', 'Vor Ort'), ('fraktion', 'Stadtrat'), ('aktuelles', 'Aktuelles'), ('termine', 'Termine'), ('kontakt', 'Kontakt')]
    sub_menu = [('kreisvorstand-2', 'Kreisverband', 'CSU Bamberg'), ('mandatstraeger', 'Mandatsträger', 'CSU Bamberg'), ('fachgruppen', 'Fachgruppen', 'CSU Bamberg'), ('asp-kreisverband', 'Außen- & Sicherheitspolitik', 'CSU Bamberg'), ('mitglied-werden', 'Mitglied werden', 'CSU Bamberg'), ('spenden', 'Unterstützen', 'CSU Bamberg'),
                ('themen', 'Themen für Bamberg', 'Stadtrat'), ('fraktionsantraege', 'Anträge & Dokumente', 'Stadtrat')]
    sub_menu += [(slug, 'CSU ' + info['label'], 'Vor Ort') for slug, info in DISTRICTS.items()]
    nav_items = [{'_id': uid(), 'label': label, 'link': {'url': link(slug)}, 'parent': ''} for slug, label in main_menu]
    nav_items += [{'_id': uid(), 'label': label, 'link': {'url': link(slug)}, 'parent': parent} for slug, label, parent in sub_menu]
    save('header', 'Kopfbereich & Navigation', [
        section([row([E('CSU BAMBERG-STADT · IN ACHT ORTSVERBÄNDEN ZU HAUSE', '#d5e7f2', 10), E(f'<p><a href="{link("csu-gaustadt")}">CSU Gaustadt</a> <span>·</span> <a href="{link("mitglied-werden")}">Mitmachen</a></p>', '#d5e7f2', 11)], flex_justify_content='space-between')], NAVY, 'tb-topbar', pad=8, padding_mobile=dims(8, 20)),
        section([row([C([row([C([I(logo, 'tb-logo', link('startseite'))], css='tb-brand-mark', width=35, bg=BLUE, pad=dims(14, 16)), C([H('Bamberg-Stadt', 'p', 20)], css='tb-brand-label', width=65)], css='tb-brand-lockup', gap=12, flex_align_items='center', flex_direction_mobile='row')], css='tb-header-brand', width=26, width_mobile={'unit': '%', 'size': 76}), C([W('team-bamberg-navigation', {'items': nav_items})], css='tb-header-navigation', width=74, width_mobile={'unit': '%', 'size': 24}, flex_align_items='flex-end')], flex_align_items='center', flex_direction_mobile='row', gap=18)], PAPER, 'tb-header-main', pad=20, padding_mobile=dims(16, 20))
    ])
    footer_links = [('CSU Bamberg', [('kreisvorstand-2', 'Kreisverband'), ('ortsverbaende', 'Ortsverbände'), ('fachgruppen', 'Fachgruppen'), ('asp-kreisverband', 'ASP Kreisverband')]),
                    ('Politik & Menschen', [('fraktion', 'Stadtratsfraktion'), ('mandatstraeger', 'Mandatsträger'), ('fraktionsantraege', 'Anträge & Archiv'), ('aktuelles', 'Aktuelles'), ('themen', 'Themen'), ('aktuelles-2', 'Transparenz'), ('termine', 'Termine')]),
                    ('Mitmachen', [('mitglied-werden', 'Mitglied werden'), ('spenden', 'Spenden'), ('kontakt', 'Kontakt')])]
    columns = [C([I(logo, 'tb-footer-logo', link('startseite')), H('Bamberg gestalten.', 'h3', 25, WHITE), E('Näher am Menschen.', '#adc1d4', 14)], width=30)]
    for title, links in footer_links:
        columns.append(C([eye(title, '#adc1d4'), E(''.join(f'<p><a href="{link(slug)}">{label}</a></p>' for slug, label in links), WHITE, 13)], width=23))
    save('footer', 'Fußbereich', [section([row(columns, css='tb-footer-columns', gap=40), row([
        E('CSU Bamberg-Stadt · Gestaltungsentwurf · Stand 11.10.2026', '#adc1d4', 11),
        E(f'<p><a href="{link("impressum")}">Impressum</a> · <a href="{link("datenschutz")}">Datenschutz</a> · <a href="https://www.facebook.com/csubamberg" target="_blank" rel="noopener noreferrer">Facebook →</a></p>', WHITE, 11)], css='tb-footer-bottom', gap=35)], NAVY, 'tb-footer', pad=65)])

    district_soup = BeautifulSoup((source_root / pages['ortsverbaende']['file']).read_text(), 'html.parser')
    district_cards = []
    district_names = [('csu-mitte', 'Mitte', 'Bamberg_Mitte'), ('csu-gangolf', 'Gangolf', 'Gangolf-1'),
        ('csu-berg', 'Berg', 'Berg1'), ('csu-wunderburg', 'Wunderburg / Gereuth', 'Bamberg_wunderburg'),
        ('csu-nord', 'Nord', 'Nord2'), ('csu-ost', 'Ost', 'Ost1'), ('csu-gartenstadt', 'Gartenstadt', 'Gartenstadt1'), ('csu-gaustadt', 'Gaustadt', 'Gaustadt1')]
    for slug, label, marker in district_names:
        img = next(i for i in district_soup.select('img') if marker in i.get('src', ''))
        key = add_asset(image_source(img), 'Bamberg – ' + label)
        district_cards.append(C([I(key, 'tb-district-image', link(slug)), row([H(label, 'h3', 19), B('→', link(slug), WHITE, BLUE)], gap=8, flex_align_items='center', flex_justify_content='space-between', flex_direction_mobile='row')], css='tb-district-card', gap=18))
    home_original = original_text('startseite')
    about = next(w for w in home_original if 'Bamberg ist eine besondere Stadt' in w.get_text())
    featured = ['dr-christian-lange', 'prof-dr-gerhard-seitz', 'dr-ursula-redler', 'you-xie']
    people_cards = [C([I(page_picture(p), 'tb-person-image', link(p)), C([
        H(pages[p]['title'], 'h3', 23), B('Persönlich kennenlernen →', link(p), PAPER, NAVY)], css='tb-person-caption', gap=14)], css='tb-person-card', gap=0) for p in featured]
    home = [section([W('team-bamberg-hero-media', {'poster': {'team_asset': hero}, 'autoplay': ''}, 'tb-hero-backdrop'), C([
        eye('HIER SIND WIR ZU HAUSE.', '#dcebb3'),
        H('Bamberg.<br>Unsere Stadt.<br>Unser Miteinander.', 'h1', 77, WHITE),
        E('CSU Bamberg-Stadt. Acht Ortsverbände, persönliche Begegnungen und ein gemeinsamer Blick auf unsere Stadt.', '#e6e9e6', 19),
        row([B('Die CSU Bamberg kennenlernen →', link('kreisvorstand-2'), LIME, NAVY), B('In Ihrem Stadtteil →', link('ortsverbaende'), '#254361', WHITE)], gap=12),
        E('CSU BAMBERG-STADT · NÄHER AM MENSCHEN', '#dae3e8', 10, 'tb-hero-foot')
    ], css='tb-hero-copy', width=62, gap=28), E('Bamberg an der Regnitz · Altes Rathaus', '#e3e8eb', 11, 'tb-hero-caption')], NAVY, 'tb-hero', pad=78),
        section([row([C([eye('UNSERE STADT. UNSER MITEINANDER.'), H('Bamberg ist mehr<br>als eine Adresse.'),
            E(sanitise((about.select_one('.elementor-widget-container') or about).decode_contents())),
            B('Unseren Kreisverband entdecken →', link('kreisvorstand-2'), NAVY, WHITE)], width=55, flex_justify_content='center'),
            C([I(city, 'tb-about-image'), E('Vertraute Orte. Unterschiedliche Perspektiven. Ein gemeinsames Bamberg.', '#4c5d60', 13)], width=45)], gap=65)], PAPER, 'tb-home-about', pad=68),
        section([row([C([eye('PERSÖNLICH KENNENLERNEN'), H('Politik hat Gesichter.'), E('Persönliche Vorstellungen aus Bamberg: Entdecken Sie Menschen und ihren Blick auf die Stadt.')], width=72),
                     C([B('Zum Kreisverband →', link('kreisvorstand-2'), NAVY, WHITE)], width=28, flex_justify_content='center')], gap=35),
                 C(people_cards, css='tb-grid tb-grid-4'), E('Porträts aus der bisherigen Website. Aktuelle Funktionen werden vor Veröffentlichung abgeglichen.', '#5b625d', 12)], SAND, 'tb-people-section', pad=65),
        section([row([C([eye('ACHT ORTSVERBÄNDE', '#c5dfef'), H('Ihr Stadtteil.<br>Ihr Bamberg.', 'h2', 49, WHITE),
            E('Vom Berggebiet bis zur Gartenstadt, von Gaustadt bis zur Wunderburg: Hier finden Sie den Ortsverband in Ihrer Nähe.', '#d8e4e9')], width=72),
            C([B('Alle Ortsverbände →', link('ortsverbaende'), LIME, NAVY)], width=28, flex_justify_content='center')], gap=35), C(district_cards, css='tb-grid tb-grid-4')], NAVY, 'tb-district-section', pad=65),
        section([row([C([eye('WAS PASSIERT IM STADTRAT?'), H('Stadtpolitik.<br>Zum Nachlesen.'), E('Welche Themen wurden eingebracht? Wer gehört zum vorgestellten Team? Die Fraktionsseiten und das Antragsarchiv machen die bisherige Arbeit zugänglich.'), B('Zur Stadtratsfraktion →', link('fraktion'), NAVY, WHITE)], width=52),
            C([C([eye('ANTRÄGE & DOKUMENTE'), H('Ein Thema suchen.<br>Mehr erfahren.', 'h3', 31), E('Originalanträge mit Datum, Dokumenten und einer Suche nach Thema und Jahr.'), B('Im Archiv stöbern →', link('fraktionsantraege'))], css='tb-feature-card', bg=SAND, pad=34),
               C([H('Im Gespräch bleiben.', 'h3', 24), E('Eine Frage, eine Idee oder ein Anliegen aus Ihrem Stadtteil? Hier geht es zum Kontakt.'), B('Kontakt aufnehmen →', link('kontakt'), PAPER, NAVY)], css='tb-feature-card', bg='#dae5df', pad=30)], width=48)], gap=65)], PAPER, pad=65),
        section([row([C([eye('BEGEGNEN & AUSTAUSCHEN'), H('Manches bespricht<br>sich besser persönlich.'), E('Hier finden Sie bestätigte kommende Veranstaltungen. Bis dahin können Sie über die Kontaktseite den Austausch suchen.')], width=55), C([W('team-bamberg-events', {'source': 'shared', 'single': 'yes', 'empty_title': 'Wann sehen wir uns?', 'empty_text': 'Neue bestätigte Termine finden Sie hier, sobald sie feststehen.'}), B('Zur Terminübersicht →', link('termine'), NAVY, WHITE)], width=45)], gap=65)], '#dbe6e6', pad=60),
        section([row([C([eye('LUST, BAMBERG MITZUGESTALTEN?', '#dcebb3'), H('Gute Gespräche.<br>Neue Begegnungen.', 'h2', 48, WHITE), E('Ob Sie erst einmal eine Frage stellen oder sich über eine Mitgliedschaft informieren möchten: Finden Sie Ihren Einstieg.', '#d5e7f2')], width=65), C([B('Mitgliedschaft kennenlernen →', link('mitglied-werden'), LIME, NAVY), B('Sagen Sie Hallo →', link('kontakt'), '#254361', WHITE)], width=35, flex_justify_content='center')], gap=45)], NAVY, 'tb-join-section', pad=60)]
    home.insert(1, section([row([C([eye('NAH DRAN. GUT ORIENTIERT.'), H('Was gibt es Neues?', 'h2', 43)], width=70), C([B('Alle Meldungen →', link('aktuelles'), PAPER, NAVY)], width=30, flex_justify_content='center')], gap=30), W('team-bamberg-news', {'area': 'all', 'limit': 3, 'empty_title': 'Bamberg bleibt im Gespräch.', 'empty_text': 'Neue Meldungen aus dem Kreisverband und den Ortsverbänden erscheinen hier nach Veröffentlichung. Stadtteilinformationen und das Antragsarchiv finden Sie bereits im Menü.'})], PAPER, 'tb-home-news', pad=58))
    gaustadt_picture = page_picture('csu-gaustadt')
    home.insert(5, section([row([C([I(gaustadt_picture, 'tb-gaustadt-feature-image', link('csu-gaustadt'))], width=48), C([eye('BAMBERG HAT VIELE GESICHTER'), H('Gaustadt.<br>Mit eigener Geschichte.'), E(DISTRICTS['csu-gaustadt']['intro']), B('Den Ortsverband Gaustadt entdecken →', link('csu-gaustadt'), NAVY, WHITE)], width=52, flex_justify_content='center')], gap=55)], SAND, 'tb-gaustadt-feature', pad=55))
    save('startseite', 'Startseite', home)

    descriptions = {
        'kreisvorstand-2': 'Eine Stadt, viele Menschen. Hier lernen Sie den Kreisverband, seine Organisation und die auf der bisherigen Website vorgestellten Ansprechpartner kennen.',
        'ortsverbaende': 'Bamberg beginnt vor der eigenen Haustür. Entdecken Sie unsere acht Ortsverbände und die Menschen in Ihrem Stadtteil.',
        'fraktion': 'Stadtpolitik nachvollziehbar machen: Ansprechpartner, Anträge und dokumentierte Arbeit im Bamberger Stadtrat.',
        'mandatstraeger': 'Politik wird von Menschen gemacht. Lernen Sie die auf Team Bamberg vorgestellten Mandatsträger und ihre Aufgaben kennen.',
        'fachgruppen': 'Menschen zusammenbringen, Erfahrungen teilen, Themen vertiefen. Ein Überblick über die Fachgruppen und Arbeitsgemeinschaften der CSU Bamberg.',
        'kontakt': 'Eine Frage, eine Idee oder ein Anliegen aus Ihrem Stadtteil? Finden Sie den passenden Kontakt und bereiten Sie Ihre Nachricht vor.',
        'fraktionsantraege': 'Was wurde eingebracht, wann und zu welchem Thema? Stöbern Sie in den Originalanträgen oder suchen Sie gezielt nach einem Stichwort.',
        'antraege': 'Eine Auswahl aus der dokumentierten Stadtratsarbeit. Die Originaltexte und Dokumente laden dazu ein, einzelne Themen genauer kennenzulernen.',
        'termine': 'Sich begegnen, zuhören und ins Gespräch kommen. Hier ist Platz für bestätigte Veranstaltungen und die bisherigen Terminangaben.',
        'mitglied-werden': 'Sie möchten die CSU kennenlernen oder sich einbringen? Hier finden Sie Informationen zur Mitgliedschaft und die weiterführenden Originalunterlagen.',
        'spenden': 'Die Arbeit vor Ort unterstützen: Hier sind die bisherigen Angaben zu Spenden und Ansprechpartnern zusammengefasst. Bankdaten bitte vor einer Überweisung bestätigen lassen.',
        'impressum': 'Wer steht hinter dieser Website? Hier finden Sie die übernommenen Angaben zur Verantwortung und zum Kontakt.',
        'datenschutz': 'Ein transparenter Umgang mit Daten gehört zu einer guten Website. Hier finden Sie den bisherigen Datenschutztext als Grundlage für die Aktualisierung.',
        'asp-kreisverband': 'Sicherheitspolitik im Austausch. Lernen Sie den Arbeitskreis Außen- und Sicherheitspolitik und die Informationen aus dem bisherigen Auftritt kennen.',
        'asp-bezirk': 'Ein Blick zurück auf die dokumentierte Arbeit des ASP-Bezirksverbands. Die ursprünglichen Inhalte und Zeitangaben bleiben erhalten.',
        'aktuelles-2': 'Ein Ort zum Nachlesen: weitere Originalseiten, historische Inhalte und Transparenzangaben zu politischen Anzeigen.',
    }
    district_labels = {slug: label for slug, label, _ in district_names}
    for slug, label in district_labels.items():
        descriptions[slug] = DISTRICTS[slug]['intro']
    profile_slugs = PROFILE_SLUGS
    for slug in profile_slugs:
        descriptions[slug] = 'Ein persönlicher Blick auf den Menschen hinter dem Namen: die Vorstellung, Schwerpunkte und Kontaktangaben aus dem bisherigen Team-Bamberg-Auftritt.'
    for slug, record in pages.items():
        if slug in {'startseite', 'aktuelles', 'themen'}: continue
        title = 'Anträge & Archiv' if slug == 'fraktionsantraege' else record['title']
        content = [heading(slug, title, descriptions.get(slug, 'Originalunterlagen und Transparenzangaben zum Nachlesen. Diese Archivseite bewahrt die veröffentlichten Informationen und ihre ursprünglichen Zeiträume.'))]
        if slug in DISTRICTS:
            info = DISTRICTS[slug]
            content = [section([I(page_picture(slug), 'tb-hero-backdrop'), C([E(f'<p><a href="{link("ortsverbaende")}">← Alle Ortsverbände</a></p>', '#d5e7f2', 13), eye('CSU BAMBERG-STADT · VOR ORT', '#dcebb3'), H('CSU ' + info['label'] + '.', 'h1', 72, WHITE), E(info['intro'], '#e6e9e6', 19), B('Unser Ortsverband ↓', '#ortsverband', LIME, NAVY)], css='tb-hero-copy', width=67)], NAVY, 'tb-hero tb-local-hero' + (' tb-gaustadt-hero' if slug == 'csu-gaustadt' else ''), pad=65)]
        if slug in {'kreisvorstand-2', 'fraktion', 'mandatstraeger'} or slug in profile_slugs:
            content.append(section([note('Personen, Funktionen und Kontaktdaten wurden aus der bisherigen Website übernommen. Die aktuelle Besetzung muss vor Veröffentlichung bestätigt werden.')], pad=20))
        if slug in {'impressum', 'datenschutz'}:
            content.append(section([note('Übernommener Rechtstext der bisherigen Website. Die enthaltene Datenschutzerklärung trägt den Stand Mai 2018. Verantwortliche, Kontaktdaten und tatsächliche Dienste müssen für die neue Website aktualisiert werden.')], pad=20))
        if slug == 'spenden':
            content.append(section([note('Die veröffentlichte IBAN ist unvollständig und beginnt ohne Länderkennung. Bankdaten, Ansprechpartner und steuerliche Angaben müssen vor Verwendung bestätigt werden. Die Originalangaben sind unten dokumentiert.')], pad=20))
        if slug == 'termine':
            content.append(section([H('Kommende Veranstaltungen'), W('team-bamberg-events', {'source': 'this', 'events': [], 'show_past': 'yes', 'empty_title': 'Neue Termine folgen.', 'empty_text': 'Bestätigte kommende Veranstaltungen werden hier veröffentlicht.'}), H('Aus der bisherigen Terminübersicht', 'h2', 30), note('Die Originalangabe enthält kein Jahr. Sie wird deshalb nicht als bestätigter zukünftiger Termin angezeigt.')], pad=45))
        if slug == 'fraktionsantraege':
            cards = []
            for widget in original_text(slug):
                raw = widget.get_text(' ', strip=True)
                date = re.search(r'\b\d{2}\.\d{2}\.(\d{4})\b', raw)
                converted = convert_widget(widget, slug)
                if date: cards.append(C(converted, css='tb-document tb-year-' + date.group(1)))
                elif converted: content.append(section(converted, pad=20))
            content.append(section([W('team-bamberg-archive-filter'), C(cards, css='tb-archive-list'), E('Externe Dokumente bleiben mit ihrer veröffentlichten Originaladresse verlinkt.', size=12)], pad=40))
        elif slug in DISTRICTS:
            content.extend(district_content(slug))
        elif slug == 'ortsverbaende':
            content.append(section([eye('ACHT ORTSVERBÄNDE. EINE STADT.'), H('Wo sind Sie zu Hause?'), E('Jeder Ortsverband hat eine eigene Seite mit Stadtteilvorstellung, Originalbildern, Geschichte und Ansprechpartnern.'), C(district_cards, css='tb-grid tb-grid-2 tb-district-index')], PAPER, pad=45))
        elif slug != 'kontakt': content.extend(generic_content(slug))
        if slug == 'aktuelles-2':
            entries = [('antraege', 'Ausgewählte Stadtratsanträge'), ('asp-bezirk', 'ASP Bezirk – historisches Archiv'),
                       ('city-lights-weihnachten', 'City Lights Weihnachten'), ('stroer_drei', 'Ströer – drei Motive'),
                       ('wesselmann', 'Wesselmann'), ('matino', 'Mitte'), ('city-lights-huml-februar', 'City Lights Huml – Februar'),
                       ('stroeer-kuhn-rudel', 'Ströer – Kuhn / Rudel'), ('city-lights-huml-maerz', 'City Lights Huml – März'),
                       ('2026-2', '2026 – Originalseite'), ('wesselmann-stichwahl', 'Wesselmann Stichwahl – Originalseite')]
            content.append(section([eye('WEITERE ORIGINALINHALTE'), H('Archiv & Transparenz.'),
                E('Zusätzliche öffentliche Seiten der bisherigen Website. Ältere Inhalte und Transparenzangaben bleiben mit ihren ursprünglichen Daten erhalten.'),
                C([C([H(label, 'h3', 22), B('Seite öffnen →', link(target), PALE, NAVY)], css='tb-profile-link')
                   for target, label in entries if target in pages], css='tb-grid tb-grid-3')], pad=50))
        if slug == 'asp-bezirk' or slug in {'city-lights-weihnachten', 'stroer_drei', 'wesselmann', 'matino', 'city-lights-huml-februar', 'stroeer-kuhn-rudel', 'city-lights-huml-maerz', '2026-2', 'wesselmann-stichwahl'}:
            content.insert(1, section([note('Archivinhalt der bisherigen Website. Ursprüngliche Daten, Zeiträume und Verantwortliche sind erhalten; diese Seite beschreibt keine neu geschaltete Anzeige oder aktuell bestätigte Veranstaltung.')], pad=20))
        if slug == 'fraktion':
            content.append(section([note('Die vollständige aktuelle Fraktionsliste wird vor Veröffentlichung ergänzt. Die folgenden Porträts stammen aus dem bisherigen Auftritt und bestätigen keine aktuelle Fraktionszugehörigkeit.')], pad=20))
            content.append(section([eye('PORTRÄTS AUS DEM BISHERIGEN AUFTRITT'), H('Persönliche Vorstellungen.'), C([C(([I(page_picture(p), 'tb-person-image', link(p))] if page_picture(p) else []) + [C([H(pages[p]['title'], 'h3', 22), B('Profil kennenlernen →', link(p), PAPER, NAVY)], css='tb-person-caption')], css='tb-person-card') for p in profile_slugs if p not in LEFT_FRACTION], css='tb-grid tb-grid-3')], PAPER, pad=60))
        if slug == 'kreisvorstand-2':
            content.append(section([row([B('Fachgruppen kennenlernen →', link('fachgruppen')), B('ASP Kreisverband →', link('asp-kreisverband'), PALE, NAVY)], gap=15)], pad=35))
        if slug == 'kontakt':
            original_contacts = [E(sanitise((w.select_one('.elementor-widget-container') or w).decode_contents()), INK, 16) for w in original_text(slug)]
            content.append(section([row([
                C([eye('DER DIREKTE DRAHT'), H('Sagen Sie Hallo.', 'h2', 36),
                   E('Manchmal beginnt ein gutes Gespräch mit einer einfachen Frage. Hier finden Sie die veröffentlichten Kontaktwege.'),
                   C(original_contacts, css='tb-contact-addresses', bg=SAND, pad=28),
                   note('Kontaktangaben aus dem bisherigen Auftritt. Die aktuelle Erreichbarkeit wird vor Veröffentlichung bestätigt.')], width=38, gap=22),
                C([eye('IHRE NACHRICHT'), H('Was liegt Ihnen<br>am Herzen?', 'h2', 36),
                   W('team-bamberg-inquiry', {'email': '', 'button_text': 'Nachricht vorbereiten →', 'privacy_link': {'url': link('datenschutz')}})], width=62, css='tb-contact-form-card', bg='#f8f5ee', pad=35)
            ], gap=55)], PAPER, 'tb-contact-section', pad=48))
        if slug == 'termine':
            content.append(section([row([C([eye('NOCH KEIN PASSENDER TERMIN?'), H('Der erste Schritt:<br>ein Gespräch.', 'h2', 35), E('Eine Frage zur Arbeit vor Ort oder zur Mitgliedschaft? Die Kontaktseite hilft Ihnen weiter.')], width=65), C([B('Zum Kontakt →', link('kontakt'), NAVY, WHITE)], width=35, flex_justify_content='center')], gap=35)], SAND, pad=40))
        if slug not in {'impressum', 'datenschutz', 'kontakt', 'termine', 'spenden'}:
            content.append(section([row([H('Im Gespräch bleiben.', 'h2', 32), B('Kontakt aufnehmen →', link('kontakt'))], gap=30, flex_align_items='center', flex_justify_content='space-between')], '#dbe6e6', css='tb-conversation', pad=35))
        content.append(section([E(f'<p>Originalinhalte: <a href="{html.escape(record["url"])}" target="_blank" rel="noopener noreferrer">team-bamberg.de</a> · Übernommen am 10.10.2026.</p>', size=11)], pad=20))
        save(slug, title, content)

    save('aktuelles', 'Aktuelles', [heading('aktuelles', 'Aktuelles aus Bamberg.', 'Meldungen aus dem Kreisverband und unseren acht Ortsverbänden. Wählen Sie Ihren Stadtteil oder lesen Sie, was Bamberg insgesamt bewegt.'),
        section([W('team-bamberg-news', {'area': 'all', 'limit': 9, 'filters': 'yes', 'empty_title': 'Die nächsten Meldungen folgen.', 'empty_text': 'Neue Beiträge werden vom Kreisverband und den Ortsverbänden veröffentlicht. Bis dahin finden Sie Stadtteilvorstellungen, Ansprechpartner und Originaldokumente auf den jeweiligen Seiten.'})], PAPER, pad=55),
        section([row([C([eye('BAMBERG ZUM NACHLESEN'), H('Was wurde im Stadtrat eingebracht?', 'h2', 37), E('Das Antragsarchiv bewahrt die vorhandenen Dokumente und ihre ursprünglichen Daten.')], width=65), C([B('Anträge & Dokumente →', link('fraktionsantraege'), NAVY, WHITE)], width=35, flex_justify_content='center')], gap=40)], SAND, pad=45)])
    theme_groups = [('Stadtentwicklung & Wohnen', 'Bauen, Wohnen, öffentliche Räume und die Entwicklung unserer Stadt.'), ('Mobilität & Umwelt', 'Wege durch Bamberg, Grünflächen, Klimaschutz und das städtische Umfeld.'), ('Bildung, Kultur & Sport', 'Schulen, kulturelles Leben, Freizeit und die Begegnung in Vereinen.'), ('Familie & Soziales', 'Fragen des Zusammenlebens, der Generationen und der sozialen Infrastruktur.'), ('Wirtschaft & Digitalisierung', 'Arbeiten in Bamberg, lokale Wirtschaft und digitale Angebote.'), ('Finanzen & Verwaltung', 'Kommunale Aufgaben, Haushalt und nachvollziehbare Entscheidungen.')]
    save('themen', 'Themen für Bamberg', [heading('themen', 'Was Bamberg bewegt.', 'Ein Zugang zu Themenfeldern aus der veröffentlichten Fachgruppenübersicht. Konkrete aktuelle Positionen und Vorhaben werden vom Kreisverband ergänzt.'),
        section([C([C([eye('0' + str(i + 1)), H(title, 'h3', 28), E(text), B('Dokumentierte Anträge finden →', link('fraktionsantraege'), PAPER, NAVY)], css='tb-local-topic', bg='#f8f5ee', pad=32) for i, (title, text) in enumerate(theme_groups)], css='tb-grid tb-grid-3')], PAPER, pad=55),
        section([row([C([eye('THEMEN GEMEINSAM VERTIEFEN'), H('Menschen mit Erfahrung.<br>Fragen mit vielen Perspektiven.', 'h2', 40), E('Die vorhandene Fachgruppenübersicht zeigt die thematischen Bereiche des Kreisverbands.')], width=65), C([B('Zu den Fachgruppen →', link('fachgruppen'), NAVY, WHITE), B('Ein Anliegen mitteilen →', link('kontakt'), PAPER, NAVY)], width=35, flex_justify_content='center')], gap=45)], SAND, pad=50)])
    for slug in ['aktuelles', 'themen']:
        data = json.loads((THEME / 'templates' / (slug + '.json')).read_text())
        pages[slug]['text'] = ' '.join(re.findall(r'"(?:title|editor)": "([^"]+)"', json.dumps(data, ensure_ascii=False)))
    manifest = {'version': 1, 'captured_at_utc': inventory['captured_at_utc'], 'palette_source': 'https://www.csu.de/assets/css/csu.min.css',
        'pages': {slug: {'title': ('Anträge & Archiv' if slug == 'fraktionsantraege' else item['title']), 'source_url': item['url'], 'search_text': item['text']} for slug, item in pages.items()},
        'parts': {'header': 'Kopfbereich & Navigation', 'footer': 'Fußbereich'}, 'media': assets,
        'source_exceptions': {'unavailable_images': sorted(set(missing)), 'masked_email_addresses': sorted(set(masked)),
            'external_documents': inventory['external_media'], 'source_capture_errors': inventory['errors'],
            'sitemap_review': inventory.get('sitemap_review', {})},
        'live_source_checks': json.loads(Path(__file__).with_name('source-checks.json').read_text()),
        'personnel_updates': {'reported_at': '2026-10-11', 'source': 'Angabe des Auftraggebers; Zeitungsartikel nicht unabhängig abgerufen', 'left_fraction': sorted(LEFT_FRACTION), 'party_membership': 'Keine Änderung aus Fraktionsaustritt abgeleitet'},
        'design_references': {'requested': ['https://www.spd-bamberg-stadt.de/', 'https://afd-bamberg.de/'], 'retrieval': 'Beide exakten Adressen vom Cloud-Netzwerkproxy gesperrt; keine direkte Sichtprüfung behauptet', 'applied_direction': 'Große lokale Bilder, optionales eigenes Video, klare Navigation und Meldungen'},
        'review_notes': ['Aktuelle vollständige Fraktionsliste, Personen und Funktionen bestätigen.', 'Veröffentlichte E-Mail-Adressen sind teilweise verschleiert; nicht erraten.', 'IBAN ohne Länderkennung auf der Originalseite: vor Verwendung bestätigen.', 'Datenschutzerklärung Stand Mai 2018: an neuen Betrieb anpassen.', 'Terminangabe ohne Jahr: nicht als zukünftiges Ereignis übernommen.', 'Originalfoto Andreas Dechant nicht abrufbar; kein Ersatzporträt erfunden.']}
    manifest['source_link_corrections'] = {'unavailable_membership_pdf': DEAD_MEMBERSHIP_PDF, 'replacement': 'https://www.csu.de/jetzt-mitmachen/', 'malformed_privacy_links': 'Entfernt den versehentlichen CSU-URL-Präfix vor zwei Google-Adressen; Rechtstext bleibt zur Prüfung markiert.'}
    (THEME / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (PROJECT / 'QUELLEN.json').write_text(json.dumps({k: v for k, v in manifest.items() if k not in {'media', 'pages', 'parts'}}, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(pages)} native Elementor pages, 2 shared sections and {len(assets)} original media files.')


if __name__ == '__main__': main()
