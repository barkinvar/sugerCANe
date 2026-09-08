"""Readable purchasing BOM from the same grouped CSV used for ordering."""
from pathlib import Path
from html import escape
import csv
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('BOM', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('BOMBold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('BOM', normal='BOM', bold='BOMBold')
rows = list(csv.DictReader((ROOT/'bom/BOM_grouped.csv').open()))
summary = json.loads((ROOT/'bom/summary.json').read_text())
body = ParagraphStyle('body', fontName='BOM', fontSize=8, leading=11, spaceAfter=8)
cell = ParagraphStyle('cell', fontName='BOM', fontSize=7.5, leading=10)
title = ParagraphStyle('title', fontName='BOMBold', fontSize=20, leading=25, spaceAfter=10)
def para(s): return Paragraph(escape(str(s)), cell)
data = [[para(x) for x in ['References', 'Qty', 'Value / rating', 'Manufacturer part number', 'DigiKey order code', 'Observed stock', 'Unit USD', 'Line USD']]]
for row in rows:
    refs = row['References'].replace('CONFIGURATION_SHUNTS', 'Separate shunts')
    rating = row['Value']
    if row['Voltage']: rating += ' / '+row['Voltage']
    if row['Tolerance']: rating += ' / '+row['Tolerance']
    if row['Power_W']: rating += ' / '+row['Power_W']+' W'
    part = Paragraph('<b>'+escape(row['MPN'])+'</b><br/>'+escape(row['Manufacturer']),cell)
    order = Paragraph('<a color="#146d84" href="'+escape(row['DigiKey_URL'],quote=True)+'">'+escape(row['DigiKey_SKU'])+'</a>',cell)
    data.append([para(refs),para(row['Quantity']),para(rating),part,order,
                 para(f"{int(row['Observed_stock']):,}"),para(f"{float(row['Unit_USD_qty1']):.2f}"),
                 para(f"{float(row['Extended_USD_qty1']):.2f}")])
table = Table(data, colWidths=[123,28,115,159,140,70,63,64], repeatRows=1)
table.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcebf0')),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f7f8')]),
    ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),
    ('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),
    ('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#146d84')),
]))
story=[Paragraph('FRC Sensor CAN · Revision B purchasing BOM',title),
       Paragraph(f"{len(rows)} order lines · {summary['fitted_parts']} fitted components + 10 shunts · Indicative total <b>US${summary['component_estimate_usd_qty1']:.2f}</b>",body),
       Paragraph('Dated observations: 2026-09-07/08. Quantity-one prices are applied to every unit; actual quantity breaks may reduce cost. PCB, stencil, tools, mounting hardware, shipping and tax are excluded. This is not a live quote or reserved inventory. Recheck exact order codes before purchase.',body),
       Paragraph('Use DigiKey_import.csv to import an order. This PDF lists exact assembly quantities. Full ratings, footprint IDs, sources and alternative-review notes are in BOM_grouped.csv. The interactive BOM provides placement guidance.',body),table]
def footer(canvas,doc):
    canvas.setFont('BOM',7)
    canvas.drawString(30,17,'Revision B prototype · Reconfirm parts and stock · No physical build qualification')
    canvas.drawRightString(812,17,str(doc.page))
out=ROOT/'output/documentation/BOM_RevB.pdf'
doc=SimpleDocTemplate(str(out),pagesize=landscape(A4),leftMargin=30,rightMargin=30,topMargin=28,bottomMargin=32,
                      title='FRC Sensor CAN Revision B purchasing BOM')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
