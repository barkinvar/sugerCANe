"""Create a printable handbook from the maintained Markdown instructions."""
from pathlib import Path
from html import escape
import re
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
    'body': ParagraphStyle('Body', fontName='Guide', fontSize=9, leading=12, spaceAfter=6, textColor=INK),
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
        elif name == 'pre':
            lines = block.get_text().rstrip().splitlines()
            # Paragraph wraps long literal lines, unlike an overflowing Preformatted.
            flow.append(Paragraph('<br/>'.join(escape(line).replace(' ', '&#160;') for line in lines), styles['code']))
        elif name == 'table':
            rows = [[Paragraph(inline(cell), styles['cell']) for cell in row.find_all(['th', 'td'], recursive=False)]
                    for row in block.find_all('tr')]
            count = len(rows[0])
            if count == 3:
                widths = [106, 166, 239] if 'BRING_UP' not in path.name else [92, 209, 210]
                if path.name == 'OPTIMIZATION_PLAN.md':
                    widths = [105, 211, 195]
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
    canvas.drawString(42, 817, 'FRC SENSOR CAN  /  REVISION D-2 SC12 PROTOTYPE')
    canvas.drawRightString(553, 817, '2026-09-08')
    canvas.setStrokeColor(colors.HexColor('#cbd7dc'))
    canvas.line(42, 808, 553, 808)
    canvas.drawString(42, 24, 'Unbuilt design — qualification measurements remain pending')
    canvas.drawRightString(553, 24, str(doc.page))
    canvas.restoreState()

story = [Spacer(1, 33), Paragraph('FRC<br/>Sensor CAN', styles['cover']),
         Paragraph('Revision D-2 SC12 · Prototype engineering and assembly guide', styles['heading']),
         Paragraph('Three industrial / logic sensor inputs<br/>Regulated 12 V and 5 V sensor power', styles['body']),
         Spacer(1, 10)]
render = ROOT / 'output/review/board_3d_final.png'
if render.exists():
    from PIL import Image as PILImage
    with PILImage.open(render) as im:
        w, h = im.size
    story.append(Image(str(render), width=380, height=380*h/w))
story.extend([Spacer(1, 12), Paragraph('2026-09-08', styles['heading']),
              Paragraph('Editable KiCad files, split factory/hand-solder BOMs, firmware, robot examples and verification records accompany this guide. No physical prototype has been tested. Electrical ratings are design targets pending the included qualification plan.', styles['body']),
              PageBreak(), Paragraph('Contents', styles['chapter'])])
toc = TableOfContents()
toc.levelStyles = [ParagraphStyle('TOC', fontName='Guide', fontSize=10, leading=19, textColor=INK)]
story.extend([toc, PageBreak()])
chapters = [('1  Product overview', 'README.md'), ('2  Simplification', 'docs/SIMPLIFICATION.md'), ('3  Wiring and programming contacts', 'docs/WIRING.md'), ('4  Hand assembly', 'docs/ASSEMBLY.md'), ('5  Firmware', 'firmware/README.md'), ('6  CAN protocol', 'docs/CAN_PROTOCOL.md'), ('7  Robot integration', 'examples/README.md'), ('8  Purchasing and factory quote', 'docs/FACTORY_ORDER.md'), ('9  Validation and qualification', 'docs/VALIDATION.md'), ('10  Connector evidence', 'docs/CONNECTORS.md'), ('11  Tools and reproduction', 'TOOLS.md'), ('12  Sources and notices', 'docs/SOURCES_AND_LICENSES.md'), ('13  Cost reduction', 'docs/COST_REDUCTION.md')]

chapters.extend([('14  Optimization progress and qualification', 'docs/OPTIMIZATION_PLAN.md'), ('15  CAN setup and updates', 'docs/CAN_SERVICE.md'), ('16  Programming and unit fixture', 'docs/FIXTURE.md')])

for i, (title, path) in enumerate(chapters):
    if i:
        story.append(PageBreak())
    story.append(Paragraph(title, styles['chapter']))
    story.append(Paragraph('Source: ' + path, styles['small']))
    story.extend(convert(ROOT / path))

doc = Guide(str(OUT / 'SC12_RevD2_Handbook.pdf'), pagesize=A4,
            leftMargin=42, rightMargin=42, topMargin=48, bottomMargin=43,
            title='FRC Sensor CAN — Revision D-2 SC12 prototype handbook',
            author='FRC Sensor CAN project')
doc.multiBuild(story, onFirstPage=page, onLaterPages=page)
print(OUT / 'SC12_RevD2_Handbook.pdf')
