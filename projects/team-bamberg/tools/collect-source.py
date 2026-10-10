#!/usr/bin/env python3
"""Inventory public site content and original media without executing page code."""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ORIGIN = 'https://team-bamberg.de/'
HOSTS = {'team-bamberg.de', 'www.team-bamberg.de'}
MEDIA = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif', '.svg', '.pdf', '.mp4', '.mp3', '.doc', '.docx', '.zip', '.pptx', '.xlsx'}
STYLE_URL = re.compile(r'url\(\s*[\"\']?([^\"\')]+)', re.I)


def normalise(value: str, base: str) -> str | None:
    value = value.strip()
    if not value or value.startswith(('data:', 'mailto:', 'tel:', 'javascript:', '#')):
        return None
    result = urllib.parse.urlsplit(urllib.parse.urljoin(base, value))
    if result.scheme not in {'http', 'https'} or result.username or result.password:
        return None
    if result.port not in {None, 80, 443}:
        return None
    query = '&'.join(part for part in result.query.split('&')
                     if not urllib.parse.unquote(part.split('=', 1)[0]).lower().startswith('utm_')
                     and urllib.parse.unquote(part.split('=', 1)[0]).lower() not in {'fbclid', 'gclid'})
    path = urllib.parse.quote(result.path or '/', safe="/%:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(query, safe="%/?@!$&'()*+,;=:-._~")
    return urllib.parse.urlunsplit((result.scheme, result.netloc.lower(), path, query, ''))


def internal(url: str) -> bool:
    return urllib.parse.urlsplit(url).hostname in HOSTS


def public_page(url: str) -> bool:
    parts = urllib.parse.urlsplit(url)
    if any(x in parts.path.lower() for x in ('/wp-admin', '/wp-login', '/wp-json', '/feed', '/xmlrpc.php')):
        return False
    query = dict(urllib.parse.parse_qsl(parts.query))
    if any(x in query for x in ('s', 'replytocom', 'add-to-cart', 'preview', 'action')):
        return False
    suffix = Path(parts.path).suffix.lower()
    return suffix in {'', '.html', '.htm', '.php'}


class SourcePage(HTMLParser):
    def __init__(self, url: str):
        super().__init__(convert_charrefs=True)
        self.url = url
        self.links: set[str] = set()
        self.media: dict[str, str] = {}
        self.text: list[str] = []
        self.title: list[str] = []
        self.title_depth = 0
        self.hidden = 0
        self.dates: list[dict] = []

    def add_media(self, value: str, alt: str = '') -> None:
        url = normalise(value, self.url)
        if url:
            self.media.setdefault(url, alt)

    def handle_starttag(self, tag: str, attributes: list) -> None:
        attrs = dict(attributes)
        if tag in {'script', 'style', 'noscript'}:
            self.hidden += 1
        if tag == 'title':
            self.title_depth += 1
        if tag == 'a':
            url = normalise(attrs.get('href') or '', self.url)
            if url:
                self.links.add(url)
                if Path(urllib.parse.urlsplit(url).path).suffix.lower() in MEDIA:
                    self.media.setdefault(url, '')
        if tag in {'img', 'source', 'video', 'audio'}:
            for key in ('src', 'data-src', 'data-lazy-src', 'poster'):
                if attrs.get(key):
                    self.add_media(attrs[key], attrs.get('alt') or '')
            for key in ('srcset', 'data-srcset', 'data-lazy-srcset'):
                for entry in (attrs.get(key) or '').split(','):
                    bits = entry.strip().split()
                    if bits:
                        self.add_media(bits[0], attrs.get('alt') or '')
        for value in STYLE_URL.findall(attrs.get('style') or ''):
            self.add_media(value)
        if tag == 'meta' and attrs.get('property') in {'og:image', 'og:image:url'}:
            self.add_media(attrs.get('content') or '')
        if tag == 'time':
            self.dates.append({'datetime': attrs.get('datetime') or ''})

    def handle_endtag(self, tag: str) -> None:
        if tag in {'script', 'style', 'noscript'}:
            self.hidden = max(0, self.hidden - 1)
        if tag == 'title':
            self.title_depth = max(0, self.title_depth - 1)

    def handle_data(self, value: str) -> None:
        if self.hidden:
            return
        value = ' '.join(value.split())
        if value:
            self.text.append(value)
            if self.title_depth:
                self.title.append(value)


class OriginRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = normalise(newurl, req.full_url)
        if not target or not internal(target):
            raise urllib.error.HTTPError(req.full_url, code, 'External redirect requires separate review', headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-pages', type=int, default=300)
    parser.add_argument('--max-media', type=int, default=1200)
    args = parser.parse_args()
    if args.max_pages < 1 or args.max_media < 1:
        parser.error('Limits must be positive.')
    root = args.output.resolve()
    (root / 'pages').mkdir(parents=True, exist_ok=True)
    (root / 'media').mkdir(exist_ok=True)
    opener = urllib.request.build_opener(OriginRedirects())
    queue = deque([ORIGIN])
    seen: set[str] = set()
    wanted_media: dict[str, dict] = {}
    report = {'origin': ORIGIN, 'captured_at_utc': datetime.now(timezone.utc).isoformat(),
              'pages': [], 'media': [], 'external_media': [], 'external_links': [],
              'errors': [], 'unvisited_pages': [], 'undownloaded_media': [],
              'status': 'incomplete', 'scope': 'Public linked pages; no claim of private or unlinked content completeness.'}
    external_links: set[str] = set()

    def fetch(url: str, limit: int):
        request = urllib.request.Request(url, headers={'User-Agent': 'TeamBambergRedesignInventory/1.0 (public-content review)'})
        with opener.open(request, timeout=25) as response:
            body = response.read(limit + 1)
            if len(body) > limit:
                raise ValueError(f'Resource exceeds {limit} byte capture limit')
            return body, response.url, response.headers.get_content_type(), response.headers.get_content_charset() or 'utf-8'

    def store(body: bytes, group: str, url: str, suffix: str):
        name = hashlib.sha256(url.encode()).hexdigest()[:24] + suffix
        relative = f'{group}/{name}'
        (root / relative).write_bytes(body)
        return {'file': relative, 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}

    # Include public pages outside the main menu, including older transparency pages.
    # The post sitemap is inventoried separately: unrelated posts require review.
    report['sitemaps'] = {}
    for kind in ('page', 'post'):
        sitemap_url = ORIGIN + 'wp-sitemap-posts-' + kind + '-1.xml'
        try:
            body, _, mime, _ = fetch(sitemap_url, 1024 * 1024)
            urls = [element.text for element in ET.fromstring(body).iter() if element.tag.endswith('loc') and element.text]
            report['sitemaps'][kind] = {'url': sitemap_url, 'urls': urls}
            if kind == 'page':
                for target in urls:
                    target = normalise(target, ORIGIN)
                    if target and internal(target) and public_page(target): queue.append(target)
        except (urllib.error.URLError, ValueError, OSError, ET.ParseError) as error:
            report['sitemaps'][kind] = {'url': sitemap_url, 'error': str(error)}

    while queue and len(seen) < args.max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            body, resolved, mime, charset = fetch(url, 10 * 1024 * 1024)
            if mime not in {'text/html', 'application/xhtml+xml'}:
                raise ValueError(f'Expected a public HTML page, got {mime}')
            source = SourcePage(resolved)
            source.feed(body.decode(charset, errors='replace'))
            page = {'url': url, 'resolved_url': resolved, 'title': ' '.join(source.title),
                    'text': '\n'.join(source.text), 'dates_as_published': source.dates,
                    'links': sorted(source.links), 'media': sorted(source.media), **store(body, 'pages', url, '.html')}
            report['pages'].append(page)
            for target in sorted(source.links):
                if not internal(target):
                    external_links.add(target)
                elif public_page(target) and target not in seen:
                    queue.append(target)
            for target, alt in source.media.items():
                item = wanted_media.setdefault(target, {'url': target, 'alt_as_published': alt, 'source_pages': []})
                item['source_pages'].append(url)
            print(f'Page {len(report["pages"])}: {url}')
        except (urllib.error.URLError, ValueError, LookupError, OSError) as error:
            report['errors'].append({'url': url, 'stage': 'page', 'error': str(error)})
            print(f'Capture failed: {url}: {error}')
        time.sleep(0.15)

    report['unvisited_pages'] = sorted(set(queue) - seen)
    report['external_links'] = sorted(external_links)
    count = 0
    for url, item in wanted_media.items():
        if not internal(url):
            report['external_media'].append(item)
            continue
        if count >= args.max_media:
            report['undownloaded_media'].append(item)
            continue
        count += 1
        try:
            body, resolved, mime, _ = fetch(url, 25 * 1024 * 1024)
            if not (mime.startswith(('image/', 'audio/', 'video/')) or mime in {
                    'application/pdf', 'application/zip', 'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}):
                raise ValueError(f'Unsupported media type {mime}')
            suffix = Path(urllib.parse.urlsplit(resolved).path).suffix.lower()
            if suffix not in MEDIA:
                suffix = '.bin'
            report['media'].append({**item, 'resolved_url': resolved, 'mime': mime, **store(body, 'media', url, suffix)})
        except (urllib.error.URLError, ValueError, LookupError, OSError) as error:
            report['errors'].append({'url': url, 'stage': 'media', 'error': str(error)})
        time.sleep(0.1)
    if report['pages'] and not any(report[key] for key in ('errors', 'external_media', 'unvisited_pages', 'undownloaded_media')):
        report['status'] = 'captured_linked_public_content'
    (root / 'inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'Captured {len(report["pages"])} pages and {len(report["media"])} media files. Status: {report["status"]}.')
    return 0 if report['status'] == 'captured_linked_public_content' else 1


if __name__ == '__main__':
    raise SystemExit(main())
