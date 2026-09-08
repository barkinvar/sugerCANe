"""Fetch the exact public WPILib dependencies used by the host integration tests.

The checked-in manifest pins SHA-256 as well as URLs. Existing matching files
are reused; an unexpected upstream response is never accepted as a dependency.
"""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / (sys.argv[1] if len(sys.argv)>1 else 'tools/driver_dependencies.json')).read_text())
for entry in manifest['files']:
    path = ROOT / entry['path']
    digest = lambda data: hashlib.sha256(data).hexdigest()
    if path.exists() and digest(path.read_bytes()) == entry['sha256']:
        print(f"Verified {entry['path']}")
        continue
    request = urllib.request.Request(entry['url'], headers={'User-Agent': 'FRC-Sensor-CAN-dependency-fetch/1'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    if digest(data) != entry['sha256']:
        raise RuntimeError(f"SHA-256 mismatch for {entry['url']}; existing file not replaced")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"Fetched {entry['path']}")
