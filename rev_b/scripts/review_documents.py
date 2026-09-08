"""Check document links and PDF text bounds; visual inspection is separate."""
from pathlib import Path
import hashlib
import json
import re
import pdfplumber
R=Path(__file__).resolve().parents[1]
missing=[];documents=0
for p in [R/'README.md',R/'TOOLS.md']+list((R/'docs').glob('*.md')):
    documents+=1
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
        if re.match(r'^[a-z]+:|^#',target):continue
        if not (p.parent/target.split('#')[0]).exists():missing.append([p.relative_to(R).as_posix(),target])
(R/'reports/document_links.json').write_text(json.dumps(dict(result='PASS' if not missing else 'FAIL',documents=documents,missing=missing),indent=2)+'\n')
assert not missing,missing
files=[]
for p in sorted((R/'output').rglob('*.pdf')):
    with pdfplumber.open(p) as d:
        bad=[]
        for i,page in enumerate(d.pages):
            for word in page.extract_words():
                if word['x0']<-1 or word['top']<-1 or word['x1']>page.width+1 or word['bottom']>page.height+1:
                    bad.append([i+1,word['text']])
        files.append(dict(path=p.relative_to(R).as_posix(),pages=len(d.pages),outside_page_words=bad,
                          sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
result=dict(result='PASS' if not any(q['outside_page_words'] for q in files) else 'FAIL',
    scope='Automated PDF text bounds and link checks only; selected output pages also visually inspected by the designer.',files=files)
(R/'reports/pdf_review.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['result']=='PASS',result
print(f'{documents} Markdown documents and {len(files)} PDF files checked')
