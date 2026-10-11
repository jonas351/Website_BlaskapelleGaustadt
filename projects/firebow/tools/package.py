#!/usr/bin/env python3
"""Rebuild templates and create the installable WordPress theme ZIP."""
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(['python', str(ROOT / 'tools/build-templates.py')], check=True)
theme = ROOT / 'firebow-elementor'
target = ROOT / 'releases/firebow-elementor.zip'
target.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(theme.rglob('*')):
        if not path.is_file():
            continue
        entry = zipfile.ZipInfo(str(path.relative_to(theme.parent)))
        entry.create_system = 3
        entry.external_attr = 0o100644 << 16
        entry.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(entry, path.read_bytes())
print(f'WordPress-Theme: {target.name}, {target.stat().st_size:,} Bytes')
