from docx import Document
from docx.shared import Pt
import re,pdfplumber,pathlib
p='output/docx/ESS_101_SR4_Vocab20_Shirley_25722118.docx';d=Document(p)
answers=[
'''1.Because this article is directly related to both my major (computer science) and our essay topic on sustainable development. It looks at the energy used when people run AI models on a laptop.
2.What I found most useful was the comparison between smaller and larger models. The authors report that smaller models use up to 62% less energy per token in their tests. This gives me a concrete example of Green AI.
3.The article helped me understand that training is not the only source of energy use. Running a model to answer questions or generate text also uses electricity.
4.It also showed me that choosing a model is a balance between accuracy, speed and energy, rather than simply choosing the largest model.''',
'''1.I think the main strength of the article is that it gives practical comparisons. It tests five models on three types of tasks and presents the results in tables, which makes the findings easier to follow.
2.Another strength is that the authors explain their hardware and settings. For example, they use one M4 Pro laptop with 48 GB memory and the same quantization format for all five models.
3.As for weaknesses, the whole-system power is estimated rather than measured directly. The experiment also uses only one computer, so the results may not apply to other devices.
4.I also noticed a possible calculation problem. Using the paper's formula, 0.09 J per token and 708 g CO2/kWh give about 17.7 mg CO2 per 1,000 tokens, but Table IV reports 0.18 mg. I would check this before using its carbon figures.
5.The generated code is not checked for correctness. A model that saves energy but gives wrong answers may not be the best choice.''',
'''I intend to use two aspects of this article in my own essay.
1.First, the comparison between smaller and larger models gives me an example for the Solution section. Choosing a suitable model could reduce unnecessary computation instead of always using the biggest model.
2.Second, I want to use the limitations in my Evaluation section. Since the study uses one laptop and estimated system power, it does not prove that local AI is always greener than cloud AI. This helps me explain why efficiency solutions need careful evaluation.''',
'''1.The version I read was submitted to arXiv on 24 August 2026, so it is quite recent compared with my earlier readings.
2.The article record identifies it as version 1. I am using that version rather than assuming that it is the final conference paper.
3.Compared with Green AI, this article gives a newer practical example of measuring efficiency. However, new hardware and models could change its results, so being recent does not mean that every conclusion will remain true.''',
'''1.I think the article is useful, but I would use its results carefully.
2.It is available on arXiv, and the authors state that it was accepted at IEEE ICCUBEA 2026. However, arXiv itself is a preprint repository, not a peer-reviewed journal.
3.Kannan is from Pimpri Chinchwad College of Engineering, Firke is from Red Hat, and Bengle and Deshmukh are listed as independent researchers.
4.The paper describes its methods and cites earlier work, including Green AI. These details make it easier to evaluate.
5.However, the estimated system power and possible carbon-unit error make me less confident in some of its numerical claims. I would compare them with other studies.''',
'''Purpose/research question:
to compare the speed, energy use and carbon footprint of running different open-source language models on Apple Silicon.

Main argument:
1.AI should be evaluated by energy use as well as accuracy and speed.
2.A larger model is not automatically the best choice for every task.

Key findings / conclusions:
1.The authors test five models on three tasks using an M4 Pro laptop with 48 GB memory and collect over 1,500 inference records.
2.Smaller models use up to 62% less energy per token in the tested setup.
3.Qwen 2.5 achieves 57% accuracy on the selected MMLU questions, while Gemma 2 achieves 61%. The authors consider Qwen a useful balance between accuracy and efficiency.
4.The authors recommend reporting energy per token alongside other performance measures.
5.The results are limited by one hardware platform, estimated whole-system power and a small accuracy benchmark. The carbon figures also need checking.

Other points useful for my essay:
1.This article gives me a practical example of Green AI for my Solution section.
2.I can use the limitations to show that energy savings must be evaluated carefully rather than assumed.'''
]
for i,a in enumerate(answers):d.tables[1].rows[i].cells[1 if i<5 else 0].text=a
quotes=[
(1,'The rapid proliferation of Large Language Models (LLMs) has raised concerns about their environmental impact during inference.'),
(4,'Smaller models (3–4B) achieve 2.6–4.2× higher throughput than 7–9B models.'),
(1,'Pareto analysis identifies Qwen 2.5 (7B) as the optimal accuracy-efficiency trade-off at 57% MMLU and 59 tokens/s, while Llama 3.2 (3B) suits latency-critical applications at 175 tokens/s.'),
(6,'We evaluate only Q4_K_M quantization.'),
(2,'Its methodological contribution is a dual-source measurement pipeline that fuses direct hardware power readings from macOS powermetrics with Ollama’s nanosecond-precision per-call timing to attribute energy at both CPU+GPU package and full-system granularity, a level of decomposition absent from prior work that relies solely on wall-power meters or manufacturer TDP ratings.'),
(4,'The entire pipeline—model pull, warm-up, inference, and logging—was orchestrated by a single Python script to eliminate manual timing errors and ensure reproducibility.'),
(6,'Different quantization levels (Q3_K_S, Q5_K_M, Q8_0, FP16) offer different accuracy-energy trade-offs.'),
(5,'For edge deployment, that trade favors Qwen 2.5.'),
(4,'To avoid memory contention and thermal carry-over, only one model was kept in memory at a time, and the previous model was unloaded before the next model was loaded.'),
(5,'We suspect this comes down to a poor fit between Mistral’s instruction tuning and our zero-shot prompt at Q4_K_M precision.'),
(1,'The rapid proliferation of Large Language Models (LLMs) has raised concerns about their environmental impact during inference.'),
(1,'While significant attention has been paid to the energy costs of training large models (Strubell et al. [6] estimated that training a single Transformer model emits as much CO2 as five cars over their lifetimes, and Patterson et al. [7] documented that training GPT-3 consumed 1,287 MWh), the cumulative environmental impact of inference is increasingly dominant [8].'),
(4,'MMLU (short outputs, ∼15 tokens) yields the highest throughput, while code generation (∼200 tokens) yields the lowest due to growing KV-cache memory overhead.'),
(6,'Since LLM inference is memory-bandwidth-bound, DRAM is a significant energy component.'),
(2,'Xu et al. [5] surveyed these platforms and identified the same three recurring bottlenecks: memory bandwidth, thermal headroom, and energy budget.'),
(6,'While stratified sampling across 10 subjects ensures representation, a larger sample would reduce variance in accuracy estimates.'),
(6,'We evaluate single-request inference only.'),
(2,'Dettmers et al. [27] showed that INT8 quantization halves the memory footprint with minimal quality degradation; Frantar et al. [28] later pushed this to 4 bits with GPTQ.'),
(2,'Because compression is held fixed across every model, any difference we measure in power draw can be attributed to the architecture itself and not to the quantizer.'),
(1,'Recent work has begun quantifying inference energy, revealing enormous variation across hardware and models.')]
# Concurrent entry needs the derivative in a complete sentence.
quotes[16]=(6,'Batched inference, which is common in production serving, may exhibit different power and throughput characteristics on Apple Silicon due to shared memory contention.')
# Use concurrency derivative instead, present in a complete sentence.
quotes[16]=(2,'On the system-configuration side, Stojkovic et al. [22] found that tuning model parallelism, speculative decoding, and batch size cuts energy by up to 29% at low concurrency, but the gains reverse under heavy load.')
def norm(t):return re.sub('[^a-z0-9]','',t.lower())
pdf=pdfplumber.open('C:/Users/ASUS/Desktop/2608.28667v1.pdf')
cell=d.tables[1].rows[6].cells[0];idx=0
for p in cell.paragraphs:
 if p.text.startswith('Vocabulary development'):
  p.text='Vocabulary development\nLine references are counted manually within each column from the first printed text line, including headings. Left and right columns are counted separately.'
 if p.text.startswith('Word in Context I:'):
  page,sent=quotes[idx];source=pdf.pages[page-1];best=None
  for col,(l,r) in enumerate([(20,source.width/2),(source.width/2,source.width-20)],1):
   lines=(source.crop((l,0,r,source.height)).extract_text(x_tolerance=2) or '').splitlines();combined='';mapping=[]
   for no,line in enumerate(lines,1):
    z=norm(line);combined+=z;mapping.extend([no]*len(z))
   needle=norm(sent)[:65];at=combined.find(needle)
   if at>=0:best=(col,mapping[at]);break
  if best is None:raise ValueError((idx,page,sent[:65]))
  col,line=best;p.text=f"Word in Context I: '{sent}' (Kannan et al., p. {page}, {'left' if col==1 else 'right'} column, L{line}).";idx+=1
 if p.text.startswith('Synonyms / Antonyms:'):
  x=p.text.split(': ',1)[1].rstrip('.');parts=x.split(';');p.text='Synonyms/Antonyms: Syn: '+parts[0].strip()+'; Ant: '+(';'.join(parts[1:]).strip() or '(no direct antonym)')+'.'
 if p.text.startswith('Word in Context II:'):
  x=p.text.replace('Word in Context II: (a) ','',1);a,b=x.split(' (b) ',1);p.text=f"Word in Context II: (a) '{a}' (b) '{b}'"
for table in d.tables:
 seen=set()
 for row in table.rows:
  for cell in row.cells:
   if cell._tc in seen:continue
   seen.add(cell._tc)
   for p in cell.paragraphs:
    p.paragraph_format.line_spacing=1.08;p.paragraph_format.space_after=Pt(5)
    for run in p.runs:run.font.name='Calibri';run.font.size=Pt(11)
out=pathlib.Path('output/docx/ESS_101_SR4_Strict_Template_Shirley_25722118.docx');d.save(out);print('Verified contexts:',idx);print(out.resolve())
