"""Check maintained Markdown links and PDF text page bounds; visual review is separate."""
from pathlib import Path
import re,json
import pdfplumber
R=Path(__file__).resolve().parents[1];broken=[];links=0
docs=[R/'README.md',R/'TOOLS.md',R/'DESIGN_PLAN.md',R/'firmware/README.md',R/'examples/README.md',R/'bom/README.md',*R.glob('docs/*.md')]
for p in docs:
 for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
  if re.match(r'^[a-z]+:|^#',link):continue
  target=(p.parent/link.split('#')[0]).resolve();links+=1
  if not target.exists() and not (target.parent==R/'release' and target.suffix=='.zip'):broken.append([str(p.relative_to(R)),link])
assert not broken,broken
pdfs=[]
for path in [*R.glob('output/documentation/*.pdf'),R/'output/mechanical/mechanical_drawing.pdf',R/'output/assembly/top_assembly.pdf',R/'output/assembly/schematic.pdf']:
 with pdfplumber.open(path) as pdf:
  bad=[]
  for n,page in enumerate(pdf.pages,1):
   for ch in page.chars:
    if ch['x0'] < -1 or ch['x1']>page.width+1 or ch['top'] < -1 or ch['bottom']>page.height+1:bad.append([n,ch.get('text'),ch['x0'],ch['top']])
  assert not bad,(path,bad[:10])
  pdfs.append(dict(file=str(path.relative_to(R)),pages=len(pdf.pages),text_within_page=True))
out=dict(result='PASS',local_links_checked=links,broken_links=broken,pdfs=pdfs,limitations='Checks links and text-page bounds, not visual overlap, circuit correctness or print scaling. Visual inspection is required separately.')
(R/'reports/document_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
