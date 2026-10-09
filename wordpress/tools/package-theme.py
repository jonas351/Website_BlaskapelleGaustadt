#!/usr/bin/env python3
"""Build the WordPress upload ZIP without credentials, dependencies or test data."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
theme = root / 'gaustadt-elementor'
out = root / 'releases' / 'gaustadt-elementor.zip'
required = ['style.css', 'index.php', 'functions.php', 'templates/startseite.json', 'templates/footer.json', 'assets/brass.png']
for item in required:
    if not (theme / item).is_file(): raise SystemExit('Missing required theme file: '+item)
out.parent.mkdir(exist_ok=True)
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for source in sorted(theme.rglob('*')):
        if not source.is_file(): continue
        relative = source.relative_to(theme)
        if any(part.startswith('.') for part in relative.parts): continue
        info = ZipInfo(str(Path('gaustadt-elementor') / relative), date_time=(2026,10,9,0,0,0))
        info.external_attr = 0o100644 << 16
        info.compress_type = ZIP_DEFLATED
        archive.writestr(info, source.read_bytes())
with ZipFile(out) as archive:
    if archive.testzip() is not None: raise SystemExit('ZIP integrity check failed')
print('WordPress theme ZIP:', out, f'({out.stat().st_size} bytes)')
