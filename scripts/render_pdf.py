from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
output=root/'tmp/pdfs';output.mkdir(parents=True,exist_ok=True)
pdf=root/'output/pdf/justificacion_examen_unicah.pdf'
doc=pdfium.PdfDocument(str(pdf))
thumbs=[]
for i in range(len(doc)):
 im=doc[i].render(scale=1.2).to_pil().convert('RGB'); im.save(output/f'final-{i+1:02}.png')
 im.thumbnail((224,320));tile=Image.new('RGB',(240,345),'#e2e8f0');tile.paste(im,((240-im.width)//2,0));ImageDraw.Draw(tile).text((8,326),str(i+1),fill='black');thumbs.append(tile)
sheet=Image.new('RGB',(1200,345*((len(thumbs)+4)//5)),'white')
for i,im in enumerate(thumbs):sheet.paste(im,((i%5)*240,(i//5)*345))
sheet.save(output/'final-contact-sheet.png')
reader=PdfReader(str(pdf))
print('Páginas:',len(reader.pages))
print('Todas contienen texto:',all(bool(p.extract_text().strip()) for p in reader.pages))
print('Imágenes:',sum(len(p.images) for p in reader.pages))
