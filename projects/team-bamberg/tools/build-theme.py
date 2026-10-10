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
                ('kreisvorstand-2', 'Menschen'), ('ortsverbaende', 'Vor Ort'), ('fraktion', 'Stadtrat'), ('termine', 'Termine'), ('kontakt', 'Kontakt')]]})], width=72, width_mobile={'unit': '%', 'size': 24}, flex_align_items='flex-end')], flex_align_items='center', flex_direction_mobile='row', gap=18)], PAPER, 'tb-header-main', pad=22, padding_mobile=dims(16, 20))
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
    featured = ['anna-niedermaier', 'dr-christian-lange', 'anne-rudel', 'you-xie']
    people_cards = [C([I(page_picture(p), 'tb-person-image', link(p)), C([
        H(pages[p]['title'], 'h3', 23), B('Persönlich kennenlernen →', link(p), PAPER, NAVY)], css='tb-person-caption', gap=14)], css='tb-person-card', gap=0) for p in featured]
    home = [section([I(hero, 'tb-hero-backdrop'), C([
        eye('HIER SIND WIR ZU HAUSE.', '#dcebb3'),
        H('Für Bamberg.<br>Mit Menschen.', 'h1', 82, WHITE),
        E('Zwischen Regnitz und Michaelsberg, in unseren Stadtteilen und mitten im Alltag: Lernen Sie die CSU Bamberg und die Menschen dahinter kennen.', '#e6e9e6', 19),
        row([B('Die Menschen kennenlernen →', link('kreisvorstand-2'), LIME, NAVY), B('In Ihrem Stadtteil →', link('ortsverbaende'), '#254361', WHITE)], gap=12),
        E('CSU BAMBERG-STADT · NÄHER AM MENSCHEN', '#dae3e8', 10, 'tb-hero-foot')
    ], css='tb-hero-copy', width=62, gap=28), E('Bamberg an der Regnitz · Altes Rathaus', '#e3e8eb', 11, 'tb-hero-caption')], NAVY, 'tb-hero', pad=78),
        section([row([C([eye('UNSERE STADT. UNSER MITEINANDER.'), H('Bamberg ist mehr<br>als eine Adresse.'),
            E(sanitise((about.select_one('.elementor-widget-container') or about).decode_contents())),
            B('Unseren Kreisverband entdecken →', link('kreisvorstand-2'), NAVY, WHITE)], width=55, flex_justify_content='center'),
            C([I(city, 'tb-about-image'), E('Vertraute Orte. Unterschiedliche Perspektiven. Ein gemeinsames Bamberg.', '#4c5d60', 13)], width=45)], gap=65)], PAPER, 'tb-home-about', pad=68),
        section([row([C([eye('PERSÖNLICH KENNENLERNEN'), H('Politik hat Gesichter.'), E('Wer steckt hinter den Namen? Entdecken Sie die Porträts und persönlichen Vorstellungen aus dem Team-Bamberg-Auftritt.')], width=72),
                     C([B('Zum ganzen Team →', link('fraktion'), NAVY, WHITE)], width=28, flex_justify_content='center')], gap=35),
                 C(people_cards, css='tb-grid tb-grid-4'), E('Porträts aus der bisherigen Website. Aktuelle Funktionen werden vor Veröffentlichung abgeglichen.', '#5b625d', 12)], SAND, 'tb-people-section', pad=65),
        section([row([C([eye('ACHT ORTSVERBÄNDE', '#c5dfef'), H('Ihr Stadtteil.<br>Ihr Bamberg.', 'h2', 49, WHITE),
            E('Vom Berggebiet bis zur Gartenstadt, von Gaustadt bis zur Wunderburg: Hier finden Sie den Ortsverband in Ihrer Nähe.', '#d8e4e9')], width=72),
            C([B('Alle Ortsverbände →', link('ortsverbaende'), LIME, NAVY)], width=28, flex_justify_content='center')], gap=35), C(district_cards, css='tb-grid tb-grid-4')], NAVY, 'tb-district-section', pad=65),
        section([row([C([eye('WAS PASSIERT IM STADTRAT?'), H('Stadtpolitik.<br>Zum Nachlesen.'), E('Welche Themen wurden eingebracht? Wer gehört zum vorgestellten Team? Die Fraktionsseiten und das Antragsarchiv machen die bisherige Arbeit zugänglich.'), B('Zur Stadtratsfraktion →', link('fraktion'), NAVY, WHITE)], width=52),
            C([C([eye('ANTRÄGE & DOKUMENTE'), H('Ein Thema suchen.<br>Mehr erfahren.', 'h3', 31), E('Originalanträge mit Datum, Dokumenten und einer Suche nach Thema und Jahr.'), B('Im Archiv stöbern →', link('fraktionsantraege'))], css='tb-feature-card', bg=SAND, pad=34),
               C([H('Im Gespräch bleiben.', 'h3', 24), E('Eine Frage, eine Idee oder ein Anliegen aus Ihrem Stadtteil? Hier geht es zum Kontakt.'), B('Kontakt aufnehmen →', link('kontakt'), PAPER, NAVY)], css='tb-feature-card', bg='#dae5df', pad=30)], width=48)], gap=65)], PAPER, pad=65),
        section([row([C([eye('BEGEGNEN & AUSTAUSCHEN'), H('Manches bespricht<br>sich besser persönlich.'), E('Hier finden Sie bestätigte kommende Veranstaltungen. Bis dahin können Sie über die Kontaktseite den Austausch suchen.')], width=55), C([W('team-bamberg-events', {'source': 'shared', 'single': 'yes', 'empty_title': 'Wann sehen wir uns?', 'empty_text': 'Neue bestätigte Termine finden Sie hier, sobald sie feststehen.'}), B('Zur Terminübersicht →', link('termine'), NAVY, WHITE)], width=45)], gap=65)], '#dbe6e6', pad=60),
        section([row([C([eye('LUST, BAMBERG MITZUGESTALTEN?', '#dcebb3'), H('Gute Gespräche.<br>Neue Begegnungen.', 'h2', 48, WHITE), E('Ob Sie erst einmal eine Frage stellen oder sich über eine Mitgliedschaft informieren möchten: Finden Sie Ihren Einstieg.', '#d5e7f2')], width=65), C([B('Mitgliedschaft kennenlernen →', link('mitglied-werden'), LIME, NAVY), B('Sagen Sie Hallo →', link('kontakt'), '#254361', WHITE)], width=35, flex_justify_content='center')], gap=45)], NAVY, 'tb-join-section', pad=60)]
    save('startseite', 'Startseite', home)

    descriptions = {
        'kreisvorstand-2': 'Eine Stadt, viele Menschen. Hier lernen Sie den Kreisverband, seine Organisation und die auf der bisherigen Website vorgestellten Ansprechpartner kennen.',
        'ortsverbaende': 'Bamberg beginnt vor der eigenen Haustür. Entdecken Sie unsere acht Ortsverbände und die Menschen in Ihrem Stadtteil.',
        'fraktion': 'Vom persönlichen Anliegen bis zum Stadtratsantrag: Hier finden Sie das vorgestellte Team der Fraktion, Kontaktmöglichkeiten und dokumentierte politische Arbeit.',
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
        descriptions[slug] = f'Zu Hause in {label}. Lernen Sie den Ortsverband, die vorgestellten Menschen und die Kontaktmöglichkeiten aus dem bisherigen Auftritt kennen.'
    profile_slugs = PROFILE_SLUGS
    for slug in profile_slugs:
        descriptions[slug] = 'Ein persönlicher Blick auf den Menschen hinter dem Namen: die Vorstellung, Schwerpunkte und Kontaktangaben aus dem bisherigen Team-Bamberg-Auftritt.'
    for slug, record in pages.items():
        if slug == 'startseite': continue
        title = 'Anträge & Archiv' if slug == 'fraktionsantraege' else record['title']
        content = [heading(slug, title, descriptions.get(slug, 'Originalunterlagen und Transparenzangaben zum Nachlesen. Diese Archivseite bewahrt die veröffentlichten Informationen und ihre ursprünglichen Zeiträume.'))]
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
            content.append(section([eye('DIE VORGESTELLTEN PERSONEN'), H('Gesichter der Fraktion.'), C([C(([I(page_picture(p), 'tb-person-image', link(p))] if page_picture(p) else []) + [C([H(pages[p]['title'], 'h3', 22), B('Profil kennenlernen →', link(p), PAPER, NAVY)], css='tb-person-caption')], css='tb-person-card') for p in profile_slugs], css='tb-grid tb-grid-3')], '#f3f7fa', pad=60))
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
