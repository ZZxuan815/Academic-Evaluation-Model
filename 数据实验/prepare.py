"""Offline, reproducible preparation and baseline; never changes source files."""
from pathlib import Path
import csv, json, hashlib, random, math, statistics, copy
from collections import Counter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '加工结果'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT / '原始仓库/data/uci_higher_education_dea_sample.csv'
FIELDS = ['第一学期选课数','第二学期选课数','第一学期考核次数','第二学期考核次数','第一学期通过课程数','第二学期通过课程数','第一学期平均成绩','第二学期平均成绩']
LABELS = ['Dropout','Enrolled','Graduate']

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def validate(row):
    errors = []
    if not row.get('学生ID'): errors.append('missing_id')
    if row.get('学业结果') not in LABELS: errors.append('unknown_label')
    values = {}
    for f in FIELDS:
        v = row.get(f)
        try:
            if v is None or isinstance(v, bool) or str(v).strip() == '': raise ValueError()
            n = float(v)
            if not math.isfinite(n): raise ValueError()
        except (ValueError, TypeError):
            errors.append('invalid_number:'+f)
            continue
        values[f] = n
        if n < 0: errors.append('negative:'+f)
        if '成绩' not in f and n != int(n): errors.append('fractional_count:'+f)
    # Relational checks do not assume an undocumented grade scale.
    for term in ['第一学期','第二学期']:
        a,b = term+'通过课程数',term+'选课数'
        if a in values and b in values and values[a] > values[b]: errors.append('approved_exceeds_enrolled:'+term)
    return errors

raw = list(csv.DictReader(SOURCE.open(encoding='utf-8-sig', newline='')))
ids = [r['学生ID'] for r in raw]
issues = [{'id':r['学生ID'],'errors':validate(r)} for r in raw if validate(r)]
assert len(ids) == len(set(ids)), 'Duplicate IDs require review before splitting'
assert not issues, issues
records = []
for r in raw:
    x = dict(r)
    for f in FIELDS: x[f] = float(r[f]) if '成绩' in f else int(r[f])
    x.update({'数据类型':'真实仓库样本','attendance':None,'study':None,'sleep':None,'practice':None})
    for term in ['第一学期','第二学期']:
        x[term+'通过率'] = x[term+'通过课程数']/x[term+'选课数'] if x[term+'选课数'] else None
    x['成绩变化_原始单位'] = x['第二学期平均成绩']-x['第一学期平均成绩']
    records.append(x)
dump('真实样本.json', records)

# Stratified fixed split. No second-semester data, IDs, course codes or labels in X.
rng = random.Random(20261018)
train, test = [], []
for label in LABELS:
    group = [r for r in records if r['学业结果']==label]
    rng.shuffle(group)
    cut = int(len(group)*.8)
    train.extend(group[:cut]); test.extend(group[cut:])
assert not set(r['学生ID'] for r in train) & set(r['学生ID'] for r in test)
features = ['第一学期选课数','第一学期考核次数','第一学期通过课程数','第一学期平均成绩']
means = [statistics.mean(r[f] for r in train) for f in features]
scales = [statistics.pstdev(r[f] for r in train) or 1 for f in features]
def vector(r): return [(r[f]-m)/s for f,m,s in zip(features,means,scales)]
centers = {c:[statistics.mean(vector(r)[j] for r in train if r['学业结果']==c) for j in range(len(features))] for c in LABELS}
def predict(r):
    v = vector(r)
    return min(LABELS, key=lambda c:sum((a-b)**2 for a,b in zip(v,centers[c])))
def metrics(pred):
    cm = [[0]*3 for _ in LABELS]
    for r,p in zip(test,pred): cm[LABELS.index(r['学业结果'])][LABELS.index(p)]+=1
    per = {}
    for i,c in enumerate(LABELS):
        tp=cm[i][i]; actual=sum(cm[i]); guessed=sum(row[i] for row in cm)
        precision=tp/guessed if guessed else 0; recall=tp/actual if actual else 0
        per[c]={'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0,'support':actual}
    return {'accuracy':sum(cm[i][i] for i in range(3))/len(test),'macro_f1':statistics.mean(v['f1'] for v in per.values()),'per_class':per,'confusion_matrix_true_rows_predicted_columns':cm,'label_order':LABELS}
pred = [predict(r) for r in test]
majority = Counter(r['学业结果'] for r in train).most_common(1)[0][0]
result = {'seed':20261018,'train_count':len(train),'test_count':len(test),'features':features,'model':'standardized nearest centroid','baseline':metrics([majority]*len(test)),'experiment':metrics(pred)}
dump('预测实验结果.json',result)
dump('固定数据划分.json',{'train':[r['学生ID'] for r in train],'test':[r['学生ID'] for r in test]})
dump('基线模型参数.json',{'features':features,'means_train_only':means,'scales_train_only':scales,'centers':centers})
dump('测试集逐条预测.json',[{'id':r['学生ID'],'actual':r['学业结果'],'predicted':p,'correct':r['学业结果']==p} for r,p in zip(test,pred)])

# Synthetic corruption cases for the data preparation validator, not model accuracy.
cases=[]
def case(name, changes, expected):
    r=copy.deepcopy(raw[0]); r.update(changes)
    actual=validate(r)
    passed=(not actual) if expected is None else any(e.startswith(expected) for e in actual)
    cases.append({'name':name,'synthetic':True,'record':r,'expected_error_prefix':expected,'observed_errors':actual,'passed':passed})
case('正常记录',{},None)
for name,value in [('空白',''),('缺失',None),('非数字','abc'),('无穷','Infinity'),('非有限数','NaN'),('布尔值',True)]:
    case(name,{'第一学期平均成绩':value},'invalid_number:')
case('负数',{'第一学期选课数':-1},'negative:')
case('小数课程数',{'第一学期选课数':6.5},'fractional_count:')
case('通过数超过选课数',{'第一学期通过课程数':999},'approved_exceeds_enrolled:')
case('未知结果标签',{'学业结果':'优秀'},'unknown_label')
case('缺少学生编号',{'学生ID':''},'missing_id')
case('零通过零成绩保留',{'第一学期通过课程数':0,'第一学期平均成绩':0},None)
case('零选课零通过允许后续通过率为空',{'第一学期选课数':0,'第一学期通过课程数':0},None)
dump('合成异常测试及结果.json',cases)
assert all(c['passed'] for c in cases)
audit={'rows':len(raw),'labels':dict(Counter(r['学业结果'] for r in raw)),'duplicate_ids':len(ids)-len(set(ids)),'issues':issues,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'numeric_fields':{f:{'min':min(r[f] for r in records),'max':max(r[f] for r in records),'zeros':sum(r[f]==0 for r in records)} for f in FIELDS}}
dump('数据质量报告.json',audit)
e,b=result['experiment'],result['baseline']
report=f'''# 数据实验：先看这里

## 已完成的工作

保留原始文件，加工真实样本 {len(raw)} 条；三类结果各 {len(raw)//3} 条。学生编号无重复，当前数值及课程数关系校验发现 {len(issues)} 条异常。另建 {len(cases)} 个合成数据校验案例，全部通过。合成案例不参与训练和准确率计算。

加工结果在同级“加工结果”目录，JSON 文件保留字段名称、数值类型和缺失值。睡眠、出勤、学习时长、实践数据均保留 null，没有伪造。保留平均成绩原始单位；未核实量纲前不转换为百分制。通过率=通过课程数÷选课数，零分母返回空值。原始零成绩保留，不擅自当作缺失填补，也不解释为某次考试得零分。

## 跑出来的效果

已训练一个小型“标准化最近中心”基线模型，不是千问微调。只使用第一学期的选课数、考核次数、通过数和平均成绩预测最终学业结果。它先从训练集中算出各类学生的平均特征，再判断测试学生更接近哪一类。标准化参数仅从训练集计算。

固定随机种子 20261018，分层划分训练 {len(train)} 条、测试 {len(test)} 条。测试集没有参与拟合，未为提高成绩反复选择切分。

| 方法 | 测试准确率 | 宏平均 F1 |
|---|---:|---:|
| 永远猜训练集最多的一类（并列时固定选一类） | {b['accuracy']:.1%} | {b['macro_f1']:.3f} |
| 标准化最近中心 | {e['accuracy']:.1%} | {e['macro_f1']:.3f} |

准确率是“总共猜对多少”；宏平均 F1 是“每一类分别看查得准、找得全，再平均”，可以避免只照顾某一类。逐类召回率、混淆矩阵见加工结果/预测实验结果.json；每个学生的预测见测试集逐条预测.json。

测试集只有 {len(test)} 条，错一条就改变 {100/len(test):.2f} 个百分点。仓库预先按结果抽样且过滤学业产出，已不同于原始人群分布。因此结果仅说明这批筛选样本上的基线表现，不能据此声称真实部署准确率或因果效果。当前未知原始学生对应关系，只能检查仓库编号重复。

## 怎样判断我们的平台有效

| 要验证什么 | 怎么测 | 本次状态 |
|---|---|---|
| 数据处理是否可靠 | 缺失、文本、非有限数、负数、小数计数、关系冲突、零值分别测试 | {len(cases)} 个离线校验案例通过；不代表网页导入已通过 |
| 学业结果能否预测 | 固定未见测试集，与简单基线比较准确率、宏 F1、各类召回率 | 已完成上述小实验 |
| 问卷能否选对指标 | 建立独立自然语言题库，两人先标注应选/排除指标和是否追问，再测指标准确率、召回率、排除遵从率 | 尚未建立正式人工标注题库；本数据不含问卷语言 |
| 权重是否合理 | 等权对照、权重强度变化、单指标改善前后比较，再由老师复核有争议案例 | 本次预测不能证明权重合理 |
| 激励有没有帮助 | 自愿试用，随机分配普通计划与激励计划，提前约定七天完成率和退出率，并收集负担感受 | 尚未开展；打卡次数不等于成绩提升 |

不能保证覆盖所有未来情况。这里覆盖的是明确列出的数据校验情形；网页文件解析、文件大小、重复导入、模型超时和真实用户行为还需专项验证。建议先冻结问卷标注规则与主评价指标，再扩充数据；不要根据测试结果回改答案。

## 如何使用

1. 查看本说明中的结果表，汇报时说“完成公开数据加工与基线实验”。
2. 如需检查某条结果，打开加工结果/测试集逐条预测.json。
3. 当前 JSON 是离线实验数据包，尚未接入网页批量导入。不要把课程通过率映射为出勤率，也不要用假睡眠值填满网页。
4. 后续网页可增加“公开学业数据实验”入口，展示两学期通过率与成绩，和个人画像功能分开。
5. 重新运行 prepare.py 会按相同种子更新结果，不改原始数据。

## 来源与许可

仓库：https://github.com/Nitrene123/college-student-dea-evaluation-system

固定版本：43c04d6119cef89819bd5fc343f2f448447cdbc9。使用其中 data/uci_higher_education_dea_sample.csv，仓库说明为 UCI 697 的 180 条筛选样本。仅处理学生数据，医院、经济示例未混入。

原始数据：Realinho, V., Vieira Martins, M., Machado, J., & Baptista, L. (2021). Predict Students' Dropout and Academic Success. UCI Machine Learning Repository. https://doi.org/10.24432/C5MC89 。许可 CC BY 4.0：https://creativecommons.org/licenses/by/4.0/ 。本次增加类型转换、通过率、变化值、划分和模型预测；未改变原始文件。原始全集 4424 条，本次未下载全集。仓库代码的 MIT 许可不能替代数据许可。
'''
(ROOT/'先看这里_数据与效果说明.md').write_text(report,encoding='utf-8')
print(json.dumps({'audit':audit,'experiment':result,'synthetic_passed':len(cases)},ensure_ascii=False,indent=2))
