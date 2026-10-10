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

from bs4 import BeautifulSoup

PROJECT = Path(__file__).resolve().parents[1]
THEME = PROJECT / 'team-bamberg-elementor'
BLUE, NAVY, PALE, INK, MUTED, WHITE, LIME = '#0080c8', '#112b4b', '#e5f2f8', '#142b43', '#566779', '#ffffff', '#a2c516'
counter = 0
assets = {}
missing = []
masked = []
source_root = None
media_by_url = {}
pages = {}


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
        'text_padding': dims(18, 25), 'border_radius': dims(7), 'align': 'left', '_element_width': 'auto'})


def C(children, direction='column', css='', bg=None, width=100, pad=0, gap=24, **extra):
    s = {'content_width': 'full', 'flex_direction': direction, 'flex_direction_mobile': 'column',
         'width': {'unit': '%', 'size': width}, 'width_mobile': {'unit': '%', 'size': 100},
         'padding': pad if isinstance(pad, dict) else dims(pad), 'padding_mobile': dims(0),
         'flex_gap': {'unit': 'px', 'size': gap, 'column': str(gap), 'row': str(gap), 'isLinked': True},
         'flex_align_items': 'stretch', 'css_classes': css}
    if bg: s.update(background_background='classic', background_color=bg)
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
    parsed = urllib.parse.urlsplit(url)
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
            if old.get('href', '').startswith('mailto:') and '*' in old.get('href', ''):
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
    return section(children, '#f3f7fa', css='tb-page-title', pad=55)


def note(text): return E(text, color='#75571c', size=13, css='tb-source-note')


def convert_widget(widget, slug):
    kind = widget.get('data-widget_type', '').split('.')[0]
    body = widget.select_one('.elementor-widget-container') or widget
    if kind == 'image':
        img = body.find('img')
        if not img or 'CSU_Logo' in img.get('src', ''): return []
        url = image_source(img)
        key = add_asset(url, img.get('alt') or pages[slug]['title'])
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
        text = sanitise(title.decode_contents())
        return [H(text, 'h3', 26)] if title.get_text(strip=True) else []
    if kind == 'text-editor':
        text = sanitise(body.decode_contents())
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
            if content: children.append(C(content, css='tb-content-card' if len(groups) > 1 else 'tb-content-block'))
        if children:
            result.append(section([C(children, css='tb-grid tb-grid-' + str(min(len(children), 4)))], pad=30))
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
    THEME.joinpath('assets/media').mkdir(parents=True, exist_ok=True)
    THEME.joinpath('templates').mkdir(parents=True, exist_ok=True)
    logo_url = 'https://team-bamberg.de/wp-content/uploads/2020/11/CSU_Logo_1c_neg-300x69.png'
    logo = add_asset(logo_url, 'CSU – Christlich-Soziale Union')
    hero = add_asset('https://team-bamberg.de/wp-content/uploads/2020/11/AdobeStock_97121734-11-2048x1041.jpg', 'Altes Rathaus in Bamberg an der Regnitz')
    city = add_asset('https://team-bamberg.de/wp-content/uploads/2020/12/AdobeStock_193611934-11-scaled-1536x1025.jpg', 'Bamberg – Foto aus der bisherigen Website')
    save('header', 'Kopfbereich & Navigation', [
        section([row([E('CSU BAMBERG-STADT · NÄHER AM MENSCHEN', '#d5e7f2', 10), E(f'<p><a href="{link("mandatstraeger")}">Mandatsträger</a> <span>·</span> <a href="{link("spenden")}">Spenden</a></p>', '#d5e7f2', 11)], flex_justify_content='space-between')], NAVY, 'tb-topbar', pad=8, padding_mobile=dims(8, 20)),
        section([row([C([row([C([I(logo, 'tb-logo', link('startseite'))], width=43, bg=BLUE, pad=dims(14, 16)), C([H('Bamberg', 'p', 24)], width=53)], gap=10, flex_align_items='center', flex_direction_mobile='row')], width=28, width_mobile={'unit': '%', 'size': 76}), C([W('team-bamberg-navigation', {'items': [
            {'_id': uid(), 'label': label, 'link': {'url': link(slug)}} for slug, label in [
                ('kreisvorstand-2', 'Über uns'), ('ortsverbaende', 'Vor Ort'), ('fraktion', 'Stadtrat'), ('termine', 'Termine'), ('kontakt', 'Kontakt')]]})], width=72, width_mobile={'unit': '%', 'size': 24}, flex_align_items='flex-end')], flex_align_items='center', flex_direction_mobile='row', gap=18)], WHITE, 'tb-header-main', pad=22, padding_mobile=dims(16, 20))
    ])
    footer_links = [('CSU Bamberg', [('kreisvorstand-2', 'Kreisverband'), ('ortsverbaende', 'Ortsverbände'), ('fachgruppen', 'Fachgruppen'), ('asp-kreisverband', 'ASP Kreisverband')]),
                    ('Politik & Menschen', [('fraktion', 'Stadtratsfraktion'), ('mandatstraeger', 'Mandatsträger'), ('fraktionsantraege', 'Anträge & Archiv'), ('aktuelles-2', 'Archiv & Transparenz'), ('termine', 'Termine')]),
                    ('Mitmachen', [('mitglied-werden', 'Mitglied werden'), ('spenden', 'Spenden'), ('kontakt', 'Kontakt')])]
    columns = [C([I(logo, 'tb-footer-logo', link('startseite')), H('Bamberg gestalten.', 'h3', 25, WHITE), E('Näher am Menschen.', '#adc1d4', 14)], width=30)]
    for title, links in footer_links:
        columns.append(C([eye(title, '#adc1d4'), E(''.join(f'<p><a href="{link(slug)}">{label}</a></p>' for slug, label in links), WHITE, 13)], width=23))
    save('footer', 'Fußbereich', [section([row(columns, css='tb-footer-columns', gap=40), row([
        E('Gestaltungsentwurf · Inhalte aus team-bamberg.de · Übernahme: 10.10.2026', '#adc1d4', 11),
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
    home = [section([row([
        C([eye('CSU BAMBERG-STADT'), H('Bamberg.<br><span style="color:#0080c8">gestalten.</span>', 'h1', 86), E('Unsere Stadt. Unsere Menschen. Unser gemeinsames Morgen.', size=19),
           row([B('Unser Team kennenlernen →', link('kreisvorstand-2')), B('Vor Ort entdecken →', link('ortsverbaende'), PALE, NAVY)], gap=12), E('WELTKULTURERBE. HEIMAT. ZUKUNFT.', size=10, css='tb-hero-foot')], width=45, flex_justify_content='center', gap=25),
        C([I(hero, 'tb-hero-image'), row([E('Näher am Menschen.', INK, 13), E('BAMBERG-STADT', BLUE, 10)], css='tb-photo-caption', flex_justify_content='space-between', flex_direction_mobile='row')], width=55, gap=15)], gap=65)], '#f8fafc', 'tb-hero', pad=65),
        section([C([C([eye(num), H(title, 'h3', 23), E(text, size=14), B('Entdecken →', link(slug), WHITE, BLUE)], css='tb-quick-card', gap=15) for num, title, text, slug in [
            ('01 · MENSCHEN', 'Ein Team für Bamberg.', 'Kreisverband, Fachgruppen und Ansprechpartner.', 'kreisvorstand-2'),
            ('02 · STADTTEILE', 'Ganz nah. Vor Ort.', 'Acht Ortsverbände in unserer Stadt.', 'ortsverbaende'),
            ('03 · STADTRAT', 'Politik zum Nachlesen.', 'Fraktion, Anträge und Dokumente im Überblick.', 'fraktionsantraege')]], css='tb-grid tb-grid-3')], WHITE, pad=40),
        section([row([C([I(city, 'tb-about-image')], width=45), C([eye('UNSER BAMBERG'), H('Besondere Stadt.<br>Gemeinsames Morgen.'), E(sanitise((about.select_one('.elementor-widget-container') or about).decode_contents())), B('Die CSU Bamberg kennenlernen →', link('kreisvorstand-2'))], width=55, flex_justify_content='center')], gap=70)], pad=85),
        section([row([C([eye('IN IHREM STADTTEIL'), H('Bamberg hat viele Gesichter.')], width=72), C([B('Alle Ortsverbände →', link('ortsverbaende'), WHITE, BLUE)], width=28, flex_justify_content='flex-end')]), C(district_cards, css='tb-grid tb-grid-4')], '#f3f7fa', pad=75),
        section([row([C([eye('IM BAMBERGER STADTRAT', '#b9def4'), H('Menschen hinter<br>der Stadtpolitik.', 'h2', 46, WHITE), E('Die politische Arbeit der CSU-Fraktion im Bamberger Stadtrat.', '#d5e7f2'), row([B('Zur Stadtratsfraktion →', link('fraktion'), WHITE, NAVY), B('Mandatsträger →', link('mandatstraeger'), '#234864', WHITE)], gap=15)], width=60), C([eye('NACHLESEN STATT SUCHEN', '#b9def4'), H('Anträge.<br>Dokumente.<br>Einblicke.', 'h3', 33, WHITE), B('Zum Antragsarchiv →', link('fraktionsantraege'), LIME, NAVY)], width=40, css='tb-politics-side')], gap=70)], NAVY, pad=70),
        section([row([C([eye('BEGEGNEN & AUSTAUSCHEN'), H('Termine im Überblick.')], width=55), C([W('team-bamberg-events', {'source': 'shared', 'single': 'yes', 'empty_title': 'Neue Termine folgen.', 'empty_text': 'Bestätigte kommende Veranstaltungen werden hier veröffentlicht.'}), B('Zur Terminübersicht →', link('termine'), PALE, NAVY)], width=45)], gap=80)], pad=75),
        section([row([C([eye('MITMACHEN', WHITE), H('Mitmachen.<br>Mitgestalten.', 'h2', 48, WHITE), E('Die CSU Bamberg kennenlernen und sich einbringen.', '#e5f2f8')], width=65), C([B('Mitglied werden →', link('mitglied-werden'), WHITE, NAVY), B('Kontakt aufnehmen →', link('kontakt'), NAVY, WHITE)], width=35, flex_justify_content='center')], gap=45)], BLUE, pad=60)]
    save('startseite', 'Startseite', home)

    descriptions = {'kreisvorstand-2': 'Kreisvorstand, Ansprechpartner und die Organisation der CSU Bamberg.',
                    'ortsverbaende': 'Acht Ortsverbände. Die CSU in den Bamberger Stadtteilen.',
                    'fraktion': 'Menschen und Arbeit der CSU-Stadtratsfraktion.',
                    'mandatstraeger': 'Die auf der bisherigen Website vorgestellten Mandatsträger.',
                    'fachgruppen': 'Thematische Fachgruppen der Bamberger CSU.',
                    'kontakt': 'Geschäftsstelle, Stadtratsfraktion und Ihre Nachricht.',
                    'fraktionsantraege': 'Dokumente und Anträge aus der bisherigen Website – mit ihren ursprünglichen Daten.'}
    profile_slugs = ['andeas-dechant', 'dr-franz-wilhelm-heller', 'michael-kalb', 'stefan-kuhn', 'dr-christian-lange', 'peter-neller', 'anna-niedermaier', 'dr-ursula-redler', 'anne-rudel', 'prof-dr-gerhard-seitz', 'you-xie']
    for slug, record in pages.items():
        if slug == 'startseite': continue
        title = 'Anträge & Archiv' if slug == 'fraktionsantraege' else record['title']
        content = [heading(slug, title, descriptions.get(slug, ''))]
        if slug in {'kreisvorstand-2', 'fraktion', 'mandatstraeger'} or slug in profile_slugs or slug.startswith('csu-'):
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
        else: content.extend(generic_content(slug))
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
            content.append(section([eye('DIE VORGESTELLTEN PERSONEN'), H('Gesichter der Fraktion.'), C([C([H(pages[p]['title'], 'h3', 22), B('Profil ansehen →', link(p), PALE, NAVY)], css='tb-profile-link') for p in profile_slugs], css='tb-grid tb-grid-3')], '#f3f7fa', pad=60))
        if slug == 'kreisvorstand-2':
            content.append(section([row([B('Fachgruppen kennenlernen →', link('fachgruppen')), B('ASP Kreisverband →', link('asp-kreisverband'), PALE, NAVY)], gap=15)], pad=35))
        if slug == 'kontakt':
            content.append(section([H('Ihre Nachricht vorbereiten'), W('team-bamberg-inquiry', {'email': '', 'privacy_link': {'url': link('datenschutz')}})], '#f3f7fa', pad=55))
        if slug not in {'impressum', 'datenschutz', 'kontakt', 'termine', 'spenden'}:
            content.append(section([row([H('Im Gespräch bleiben.', 'h2', 32), B('Kontakt aufnehmen →', link('kontakt'))], gap=30, flex_align_items='center', flex_justify_content='space-between')], PALE, pad=35))
        content.append(section([E(f'<p>Originalinhalte: <a href="{html.escape(record["url"])}" target="_blank" rel="noopener noreferrer">team-bamberg.de</a> · Übernommen am 10.10.2026.</p>', size=11)], pad=20))
        save(slug, title, content)

    manifest = {'version': 1, 'captured_at_utc': inventory['captured_at_utc'], 'palette_source': 'https://www.csu.de/assets/css/csu.min.css',
        'pages': {slug: {'title': ('Anträge & Archiv' if slug == 'fraktionsantraege' else item['title']), 'source_url': item['url'], 'search_text': item['text']} for slug, item in pages.items()},
        'parts': {'header': 'Kopfbereich & Navigation', 'footer': 'Fußbereich'}, 'media': assets,
        'source_exceptions': {'unavailable_images': sorted(set(missing)), 'masked_email_addresses': sorted(set(masked)),
            'external_documents': inventory['external_media'], 'source_capture_errors': inventory['errors'],
            'sitemap_review': inventory.get('sitemap_review', {})},
        'review_notes': ['Personen und Funktionen bestätigen.', 'Veröffentlichte E-Mail-Adressen sind teilweise verschleiert; nicht erraten.', 'IBAN ohne Länderkennung auf der Originalseite: vor Verwendung bestätigen.', 'Datenschutzerklärung Stand Mai 2018: an neuen Betrieb anpassen.', 'Terminangabe ohne Jahr: nicht als zukünftiges Ereignis übernommen.', 'Originalfoto Andreas Dechant nicht abrufbar; kein Ersatzporträt erfunden.']}
    (THEME / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (PROJECT / 'QUELLEN.json').write_text(json.dumps({k: v for k, v in manifest.items() if k not in {'media', 'pages', 'parts'}}, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(pages)} native Elementor pages, 2 shared sections and {len(assets)} original media files.')


if __name__ == '__main__': main()
