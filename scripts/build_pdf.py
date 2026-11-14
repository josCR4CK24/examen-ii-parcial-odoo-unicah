"""Genera el PDF de entrega exclusivamente a partir de texto y evidencias locales reales."""
from pathlib import Path
from html import escape
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/justificacion_examen_unicah.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
font_dir = Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('ArialDoc', str(font_dir/'arial.ttf')))
pdfmetrics.registerFont(TTFont('ArialDocBold', str(font_dir/'arialbd.ttf')))
pdfmetrics.registerFontFamily('ArialDoc', normal='ArialDoc', bold='ArialDocBold', italic='ArialDoc', boldItalic='ArialDocBold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyDoc',fontName='ArialDoc',fontSize=10.1,leading=15,spaceAfter=10,textColor=colors.HexColor('#243247')))
styles.add(ParagraphStyle(name='TitleDoc',fontName='ArialDocBold',fontSize=27,leading=34,spaceAfter=20,textColor=colors.HexColor('#172b4d')))
styles.add(ParagraphStyle(name='HeadingDoc',keepWithNext=True,fontName='ArialDocBold',fontSize=17,leading=23,spaceAfter=16,textColor=colors.HexColor('#164e63')))
styles.add(ParagraphStyle(name='CaptionDoc',fontName='ArialDoc',fontSize=9,leading=13,spaceAfter=12,textColor=colors.HexColor('#475569')))
styles.add(ParagraphStyle(name='KickerDoc',fontName='ArialDocBold',fontSize=10,leading=14,spaceAfter=16,textColor=colors.HexColor('#0e7490')))
parts = (ROOT/'docs/JUSTIFICACION.md').read_text(encoding='utf-8-sig').split('\n## ')
story = []
story.append(Spacer(1,65))
story.append(Paragraph('UNICAH / PROGRAMACIÓN DE NEGOCIOS',styles['KickerDoc']))
story.append(Paragraph('Examen II Parcial',styles['TitleDoc']))
story.append(Paragraph('Implementación y justificación técnica<br/>Odoo 20.0',styles['HeadingDoc']))
story.append(Spacer(1,20))
for text in ['José Carlos Cáceres Girón','Cuenta: 0703200603787','13 de noviembre de 2026 - America/Tegucigalpa','Módulos: tienda_unicah y unicah_equipos','Base exclusiva: examen_unicah / Puerto: 8070']:
    story.append(Paragraph(escape(text),styles['BodyDoc']))
story.append(Spacer(1,24))
story.append(Paragraph('Entrega basada en código instalado, pruebas ejecutadas y evidencias identificadas. Los resultados automatizados y las comprobaciones de interfaz se distinguen expresamente.',styles['BodyDoc']))
story.append(Paragraph('Repositorio: <link href="https://github.com/josCR4CK24/examen-ii-parcial-odoo-unicah" color="#0e7490">examen-ii-parcial-odoo-unicah</link>',styles['BodyDoc']))
manifest_path=ROOT/'evidence/screenshots.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig')) if manifest_path.exists() else {}
for section in parts[1:]:
    heading, _, body = section.partition('\n')
    story.append(PageBreak())
    story.append(Paragraph(escape(heading),styles['HeadingDoc']))
    for paragraph in body.strip().split('\n\n'):
        story.append(Paragraph(escape(paragraph).replace('\n','<br/>'), styles['BodyDoc']))
    if heading.startswith('Parte '):
        num=heading[6]
        entries=manifest.get(num,[])
        if entries:
            story.append(PageBreak())
            story.append(Paragraph('Evidencia real de Odoo',styles['HeadingDoc']))
            for entry in entries:
                path=ROOT/entry['file']
                im=PILImage.open(path)
                width=475
                height=width*im.height/im.width
                if height>510:
                    width*=510/height; height=510
                story.append(KeepTogether([Image(str(path),width=width,height=height),Spacer(1,7),Paragraph(escape(entry['caption']),styles['CaptionDoc'])]))
        else:
            story.append(Paragraph('Captura de interfaz pendiente. Esta parte está implementada y su evidencia automatizada está en los registros de pruebas; no se presenta una imagen simulada como prueba.',styles['CaptionDoc']))

story.append(PageBreak())
story.append(Paragraph('Anexo: resultado de pruebas',styles['HeadingDoc']))
log=ROOT/'evidence/tests_verified.log'
if log.exists():
    lines=[line for line in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'Starting Test' in line or 'odoo.tests.result:' in line]
    for line in lines:
        msg=line.split('Starting ',1)[-1] if 'Starting ' in line else line.split('odoo.tests.result:')[-1]
        story.append(Paragraph(escape(msg),styles['CaptionDoc']))
story.append(Paragraph('Los avisos de limpieza del filestore (WinError 5) están preservados en los logs. No equivalen a errores de pruebas. No se modificaron archivos de Odoo para silenciarlos.',styles['BodyDoc']))

def footer(canvas,doc):
    canvas.saveState()
    w,h=A4
    canvas.setStrokeColor(colors.HexColor('#cbd5e1'));canvas.line(47,45,w-47,45)
    canvas.setFont('ArialDoc',8);canvas.setFillColor(colors.HexColor('#475569'))
    canvas.drawString(47,31,'UNICAH | Examen II Parcial | José Carlos Cáceres Girón')
    canvas.drawRightString(w-47,31,str(doc.page));canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=47,leftMargin=47,topMargin=48,bottomMargin=60,title='Examen II Parcial - Justificación UNICAH',author='José Carlos Cáceres Girón')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
