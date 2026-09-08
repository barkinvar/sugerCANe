"""Check printable delivery files for text overflow and mounting print scale.

This complements manual page review; it cannot judge image readability or detect
every overlap. It does not verify external URLs or qualify an assembled board.
"""
from pathlib import Path
import hashlib,json
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
files=['FRC_Sensor_CAN_RevA_Handbook.pdf','BOM_RevA.pdf','wiring_card.pdf','mounting_template.pdf']
result={'result':'PASS','scope':'PDF text page bounds and nominal vector print scale; manual visual review remains separate.','files':{}}
for name in files:
    p=ROOT/'output/documentation'/name
    with pdfplumber.open(p) as pdf:
        issues=[]
        for i,page in enumerate(pdf.pages,1):
            for word in page.extract_words():
                if word['x0']<18 or word['x1']>page.width-18 or word['top']<10 or word['bottom']>page.height-10:
                    issues.append({'page':i,'text':word['text']})
        assert not issues,(name,issues)
        result['files'][name]={'pages':len(pdf.pages),'out_of_page_words':len(issues),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        if name=='mounting_template.pdf':
            page=pdf.pages[0];scale=72/25.4
            board=[r for r in page.rects if abs(r['width']/scale-96)<.001 and abs(r['height']/scale-96)<.001]
            assert len(board)==1,'Missing 96mm vector board outline'
            ruler=[l for l in page.lines if abs(l['width']/scale-50)<.001 and abs(l['height'])<.001]
            assert len(ruler)==1,'Missing 50mm scale ruler'
            result['mounting_nominal_scale']={'board_width_mm':board[0]['width']/scale,'board_height_mm':board[0]['height']/scale,'ruler_length_mm':ruler[0]['width']/scale,'printer_scaling_verified':False}
(ROOT/'reports/documentation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
