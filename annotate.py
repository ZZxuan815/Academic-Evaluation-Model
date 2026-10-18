import pathlib,io,re
import pdfplumber
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
out=pathlib.Path('output/pdf');out.mkdir(parents=True,exist_ok=True)
rules=[('efficien','Does using less energy per task also reduce total energy use?','efficiency 效率'),('rebound','Cheaper, faster services may be used more, offsetting energy savings.','rebound effect 反弹效应'),('resource','Which scarce materials are needed, and can they be recycled?','resource 资源'),('carbon','How is CO2 estimated? The electricity source changes the result.','carbon footprint 碳足迹'),('cost','Does the reported cost include failed runs and model tuning?','cost 成本'),('policy','Which rule would change behavior, and who would enforce it?','policy 政策'),('energy','Do the energy savings outweigh the electricity used by the technology?','energy 能源'),('accuracy','Is a small accuracy gain worth a large increase in computation?','accuracy 准确率'),('FLOP','FLOPs count operations, but do not directly measure electricity use.','FLOPs 浮点运算次数'),('inclusive','Lower computing costs let researchers with smaller budgets participate.','inclusive 包容性'),('blockchain','Is blockchain needed here? Could a simpler database do the same job?','blockchain 区块链'),('lithium','EV batteries need lithium; cleaner transport still has mining impacts.','lithium 锂'),('sustainab','Consider production, use and disposal, rather than only operation.','sustainability 可持续性'),('experiment','Repeated trials consume resources even when their results are not published.','experiment 实验')]

for f in pathlib.Path('C:/Users/ASUS/Desktop').glob('*.pdf'):
 if not f.name.startswith(('Sustainable Development','1907.10597')):continue
 reader=PdfReader(f);writer=PdfWriter();pl=pdfplumber.open(f)
 for i,p in enumerate(pl.pages):
  w,h=float(p.width),float(p.height);buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(w+150,h));c.setFillColorRGB(.97,.98,1);c.rect(w,0,150,h,fill=1,stroke=0)
  c.setFillColorRGB(.15,.25,.45);c.setFont('Helvetica-Bold',9);c.drawString(w+9,h-24,'READING NOTES | '+str(i+1))
  words=p.extract_words();chosen=[];seen=set()
  matches=[]
  for word in words:
   for key,note,cn in rules:
    if key.lower() in word['text'].lower() and 55<word['top']<h-65:
     matches.append((word,note,cn));break
  # Spread concise notes across the page and mark repeated key ideas.
  if matches:
   
   unique={}
   for item in matches:
    unique.setdefault(item[2],item)
   chosen=list(unique.values())[:10]
  marked=[]
  for j,(word,note,cn) in enumerate(matches):
   if any(abs(word['top']-a)<12 and abs(word['x0']-b)<180 for a,b in marked):continue
   marked.append((word['top'],word['x0']))
   x,y,x2=word['x0'],h-word['bottom'],word['x1'];hh=word['bottom']-word['top']
   nearby=[z for z in words if abs(z['top']-word['top'])<3 and z['x0']>=x and z['x1']<=min(x+165,w-25)]
   end=max([z['x1'] for z in nearby]+[x2])
   c.setStrokeColorRGB(.15,.36,.75);c.setLineWidth(.7)
   if j%4==0:
    c.saveState();c.setFillColorRGB(1,.83,.18);c.setFillAlpha(.27);c.rect(x-1,y-1,end-x+2,hh+2,fill=1,stroke=0);c.restoreState()
   elif j%4==1:
    c.setStrokeColorRGB(.8,.18,.22);c.line(x,y-2,end,y-2)
   elif j%4==2:c.ellipse(x-2,y-2,x2+2,y+hh+2)
   else:
    c.setStrokeColorRGB(.1,.5,.35);c.line(x,y-2,end,y-2);c.line(x,y-4,end,y-4)
  for j,(word,note,cn) in enumerate(chosen):
   x,y,x2=word['x0'],h-word['bottom'],word['x1'];hh=word['bottom']-word['top'];color=[(.12,.38,.78),(.8,.18,.2),(.12,.52,.35)][j%3]
   c.setStrokeColorRGB(*color);c.setLineWidth(.9)
   if j%3==0:
    c.saveState();c.setFillColorRGB(1,.83,.2);c.setFillAlpha(.3);c.rect(x-1,y-1,x2-x+2,hh+2,fill=1,stroke=0);c.restoreState()
   elif j%3==1:c.line(x,y-2,x2,y-2);c.line(x,y-4,x2,y-4)
   else:c.ellipse(x-2,y-2,x2+2,y+hh+2)
   # Margin numbers and matching quoted anchors make each note traceable.
   bx=18 if x<w/2 else w-19
   by=y+hh/2
   c.setFillColorRGB(1,1,1);c.circle(bx,by,7,fill=1,stroke=0)
   c.setStrokeColorRGB(*color);c.circle(bx,by,7,fill=0,stroke=1)
   c.setFillColorRGB(*color);c.setFont('Helvetica-Bold',7);c.drawCentredString(bx,by-2.5,str(j+1))
   c.setLineWidth(.35);c.setDash(1,2);c.line(bx+(7 if x<w/2 else -7),by,x-3 if x<w/2 else x2+3,by);c.setDash()
   ny=h-48-j*((h-80)/10);c.setFillColorRGB(*color);c.setFont('Helvetica-Bold',8)
   c.drawString(w+10,ny,'['+str(j+1)+'] '+cn.split(' ')[0])
   ny-=11;c.setFont('Helvetica-Oblique',8)
   import textwrap
   for k,line in enumerate(textwrap.wrap(note,28)):c.drawString(w+10,ny-k*11,line)
   c.setFont('STSong-Light',8);c.drawString(w+10,ny-38,cn)
   c.setStrokeColorRGB(*color);c.line(w+10,ny-45,w+133,ny-45)
  c.save();ov=PdfReader(buf).pages[0];ov.merge_page(reader.pages[i], over=False);writer.add_page(ov)
 target=out/('Green_AI_annotated_revised.pdf' if f.name.startswith('1907') else 'Digital_sustainability_annotated_revised.pdf')
 writer.write(target)
 print(target.resolve(),len(writer.pages))
 try:
  pdfplumber.open(target).pages[0].to_image(resolution=90).save(out/(target.stem+'.png'))
 except Exception as e:print(type(e).__name__,str(e)[:150])

