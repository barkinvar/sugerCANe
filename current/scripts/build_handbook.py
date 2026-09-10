"""Create a printable handbook from the maintained Markdown instructions."""
from pathlib import Path
from html import escape
import re
import argparse
import markdown
from bs4 import BeautifulSoup, NavigableString
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Table, TableStyle, Image, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/documentation'
OUT.mkdir(parents=True, exist_ok=True)
FONT = Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('Guide', str(FONT / 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('Guide-Bold', str(FONT / 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('GuideMono', str(FONT / 'DejaVuSansMono.ttf')))
pdfmetrics.registerFontFamily('Guide', normal='Guide', bold='Guide-Bold', italic='Guide', boldItalic='Guide-Bold')
INK = colors.HexColor('#162c3d')
BLUE = colors.HexColor('#116c8a')
styles = {
    'body': ParagraphStyle('Body', fontName='Guide', fontSize=9, leading=11.5, spaceAfter=5, textColor=INK, allowWidows=0, allowOrphans=0),
    'chapter': ParagraphStyle('Chapter', fontName='Guide-Bold', fontSize=21, leading=27, spaceAfter=16, textColor=INK, keepWithNext=True),
    'heading': ParagraphStyle('Heading', fontName='Guide-Bold', fontSize=12, leading=16, spaceBefore=10, spaceAfter=7, textColor=BLUE, keepWithNext=True),
    'small': ParagraphStyle('Small', fontName='Guide', fontSize=7.4, leading=10, spaceAfter=4, textColor=INK),
    'code': ParagraphStyle('Code', fontName='GuideMono', fontSize=7.3, leading=10, spaceAfter=8, backColor=colors.HexColor('#f1f5f7'), borderPadding=6),
    'cell': ParagraphStyle('Cell', fontName='Guide', fontSize=7.4, leading=10, textColor=INK),
    'cover': ParagraphStyle('Cover', fontName='Guide-Bold', fontSize=32, leading=39, spaceAfter=18, textColor=INK),
}

def inline(node):
    if isinstance(node, NavigableString):
        return escape(str(node))
    body = ''.join(inline(c) for c in node.children)
    if node.name in ('strong', 'b'):
        return '<b>' + body + '</b>'
    if node.name in ('em', 'i'):
        return '<i>' + body + '</i>'
    if node.name == 'code':
        return '<font name="GuideMono" size="7.4">' + body + '</font>'
    if node.name == 'br':
        return '<br/>'
    if node.name == 'a' and node.get('href', '').startswith('https://'):
        return '<a href="' + escape(node['href'], quote=True) + '" color="#116c8a">' + body + '</a>'
    return body

def convert(path):
    html = markdown.markdown(path.read_text().replace('—','-').replace('–','-').replace('‑','-'), extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        href=link['href']
        if not re.match(r'^[a-z]+:|^#',href):
            filename,sep,fragment=href.partition('#')
            local=(path.parent/filename).resolve().relative_to(ROOT.parent)
            link['href']='https://github.com/barkinvar/sugerCANe/blob/main/'+local.as_posix()+(sep+fragment if sep else '')
    blocks = list(soup.children)
    # Each source document starts with its own title; the book has a chapter title.
    for n, block in enumerate(blocks):
        if getattr(block, 'name', None):
            blocks.pop(n)
            break
    flow = []
    for block in blocks:
        name = getattr(block, 'name', None)
        if name == 'p':
            picture = block.find('img')
            if picture:
                if path == ROOT/'README.md' and picture['src'].endswith('board_3d_final.png'):
                    continue
                local = (path.parent / picture['src']).resolve()
                from PIL import Image as PILImage
                with PILImage.open(local) as im:
                    w, h = im.size
                scale=min(511/w,300/h)
                flow.extend([Image(str(local), width=w*scale, height=h*scale), Spacer(1, 10)])
                continue
            title = len(block.contents) == 1 and getattr(block.contents[0], 'name', None) == 'strong'
            flow.append(Paragraph(inline(block), styles['heading' if title else 'body']))
        elif name in ('h1', 'h2', 'h3'):
            flow.append(Paragraph(inline(block), styles['heading']))
        elif name in ('ol', 'ul'):
            for i, item in enumerate(block.find_all('li', recursive=False), 1):
                label = f'{i}. ' if name == 'ol' else '• '
                flow.append(Paragraph(escape(label) + inline(item), styles['body']))
        elif name == 'blockquote':
            for para in block.find_all('p', recursive=False):
                flow.append(Paragraph(inline(para), styles['small']))
        elif name == 'pre':
            lines = block.get_text().rstrip().splitlines()
            # Paragraph wraps long literal lines, unlike an overflowing Preformatted.
            flow.append(Paragraph('<br/>'.join(escape(line).replace(' ', '&#160;') for line in lines), styles['code']))
        elif name == 'table':
            if path == ROOT/'README.md' and 'What you want to do' in block.get_text():
                continue  # The printed guide already has a chapter contents page.
            rows = [[Paragraph(inline(cell), styles['cell']) for cell in row.find_all(['th', 'td'], recursive=False)]
                    for row in block.find_all('tr')]
            count = len(rows[0])
            if count == 3:
                widths = [106, 166, 239] if 'BRING_UP' not in path.name else [92, 209, 210]
            elif count == 2:
                widths = [145, 366]
            elif count == 4:
                widths = [128, 128, 128, 127]
            elif count == 5:
                widths = [123, 110, 81, 92, 105]
            else:
                widths = [511 / count] * count
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dcebf0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7f8')]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, 0), .7, BLUE),
            ]))
            if len(rows)<=8:
                # Keep a section title with its table when the table moves pages.
                heading = ([flow.pop()] if flow and isinstance(flow[-1], Paragraph)
                           and flow[-1].style.name == 'Heading' else [])
                flow.extend([KeepTogether([*heading, table]), Spacer(1, 10)])
            else:
                flow.extend([table, Spacer(1, 10)])
    return flow

class Guide(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if (isinstance(flowable, Paragraph) and flowable.style.name == 'Chapter'
                and flowable.getPlainText() != 'Contents'):
            title = flowable.getPlainText()
            key = re.sub(r'[^A-Za-z0-9]', '_', title)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, 0)
            self.notify('TOCEntry', (0, title, self.page, key))

def page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont('Guide', 7.3)
    canvas.setFillColor(colors.HexColor('#537080'))
    canvas.drawString(42, 817, 'FRC SENSOR CAN  /  REVISION H SC12 PROTOTYPE')
    canvas.drawRightString(553, 817, '2026-09-09')
    canvas.setStrokeColor(colors.HexColor('#cbd7dc'))
    canvas.line(42, 808, 553, 808)
    canvas.drawString(42, 24, 'Unbuilt design — qualification measurements remain pending')
    canvas.drawRightString(553, 24, str(doc.page))
    canvas.restoreState()

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--order-guide',action='store_true',help='Build only the concise ordering guide')
args=ap.parse_args()
if args.order_guide:
    styles['body'].spaceAfter=4.0
    styles['body'].leading=11.5
    styles['small'].spaceAfter=3
    story=[Paragraph('sugarCANe / Rev H',styles['cover']),
           Paragraph('Order and build guide',styles['heading']),
           Paragraph('JLCPCB assembly + user-soldered DigiKey MCU',styles['body']),
           Paragraph('Selected assembly plan. Final simulation review required before paying for fabrication.',styles['small']),
           Spacer(1,12),*convert(ROOT/'docs/FACTORY_ORDER.md')]
    doc=Guide(str(OUT/'ORDER_GUIDE.pdf'),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=48,bottomMargin=43,
              title='sugarCANe Rev H ordering guide',author='sugarCANe project')
    doc.build(story,onFirstPage=page,onLaterPages=page)
    print(OUT/'ORDER_GUIDE.pdf')
    raise SystemExit(0)

story = [Spacer(1, 33), Paragraph('sugarCANe', styles['cover']),
         Paragraph('Revision H SC12 · Prototype engineering and assembly guide', styles['heading']),
         Paragraph('Three industrial / logic sensor inputs<br/>Regulated 12 V and 5 V sensor power', styles['body']),
         Spacer(1, 10)]
render = ROOT / 'output/review/board_3d_final.png'
if render.exists():
    from PIL import Image as PILImage
    with PILImage.open(render) as im:
        w, h = im.size
    story.append(Image(str(render), width=380, height=380*h/w))
story.extend([Spacer(1, 12), Paragraph('2026-09-09', styles['heading']),
              Paragraph('Rev H adds RGB diagnostics and inexpensive header programming while retaining protected sensor power and physical voltage jumpers. No physical prototype has been tested. This guide accompanies the engineering evidence and defines first-article acceptance.', styles['body']),
              PageBreak(), Paragraph('Contents', styles['chapter'])])
toc = TableOfContents()
toc.levelStyles = [ParagraphStyle('TOC', fontName='Guide', fontSize=10, leading=19, textColor=INK)]
story.extend([toc, PageBreak()])
chapters = [('1  Product overview', 'README.md'), ('2  Power and input circuit', 'DESIGN_PLAN.md'), ('3  Wiring and programming header', 'docs/WIRING.md'), ('4  Software input modes', 'docs/INPUT_MODES.md'), ('5  Assembly', 'docs/ASSEMBLY.md'), ('6  Firmware', 'firmware/README.md'), ('7  CAN protocol', 'docs/CAN_PROTOCOL.md'), ('8  CAN setup and updates', 'docs/CAN_SERVICE.md'), ('9  Robot integration', 'examples/README.md'), ('10  Purchasing and factory quote', 'docs/FACTORY_ORDER.md'), ('11  Qualification', 'docs/VALIDATION.md'), ('12  Unit fixture', 'docs/FIXTURE.md'), ('13  Connectors', 'docs/CONNECTORS.md'), ('14  Cost reduction', 'docs/COST_REDUCTION.md'), ('15  Tools', 'TOOLS.md'), ('16  Sources and notices', 'docs/SOURCES_AND_LICENSES.md')]

chapters.insert(4, ('Status and programming', 'docs/STATUS_AND_PROGRAMMING.md'))
chapters.insert(1, ('Pre-order decision', 'docs/ORDER_READINESS.md'))
chapters = [(str(i) + '  ' + re.sub(r'^\d+\s+', '', title), path)
            for i, (title, path) in enumerate(chapters, 1)]

for i, (title, path) in enumerate(chapters):
    if i:
        story.append(PageBreak())
    story.append(Paragraph(title, styles['chapter']))
    story.append(Paragraph('Source: ' + path, styles['small']))
    story.extend(convert(ROOT / path))

doc = Guide(str(OUT / 'SC12_RevH_Handbook.pdf'), pagesize=A4,
            leftMargin=42, rightMargin=42, topMargin=48, bottomMargin=43,
            title='sugarCANe — Revision H SC12 prototype handbook',
            author='FRC Sensor CAN project')
doc.multiBuild(story, onFirstPage=page, onLaterPages=page)
print(OUT / 'SC12_RevH_Handbook.pdf')
