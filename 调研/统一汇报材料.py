from pathlib import Path
import shutil
root=Path.cwd(); pack=root/'周五汇报材料'; originals=pack/'04_参考原文'
refs=[('R1','俞立平、潘伟波（2022）','学术评价中个体权重、整体权重与伪权重问题研究——以线性评价及JCR经济学期刊评价为例','论文','俞立平和潘伟波2022_设计权重与实际权重.pdf','已取得全文；已核对Z值与Sigmoid式(3)(4)，PDF第4页','标准化与设计权重'),('R2','Liu、Yu、Liu、Hu（2019）','Variable weights theory and its application to multi-attribute group decision making with intuitionistic fuzzy numbers on determining decision maker’s weights','论文','Liu等2019_状态变权理论.pdf','已取得全文；已核对第2节式(5)，并非全篇精读完成','状态变权框架'),('R3','Lalor、Wu、Yu（2016）','Building an Evaluation Scale using Item Response Theory','会议论文','Lalor等2016_IRT评价模型.pdf','已取得全文；已核对第2节式(1)，公式印刷页待补','IRT双参数和三参数'),('R4','OECD / European Union / EC-JRC（2008）','Handbook on Constructing Composite Indicators: Methodology and User Guide','手册','OECD2008_综合指标构建手册.pdf','已取得全文；相关标准化及赋权章节已查阅，公式页码待补','标准化、赋权和敏感性分析'),('L1','贺玉婷（2021）','变权层次分析法的高校英语教学效果评价','待全文线索',None,'仅核实期刊条目与摘要，未取得全文','教育应用线索，不能声称已核对公式'),('L2','苏为华（1993）','对数型功效系数法初探','待全文线索',None,'仅核实期刊条目与摘要，未取得全文','功效系数补充线索')]
manifest='# 文献与原文对应总表\n\n本表为统一编号依据。已取得全文的是三篇论文和一本手册；另有两条摘要线索。取得全文不等于全文精读完成。任务单不计入参考文献。\n\n|编号|作者年份|完整题名|类型|本地文件（04_参考原文内）|核验状态|用途|\n|---|---|---|---|---|---|---|\n'
for rid,author,title,kind,file,status,use in refs:
    if file: assert (originals/file).is_file(),file
    manifest+='|'+ '|'.join([rid,author,title,kind,file or '无全文PDF',status,use])+'|\n'
manifest+='\n平台指数变权与分段阈值均为项目演示设定，不挂靠任何文献编号。分段赋权的教育实例与部分公式出处仍未补齐，公式笔记继续保留“初稿”。\n'
(pack/'文献与原文对应总表.md').write_text(manifest,encoding='utf-8')
p=root/'调研/周五汇报稿.md';s=p.read_text(encoding='utf-8');start=s.index('目前重点核对了');end=s.index('\n\n前端',start)
s=s[:start]+'''目前汇报材料与原文统一为以下四项：

- [R1] 俞立平、潘伟波（2022）：讨论设计权重与实际贡献，已核对Z值与Sigmoid公式。
- [R2] Liu、Yu、Liu、Hu（2019）：讨论状态变权，已核对第2节式(5)的基础权重与状态因子归一化框架。
- [R3] Lalor、Wu、Yu（2016）：讨论IRT评价模型，已核对双参数和三参数关系，作为题目难度与区分度的拓展参考。
- [R4] OECD / European Union / EC-JRC（2008）：综合指标构建手册，作为标准化、赋权与敏感性分析的基础参考。

以上是三篇论文和一本手册，均有本地全文；尚未全部精读，具体核验范围见文献与原文对应总表。[L1]贺玉婷2021和[L2]苏为华1993仅核实条目与摘要，单列为待阅读全文线索，不计入已取得原文的四项。原资料中误标为郭亚军2023的PDF与[R1]相同，不重复计数。''' +s[end:];p.write_text(s,encoding='utf-8')
p=root/'调研/重点文献阅读卡片.md';s=p.read_text(encoding='utf-8');s=s.replace('## 1 标准化和综合指标','## R4 标准化和综合指标').replace('## 2 设计权重与实际贡献','## R1 设计权重与实际贡献').replace('## 3 状态变权理论','## R2 状态变权理论').replace('## 4 教育场景变权应用','## L1 教育场景变权应用 仅摘要').replace('## 5 IRT模型','## R3 IRT模型').replace('## 6 功效系数方法补充','## L2 功效系数方法补充 仅摘要');s+='\n## 本地原文对应\n\n统一文件名与获取状态见汇报材料根目录的文献与原文对应总表.md。R1至R4有PDF；L1和L2没有全文PDF。\n';p.write_text(s,encoding='utf-8')
p=root/'调研/公式笔记初稿.md';s=p.read_text(encoding='utf-8');s+='\n## 统一文献编号\n\nR1：俞立平、潘伟波2022，对应群体Z值与Sigmoid。R2：Liu等2019，对应状态变权一般式。R3：Lalor等2016，对应IRT。R4：OECD等2008，对应标准化与综合指标。L1、L2仅为摘要线索，不为未核实公式背书。具体PDF文件见文献与原文对应总表。\n';p.write_text(s,encoding='utf-8')
for f in (root/'调研').glob('*.md'):
    dest=pack/('01_汇报正文' if f.name=='周五汇报稿.md' else '02_公式与文献')/f.name
    if dest.exists():shutil.copy2(f,dest)
for name in ['00_先看这里.md']:
    p=pack/name;s=p.read_text(encoding='utf-8');s=s.replace('04_参考原文存放已核对的中文重点论文和学姐任务单，供现场查阅。其他公开文献的链接在阅读卡片中。','04_参考原文存放R1至R4共三篇论文和一本手册的全文PDF，以及学姐任务单。先查看根目录的文献与原文对应总表.md，L1和L2只有摘要线索。');p.write_text(s,encoding='utf-8')
(originals/'原文清单与获取状态.md').write_text(manifest,encoding='utf-8')
p=root/'文献调研进度.md';p.write_text('# 文献调研当前状态\n\n统一清单见 周五汇报材料/文献与原文对应总表.md。\n\nR1至R4为三篇论文和一本手册，均有全文。L1与L2仅有条目与摘要。工程领域变权文章仅为早期检索线索，未纳入本次汇报主文献。\n\n公式笔记仍为初稿，需补齐部分页码与分段赋权文献。浏览器实际交互仍未完整验证。\n',encoding='utf-8')
p=root/'调研/资料核验与周五汇报.md';s=p.read_text(encoding='utf-8');s+='\n## 当前汇报统一口径\n\n以文献与原文对应总表为准：R1至R4三篇论文和一本手册有全文，L1、L2只有摘要。具体汇报采用更新后的周五汇报稿。\n';p.write_text(s,encoding='utf-8');shutil.copy2(p,pack/'02_公式与文献'/p.name)
for source in (root/'调研').glob('*.md'):
    dest=pack/('01_汇报正文' if source.name=='周五汇报稿.md' else '02_公式与文献')/source.name
    if dest.exists():assert source.read_bytes()==dest.read_bytes(),source.name
print('PASS: four referenced PDFs exist; all packaged Markdown copies match source; report, cards, formula notes, overview and status synchronized.')
