import pathlib,io,re,textwrap
import pdfplumber
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
G={
1:[('300,000','Compute grew 300,000-fold in 2012-2018. This motivates the paper; it is not a current estimate.'),('financial','High computing costs exclude researchers with limited budgets.'),('evaluation','Main proposal: reward efficiency alongside accuracy.'),('leaderboards','Leaderboards reward the best score while hiding the resources needed to obtain it.')],
2:[('Figure1','The graph tracks training compute, not directly measured carbon emissions.'),('price','Reporting development, training and running costs creates a baseline others can improve.'),('logarithmic','Diminishing returns: much more computation buys progressively smaller gains.')],
3:[('60papers','Evidence comes from only 60 papers across three conferences; broader sampling would strengthen it.'),('90%','Accuracy dominates claimed contributions: ACL 90%, NeurIPS 80%, CVPR 75%.'),('Cost(R)','E x D x H: per-example cost, data size and tuning trials multiply total cost.'),('epochs','The formula is simplified: it omits training epochs and variation between trials.')],
4:[('64TPU','BERT-large needed 64 TPU chips for four days: reproduction requires substantial resources.'),('242','Even storing Common Crawl data is costly; data access is another barrier.'),('12,800','Architecture search trained over 12,800 networks. The final model hides this search cost.'),('1,500','Extensive tuning makes fair comparisons expensive for competing models.')],
5:[('Figure3','The graph shows diminishing returns: data grows exponentially for roughly linear accuracy gains.'),('underreported','Missing trial counts hide the real cost of model development.'),('withoutincreasing','Green AI means useful new results without raising computation, ideally reducing it.'),('allhyperparameter','Report the work of all tuning trials, not only the successful model.')],
6:[('local','Carbon emissions vary with local electricity, complicating model comparisons.'),('hardwaredependent','Electricity use reflects both the algorithm and hardware efficiency.'),('parameters','Equal parameter counts need not imply equal computational work.'),('FPO','FPO counts floating-point operations. The authors prefer it for hardware-independent comparison.')],
7:[('production','Training savings matter during research; inference savings matter when a model is deployed repeatedly.'),('memory','Limitation: FPO omits memory costs that can increase energy and expense.'),('implementation','Different implementations of the same model may perform different amounts of work.'),('perinference','Figure 4 reports cost per inference, not the complete training and tuning budget.')],
8:[('35%','ResNext needs almost 35% more FPO than ResNet for a reported 0.5% accuracy improvement.'),('AlexNet','AlexNet has more parameters than ResNet but fewer operations: model size is a poor cost proxy.'),('budget','Budget-accuracy curves show which model works best under a fixed computing budget.'),('pretrained','Sharing pretrained models avoids repeated training by other researchers.')],
9:[('exclusivemandate','The authors offer Green AI as an option; they do not reject all resource-intensive research.'),('pretrainingefficiency','Data efficiency must include pretraining, not only task-specific fine-tuning.'),('lowresource','Using less data also matters for languages where additional training text is scarce.'),('stopping','Stopping clearly weak runs early can save computation during model search.')]
}
D={
1:[('intersection','Central question: can digital sustainability support ecological sustainability without shifting harms elsewhere?'),('tantalum','The review links digital infrastructure to finite material inputs, including tantalum, indium, cobalt and lithium.'),('rebound','Efficiency can encourage greater use, offsetting the original resource savings.'),('DSinvolves','DS concerns digital systems; EES concerns ecosystems and finite resources. Their goals may conflict.')],
2:[('NRBV','NRBV treats environmental capabilities as a source of competitive advantage for firms.'),('biophysical','Ecological economics places technological growth within physical limits.'),('Bitcoin','Bitcoin mining and EV mineral extraction illustrate different environmental costs of technological growth.'),('digitaldivide','Access to technology and exposure to environmental damage are distributed unequally.')],
3:[('STT','Transition theory explains why technology alone is insufficient: rules and social practices must also change.'),('cloudcomputing','Cloud efficiency can stimulate more data use, increasing total energy demand.'),('developingcountries','Developing countries may bear extraction and e-waste burdens while receiving fewer digital benefits.'),('nonacademic','Transdisciplinary research includes stakeholders outside academia, not just several academic subjects.')],
4:[('last5','The review prioritizes recent literature; older foundational evidence may receive less attention.'),('searchterms','Search terms are listed, but databases, screening counts and reproducible selection details are not given here.'),('secondarydata','The evidence is drawn from existing studies and reports, not newly collected measurements.'),('0.5%','The cited Bitcoin estimate is for 2020. Its date matters when interpreting this percentage.')],
5:[('Seif','Source-type check: this row labels Seif et al. an industry report, but the references list a journal article.'),('Laletal','This row calls Lal et al. a policy document; the references identify a journal article.'),('Vera','Lithium extraction connects battery adoption to environmental impacts upstream.'),('Bol','Green AI is presented as a way to reduce the footprint of AI itself.')],
6:[('Picatoste','Battery life-cycle assessment includes production and disposal, extending beyond driving emissions.'),('Chamanara','Bitcoin mining evidence supports the case for environmental policy intervention.'),('Sehnem','Circular-economy examples widen the discussion beyond energy consumption.')],
7:[('15','The cited battery estimate reaches 15-20 tonnes of CO2. Battery size and production assumptions need checking.'),('household','The GPT-3 household comparison lacks a clear numerical boundary here; check the cited source.'),('full lifecycle','EV sustainability depends on production, use and disposal, not only zero tailpipe emissions.'),('PoS','Alternative consensus mechanisms show that blockchain energy demand depends on design.'),('outpace','Growth in AI use can outpace technical efficiency improvements.')],
8:[('60%','Concentrated cobalt supply creates both geopolitical risk and ethical sourcing concerns.'),('mid-2030s','Lithium shortages are a projection, not a certainty; outcomes depend on demand and new supply.'),('capacitors','Tantalum is used in capacitors; conflict-zone sourcing is a risk even when reserves are sufficient.'),('solid-state','Solid-state batteries may still use lithium. This category does not automatically solve lithium scarcity.'),('infrastructure','Recycling is promising, but limited collection and recovery infrastructure restricts its impact.')],
9:[('childlabor','The review connects clean technologies with child labor and unsafe conditions upstream.'),('economicgains','Environmental costs and economic benefits fall on different countries: this is a justice issue.'),('futuregenerations','Intergenerational equity asks whether current extraction leaves adequate resources for future users.'),('repairable','Repairable, modular products can reduce demand for newly mined materials.')],
10:[('disclose','Disclosure can reveal material origins, but enforcement is needed to change sourcing practices.'),('toxic','Informal e-waste recycling can expose workers to toxins; recycling is not automatically safe.'),('restored','Mining regulation should include ecosystem restoration after extraction.'),('Taxincentives','Recycling subsidies and mandates target the demand for new mining, rather than only its impacts.')],
11:[('producer','EPR shifts end-of-life responsibility to manufacturers, encouraging longer-lived and recyclable designs.'),('financial','International standards need financial and technical support so producer countries can implement them.'),('CONCLUSION','The conclusion largely restates policy proposals; it does not rank their effectiveness or implementation costs.'),('certification','Fair-trade certification may guide buyers, but its impact depends on credible verification.')],
12:[('repair','Repair and reuse reduce replacement demand; consumers need products that actually permit repair.'),('coordinated','The final recommendation combines sourcing, mining, recycling and consumption policies.'),('implementing','These are policy recommendations, not measured evidence that the proposed package will succeed.')]
}
def norm(s):return re.sub(r'[^a-z0-9%]','',s.lower())
out=pathlib.Path('output/pdf');out.mkdir(parents=True,exist_ok=True)
for f in pathlib.Path('C:/Users/ASUS/Desktop').glob('*.pdf'):
 if not f.name.startswith(('1907.10597','Sustainable Development')):continue
 isg=f.name.startswith('1907');data=G if isg else D;rd=PdfReader(f);wr=PdfWriter();doc=pdfplumber.open(f)
 for i,p in enumerate(doc.pages):
  notes=data.get(i+1,[])
  if not notes:wr.add_page(rd.pages[i]);continue
  w,h=float(p.width),float(p.height);buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(w+185,h));c.setFillColorRGB(.97,.98,1);c.rect(w,0,185,h,fill=1,stroke=0)
  c.setFillColorRGB(.12,.22,.38);c.setFont('Helvetica-Bold',10);c.drawString(w+12,h-25,'PAGE '+str(i+1)+' | READING NOTES')
  words=p.extract_words();used=[]
  for j,(anchor,note) in enumerate(notes):
   hits=[z for z in words if (norm(anchor)==norm(z['text']) if anchor=='PoS' else norm(anchor) in norm(z['text']))]
   if not hits and anchor!='PoS':
    # Locate multi-word anchors over a short sequence.
    hits=[words[k] for k in range(len(words)) if norm(anchor) in norm(''.join(z['text'] for z in words[k:k+5]))]
   if not hits:
    print('UNMATCHED',i+1,anchor);continue
   z=next((z for z in hits if z['top']>45),hits[0]);x=z['x0'];y=h-z['bottom'];hh=z['bottom']-z['top'];col=[(.1,.35,.72),(.75,.16,.2),(.1,.48,.3)][j%3]
   line=[a for a in words if abs(a['top']-z['top'])<3 and abs(a['x0']-x)<180 and a['x0']>=x and a['x1']<=min(w-22,x+210)]
   end=max([a['x1'] for a in line]+[z['x1']]);c.setStrokeColorRGB(*col);c.setLineWidth(.8)
   c.saveState();c.setFillColorRGB(1,.83,.15);c.setFillAlpha(.25);c.rect(x-1,y-1,end-x+2,hh+2,fill=1,stroke=0);c.restoreState()
   c.line(x,y-2,end,y-2)
   if j%2:c.line(x,y-4,end,y-4)
   else:c.ellipse(x-2,y-2,z['x1']+2,y+hh+2)
   bx=18 if x<w/2 else w-15;by=y+hh/2;c.setFillColorRGB(1,1,1);c.circle(bx,by,7,fill=1,stroke=1);c.setFillColorRGB(*col);c.setFont('Helvetica-Bold',7);c.drawCentredString(bx,by-2,str(j+1))
   ny=h-55-j*((h-100)/len(notes));c.setFont('Helvetica-Bold',9);c.drawString(w+12,ny,'['+str(j+1)+']')
   c.setFont('Helvetica',9)
   for k,t in enumerate(textwrap.wrap(note,34)):c.drawString(w+12,ny-17-k*12,t)
   gloss=[('diminishing','diminishing returns 边际收益递减'),('tuning','hyperparameter tuning 超参数调优'),('epochs','epoch 训练轮次'),('FPO','FPO 浮点运算次数'),('inference','inference 推理'),('rebound','rebound effect 反弹效应'),('life-cycle','life-cycle assessment 生命周期评估'),('life cycle','life cycle 生命周期'),('intergenerational','intergenerational equity 代际公平'),('EPR','EPR 生产者责任延伸'),('NRBV','NRBV 自然资源基础观'),('consensus','consensus mechanism 共识机制'),('sourcing','ethical sourcing 负责任采购')]
   for term,translation in gloss:
    if term.lower() in note.lower():
     c.setFont('STSong-Light',8);c.drawString(w+12,ny-23-(k+1)*12,translation);break
  c.save();ov=PdfReader(buf).pages[0];ov.merge_page(rd.pages[i],over=False);wr.add_page(ov)
 target=out/('Green_AI_close_reading.pdf' if isg else 'Digital_sustainability_close_reading.pdf');wr.write(target)
 for n in [0,2,6]:
  pdfplumber.open(target).pages[n].to_image(resolution=100).save(out/(target.stem+'_'+str(n)+'.png'))
 print(target)

