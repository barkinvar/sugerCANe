"""Check local Markdown/HTML delivery links without asserting remote availability."""
from pathlib import Path
from urllib.parse import unquote, urlparse
import json
import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
files = [ROOT/'README.md', ROOT/'DESIGN_PLAN.md', ROOT/'TOOLS.md']
files += [ROOT/p for p in ['REV_A.md','TOOLS_RevA.md','REVISIONS.md','CONTRIBUTING.md'] if (ROOT/p).exists()]
files += list((ROOT/'docs').glob('*.md'))
files += [ROOT/p for p in ['bom/README.md', 'firmware/README.md', 'examples/README.md',
                          'hardware/design/README.md', 'output/fabrication/README.md',
                          'output/documentation/setup_worksheet.html']]
files += [ROOT/'hardware/library/README.md']
for directory in ['rev_b', 'rev_b2']:
    revision = ROOT/directory
    if not revision.exists():
        continue
    files += [revision/p for p in ['README.md', 'TOOLS.md', 'DESIGN_PLAN.md',
                                    'firmware/README.md', 'examples/README.md',
                                    'hardware/library/README.md', 'output/fabrication/README.md']]
    files += list((revision/'docs').glob('*.md'))
checked=[]; missing=[]
for path in files:
    text=path.read_text()
    html=markdown.markdown(text,extensions=['tables','fenced_code']) if path.suffix=='.md' else text
    soup=BeautifulSoup(html,'html.parser')
    for anchor in soup.find_all(['a','img']):
        target=anchor.get('href',anchor.get('src',''))
        parsed=urlparse(target)
        if parsed.scheme or not parsed.path:
            continue
        destination=(path.parent/unquote(parsed.path)).resolve()
        entry=dict(source=str(path.relative_to(ROOT)),target=target,exists=destination.exists())
        checked.append(entry)
        if not entry['exists']:missing.append(entry)
report=dict(result='FAIL' if missing else 'PASS',local_links_checked=len(checked),missing=missing,
            scope='Local delivery links only; external URLs and anchors are not validated by this check.')
(ROOT/'reports/document_links.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert not missing
