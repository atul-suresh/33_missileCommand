"""Build EVIDENCE.pdf from EVIDENCE.md and PROMPTS.md; requires reportlab."""
from pathlib import Path
import re
import textwrap
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                               TableStyle, PageBreak, XPreformatted)

ROOT = Path(__file__).resolve().parents[1]
font_root = Path('/usr/share/fonts/truetype/dejavu')
if font_root.exists():
    pdfmetrics.registerFont(TTFont('Report', str(font_root / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('Report-Bold', str(font_root / 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Report-Mono', str(font_root / 'DejaVuSansMono.ttf')))
    regular, bold, mono = 'Report', 'Report-Bold', 'Report-Mono'
else:
    # Standard PDF fonts support the quoted punctuation in the prompt appendix.
    regular, bold, mono = 'Helvetica', 'Helvetica-Bold', 'Courier'

navy = colors.HexColor('#142D47')
teal = colors.HexColor('#176B77')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('ReportBody', fontName=regular, fontSize=9, leading=13,
                          spaceAfter=7, textColor=navy))
styles.add(ParagraphStyle('ReportTitle', fontName=bold, fontSize=21, leading=25,
                          spaceAfter=15, textColor=navy))
styles.add(ParagraphStyle('ReportHeading', fontName=bold, fontSize=12, leading=16,
                          spaceBefore=13, spaceAfter=8, textColor=teal, keepWithNext=True))
styles.add(ParagraphStyle('ReportCell', fontName=regular, fontSize=7.7, leading=11,
                          alignment=TA_LEFT, textColor=navy))
styles.add(ParagraphStyle('ReportCode', fontName=mono, fontSize=7.1, leading=10.5,
                          spaceAfter=9, textColor=navy))
WIDTH = A4[0] - 72

def para(text, style='ReportBody'):
    return Paragraph(escape(text).replace('`', ''), styles[style])

def blocks(path):
    lines = path.read_text().splitlines()
    output, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('```'):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                # Wrap for the page while keeping the verbatim source in PROMPTS.md.
                code.extend(textwrap.wrap(lines[i], width=105, replace_whitespace=False,
                                          drop_whitespace=False, break_long_words=False,
                                          break_on_hyphens=False) or [''])
                i += 1
            output.append(XPreformatted(escape('\n'.join(code)), styles['ReportCode']))
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    rows.append([para(c,'ReportCell') for c in cells])
                i += 1
            count = len(rows[0])
            widths = ([110,65,WIDTH-175] if count == 3 and 'Change' in line
                      else [95,WIDTH-150,55] if count == 3
                      else [155,WIDTH-155] if count == 2
                      else [WIDTH/count]*count)
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DBE9EE')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),7),
                ('RIGHTPADDING',(0,0),(-1,-1),7),
                ('TOPPADDING',(0,0),(-1,-1),6),
                ('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('LINEBELOW',(0,0),(-1,0),.7,teal),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F7F9')]),
                ('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#D7E1E5')),
            ]))
            output.extend([table,Spacer(1,9)])
        elif line.startswith('# '):
            output.append(para(line[2:],'ReportTitle'))
            i += 1
        elif line.startswith('## '):
            output.append(para(line[3:],'ReportHeading'))
            i += 1
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','- ')):
                paragraph.append(lines[i])
                i += 1
            output.append(para(' '.join(paragraph)))
    return output

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(teal)
    canvas.line(36, A4[1]-27, A4[0]-36, A4[1]-27)
    canvas.setFont(regular,7)
    canvas.setFillColor(navy)
    canvas.drawString(36,20,'MISSILE COMMAND / LAB 4 / Evidence and prompt appendix')
    canvas.drawRightString(A4[0]-36,20,f'Page {doc.page}')
    canvas.restoreState()

story = blocks(ROOT/'EVIDENCE.md') + [PageBreak()] + blocks(ROOT/'PROMPTS.md')
SimpleDocTemplate(str(ROOT/'EVIDENCE.pdf'), pagesize=A4, leftMargin=36, rightMargin=36,
                  topMargin=42, bottomMargin=38, title='Missile Command Repair Lab - Evidence',
                  author='Lab 4 submission; student details not supplied').build(
                      story,onFirstPage=footer,onLaterPages=footer)
print(ROOT/'EVIDENCE.pdf')
