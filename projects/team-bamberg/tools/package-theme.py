#!/usr/bin/env python3
"""Package the standalone WordPress theme, excluding sources and test credentials."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / 'team-bamberg-elementor'
OUTPUT = ROOT / 'releases/team-bamberg-elementor.zip'


def main():
    manifest = json.loads((THEME / 'manifest.json').read_text())
    for item in manifest['media'].values():
        path = THEME / 'assets/media' / item['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise SystemExit('Original media checksum mismatch: ' + item['file'])
    for slug in list(manifest['pages']) + list(manifest['parts']):
        data = json.loads((THEME / 'templates' / (slug + '.json')).read_text())
        if not data.get('content'): raise SystemExit('Missing Elementor content: ' + slug)
    OUTPUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(THEME.rglob('*')):
            if not path.is_file(): continue
            if path.suffix not in {'.php', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.webp', '.pdf'}:
                raise SystemExit('Unexpected package file: ' + str(path))
            info = zipfile.ZipInfo('team-bamberg-elementor/' + str(path.relative_to(THEME)), date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None: raise SystemExit('Theme ZIP is damaged.')
        if 'team-bamberg-elementor/style.css' not in archive.namelist(): raise SystemExit('Theme root is missing.')
    print(f'Installable WordPress theme: {OUTPUT.name}, {OUTPUT.stat().st_size:,} bytes.')


if __name__ == '__main__': main()
