import ast,re,copy,pathlib
import pdfplumber
from docx import Document
from docx.shared import Pt,RGBColor
from docx.oxml.ns import qn
s=pathlib.Path('make_sr4.py').read_text(encoding='utf-8-sig');tree=ast.parse(s)
v=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='vocab' for t in n.targets))
extra=[
('proliferation','n.','/prəˌlɪfəˈreɪʃən/','快速增加','rapid growth in the number of something','proliferate (v.); proliferating (adj.)','rapid proliferation; proliferation of AI tools','spread, expansion; decline (opposite)','The proliferation of chatbots has changed customer service.','Rapid proliferation makes environmental monitoring more important.'),
('cumulative','adj.','/ˈkjuːmjələtɪv/','累积的','increasing as separate amounts are added together','accumulate (v.); accumulation (n.); cumulatively (adv.)','cumulative impact; cumulative energy use','accumulated, combined; non-cumulative (opposite)','The cumulative effect of many small requests can be substantial.','We measured cumulative electricity use over a month.'),
('overhead','n.','/ˈəʊvəhed/','额外开销','extra resources needed to support the main operation','overheads (plural noun)','memory overhead; communication overhead','extra cost; no exact opposite','Moving data between devices creates additional overhead.','The new method reduces communication overhead.'),
('bandwidth','n.','/ˈbændwɪdθ/','带宽','the rate at which data can be transferred','No common derived form','memory bandwidth; bandwidth limitation','data-transfer capacity; no exact opposite','Limited memory bandwidth can slow a large model.','Increasing bandwidth may improve processing speed.'),
('bottleneck','n.','/ˈbɒtlnek/','瓶颈','a constraint that limits the performance of a whole system','bottleneck (v.); bottlenecked (adj.)','performance bottleneck; identify a bottleneck','constraint, limiting factor; no exact opposite','Slow storage became the main bottleneck.','We must identify the bottleneck before buying new hardware.'),
('stratified','adj.','/ˈstrætɪfaɪd/','分层的','divided into groups before samples are selected','stratify (v.); stratification (n.)','stratified sampling; stratified sample','grouped, layered; unstratified (opposite)','Stratified sampling included students from each year.','A stratified sample can represent several subject areas.'),
('concurrent','adj.','/kənˈkʌrənt/','并发的','happening or operating at the same time','concurrently (adv.); concurrency (n.)','concurrent requests; concurrent execution','simultaneous; sequential (contrast)','The server handles many concurrent requests.','Concurrent tasks may compete for memory.'),
('degradation','n.','/ˌdeɡrəˈdeɪʃən/','退化或下降','a decline in quality or performance','degrade (v.); degraded (adj.)','quality degradation; performance degradation','deterioration; improvement (opposite)','Compression should avoid serious quality degradation.','We observed performance degradation after prolonged use.'),
('attribute','v.','/əˈtrɪbjuːt/','归因于','to explain something as resulting from a particular cause','attribution (n.); attributable (adj.)','attribute savings to; attributable to hardware','ascribe, credit; no exact opposite','We cannot attribute every improvement to model size.','Some savings are attributable to better software.'),
('quantify','v.','/ˈkwɒntɪfaɪ/','量化衡量','to express or measure something numerically','quantification (n.); quantifiable (adj.)','quantify emissions; quantify energy savings','measure, calculate; no exact opposite','Researchers need to quantify the benefits of recycling.','It is difficult to quantify every environmental impact.')]
v[9]=('precision','n.','/prɪˈsɪʒən/','数值精度','the level of numerical detail used to represent a value','precise (adj.); precisely (adv.)','numerical precision; reduced precision','exactness; imprecision (opposite)','II-C Quantization and Model Compression','Lower precision can reduce memory requirements.','We checked whether reduced precision affected the answers.')
for a in extra:v.append((*a[:8],'',*a[8:]))
# Extract column text in reading order; keep page and column references.
pdf=pdfplumber.open('C:/Users/ASUS/Desktop/2608.28667v1.pdf');candidates=[]
for num,p in enumerate(pdf.pages,1):
 for col,(l,r) in enumerate([(20,p.width/2),(p.width/2,p.width-20)],1):
  txt=p.crop((l,35,r,p.height-25)).extract_text(x_tolerance=2) or ''
  txt=re.sub(r'-\n(?=[a-z])','',txt);txt=re.sub(r'\s+',' ',txt)
  for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z])',txt):
   if 6<len(sent.split())<105:candidates.append((num,col,sent))
old=Document('output/docx/ESS_101_SR4_Group19_Shirley_25722118.docx')
d=Document('C:/Users/ASUS/Downloads/ESS_101_SR_Vocab_Combined Template_NEW (2).docx')
d.paragraphs[1].text='Article Number: 4\nChinese name: Zhao Zixuan    English name: Shirley\nID: 25722118    Group: 19    Week 4    ESS101'
def put(c,txt):
 c.text=txt
 for p in c.paragraphs:
  p.paragraph_format.space_after=Pt(6);p.paragraph_format.line_spacing=1.08
  for r in p.runs:r.font.name='Calibri';r.font.size=Pt(11);r.font.color.rgb=RGBColor(0,0,0)
for ti in [0,1]:
 for ri,row in enumerate(old.tables[ti].rows):
  if ti==1 and ri==6:continue
  seen=set()
  for ci,c in enumerate(row.cells):
   if c._tc in seen:continue
   seen.add(c._tc)
   if ti==0 or ri>=5 or ci==1:put(d.tables[ti].rows[ri].cells[ci],c.text)
cell=d.tables[1].rows[6].cells[0]
cell.text='Vocabulary development\n20 lexical entries. Context I quotes the article; locations use PDF page and column because the PDF has no printed line numbers. Context II contains original practice sentences.'
missing=[]
for n,(word,pos,ipa,cn,definition,family,coll,syn,loc,a,b) in enumerate(v,1):
 forms={'reproducibility':'reproducib','quantify':'quantif','attribute':'attribut','trade-off':'trade.off','concurrent':'concurren','stratified':'stratified'}.get(word,re.escape(word))
 matches=[z for z in candidates if re.search(forms,z[2],re.I)]
 if not matches:missing.append(word);continue
 num,col,sent=min(matches,key=lambda z:len(z[2]))
 # Trim a heading accidentally joined to the first sentence only when separable.
 parts=[f'{n}. Word: {word} ({pos}) {ipa} {cn}',f'Definition: {definition}.',f'Word family: {family}.',f'Collocations: {coll}.',f'Synonyms / Antonyms: {syn}.',f'Word in Context I: “{sent}” (Kannan et al., 2026, PDF p. {num}, {"left" if col==1 else "right"} column).',f'Word in Context II: (a) {a} (b) {b}']
 for k,txt in enumerate(parts):
  p=cell.add_paragraph(txt);p.paragraph_format.space_after=Pt(4 if k<6 else 12);p.paragraph_format.line_spacing=1.05;p.paragraph_format.keep_with_next=k<6
  for r in p.runs:r.font.name='Calibri';r.font.size=Pt(11);r.bold=k==0
# Drop the blank instructional examples after the form; retain actual form prompts.
for p in list(d.paragraphs):
 if p.text.startswith('*Notes on recording'):break
# The template's notes remain for reference and are separated from completed work.
for table in d.tables:
 for row in table.rows:
  pr=row._tr.trPr
  if pr is not None:
   for el in list(pr):
    if el.tag in [qn('w:trHeight'),qn('w:cantSplit')]:pr.remove(el)
remove=False
for p in list(d.paragraphs):
 if p.text.startswith('*Notes on recording'):remove=True
 if remove:p._element.getparent().remove(p._element)
out=pathlib.Path('output/docx/ESS_101_SR4_Vocab20_Shirley_25722118.docx');d.save(out)
print('MISSING',missing);print('ENTRIES',len(v));print(out.resolve())
