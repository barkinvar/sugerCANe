"""Record source provenance and hashes without claiming a missing file was read."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
sources = ROOT / 'sources'
urls = json.loads((sources / 'provenance_urls.json').read_text())
records = []
for path in sorted(sources.rglob('*')):
    if not path.is_file() or path.name in ('source_manifest.json', 'provenance_urls.json'):
        continue
    relative = path.relative_to(ROOT).as_posix()
    if 'models/lm2901' in relative:
        url = 'https://www.ti.com/lit/zip/slcj010'
        role = 'TI comparator model / supplied example; original copyright retained'
    elif 'models/lmr51420x_ti' in relative:
        url = 'https://www.ti.com/lit/zip/slum848'
        role = 'Encrypted PSpice model inspected, not simulated in ngspice'
    elif path.name == 'wpilib_CAN_2026.java':
        url = 'https://raw.githubusercontent.com/wpilibsuite/allwpilib/v2026.2.1/wpilibj/src/main/java/edu/wpi/first/wpilibj/CAN.java'
        role = 'WPILib integration API reference'
    elif path.name == 'CAN_wpilib2026.h':
        url = 'https://raw.githubusercontent.com/wpilibsuite/allwpilib/v2026.2.1/wpilibc/src/main/native/include/frc/CAN.h'
        role = 'WPILib integration API reference'
    else:
        url = urls.get(path.stem)
        role = ('Historical rejected-part research' if path.stem in ('b360a', 'lmr51410', 'srp7030', 'tps1h100')
                else 'Manufacturer technical reference')
        if path.suffix == '.txt':
            role += '; text extracted locally from companion PDF'
    records.append(dict(path=relative, bytes=path.stat().st_size,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        source_url=url, role=role))
manifest = dict(consulted_date='2026-09-07',
                notice='Reference documents/models retain manufacturer copyright and terms. No files are relicensed as original project material.',
                files=records)
(sources / 'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Recorded {len(records)} local source files; {sum(r["source_url"] is None for r in records)} without a URL')
