import {scoreReport} from '../平台/server/accounts.mjs';
import {writeFileSync} from 'node:fs';
const root=new URL('./加工结果/',import.meta.url);
let seed=20261018;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};
const clamp=(v,a,b)=>Math.round(Math.max(a,Math.min(b,v))*10)/10;
const records=[];const patterns=['逐步改善','逐步回落','上下波动','基本稳定','状态改善','成绩改善但作息差'];
for(let person=0;person<180;person++){
 const pattern=patterns[person%patterns.length],base=35+random()*60;
 for(let visit=0;visit<5;visit++){
  const change=pattern==='逐步改善'?visit*3:pattern==='逐步回落'?-visit*3:pattern==='上下波动'?[0,6,-4,8,-2][visit]:pattern==='成绩改善但作息差'?visit*3:0;
  const data={grade:clamp(base+change,0,100),previous:clamp(base,0,100),attendance:clamp(75+random()*25,0,100),study:clamp(.5+random()*4,0,12),sleep:pattern==='状态改善'?5+visit*.6:pattern==='成绩改善但作息差'?4:clamp(5+random()*5,0,16),practice:Math.floor(random()*8)};
  if(pattern==='基本稳定')Object.assign(data,{grade:clamp(base,0,100),attendance:90,study:2,sleep:8,practice:3});
  const report=scoreReport({data,selected:['grade','attendance','study','sleep','practice'],mode:'variable',alpha:5});
  records.push({synthetic:true,source:'完全人工生成，未混入真实学生数据',person:`SYN-${String(person+1).padStart(3,'0')}`,visit:visit+1,pattern,...report});
 }
}
let errors=0;for(const r of records){const equal=scoreReport({...r,mode:'equal',alpha:0});if(Math.abs(equal.score-r.score)>1e-9||equal.group!==r.group)errors++;}
writeFileSync(new URL('合成学生五次评估.json',root),JSON.stringify(records,null,2));
writeFileSync(new URL('合成学生五次评估.csv',root),'\ufeff'+['数据类型,学生编号,次数,情景,成绩,上次参考成绩,出勤率,学习小时,睡眠小时,实践次数,固定等权分数',...records.map(r=>['完全合成',r.person,r.visit,r.pattern,r.data.grade,r.data.previous,r.data.attendance,r.data.study,r.data.sleep,r.data.practice,r.score.toFixed(3)].join(','))].join('\n'));
writeFileSync(new URL('../合成数据测试说明.md',root),`# 完整合成数据测试\n\n随机种子20261018。完全人工生成180名虚拟学生，每人5次评估，共900条完整记录。数据不代表真实学生，不用于证明准确率或激励有效。\n\n涵盖六种生成情景：${patterns.join('、')}。情景名描述输入生成规则，不保证综合分一定按该方向变化，因为其他指标也可能变化。基本稳定情景所有输入固定。previous字段保持初始成绩作为参考，不表示每次更新为上一条成绩。\n\n直接调用当前后端v3公式，检查全部900条记录：改变反馈模式不改变评分或历史分组，失败${errors}条。记录含固定评分、动态反馈比例与分组。\n\n文件在加工结果/合成学生五次评估.json及.csv。未写入你的个人账号，以免污染真实历史；可用CSV中的任一行手动填写网页验证。\n`);
if(errors)throw Error('invariance failure');console.log('PASS: 180 synthetic students, 900 complete records, 6 patterns; 900 attention-independent score/group checks.');
