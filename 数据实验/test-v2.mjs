import {scoreReport} from '../平台/server/accounts.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
const root=new URL('./',import.meta.url), real=JSON.parse(readFileSync(new URL('加工结果/真实样本.json',root),'utf8'));
const ids=['grade','attendance','study','sleep','practice'];
let tested=0,invalid=0,zeroMismatch=0,drops=0,maxDrop=0,worst=null,maxGap=0;
const examples=[];
for(let mask=1;mask<32;mask++)for(const alpha of [0,1,3,5])for(const attendance of [0,80,100])for(const study of [0,2,4])for(const sleep of [0,5,8,11,16]){
 const selected=ids.filter((_,i)=>mask&(1<<i));let prior=null;
 for(let grade=0;grade<=100;grade++){
  const data={grade,previous:70,attendance,study,sleep,practice:3};
  const r=scoreReport({selected,data,mode:'variable',alpha}),e=scoreReport({selected,data,mode:'equal',alpha});tested++;
  if(!Number.isFinite(r.score)||r.score< -1e-9||r.score>100+1e-9||Math.abs(r.weights.reduce((a,b)=>a+b,0)-1)>1e-9)invalid++;
  if(alpha===0&&Math.abs(r.score-e.score)>1e-9)zeroMismatch++;
  maxGap=Math.max(maxGap,Math.abs(r.score-e.score));
  if(prior&&selected.includes('grade')&&r.score<prior.score-1e-9){drops++;const d=prior.score-r.score;if(d>maxDrop){maxDrop=d;worst={selected,alpha,data,previousGrade:grade-1,previousScore:prior.score,currentScore:r.score}}}
  prior=r;
 }
}
for(const grade of [40,60,80,100]){
 const data={grade,previous:70,attendance:100,study:4,sleep:0,practice:3};
 examples.push({grade,...scoreReport({selected:['grade','attendance','study','sleep'],data,mode:'variable',alpha:5})});
}
// Local perturbations test continuity around 60 and 80, without claiming a proof.
let maxLocalJump=0;
for(const grade of [60,80])for(const sleep of [0,8,16]){
 const run=g=>scoreReport({selected:ids,data:{grade:g,previous:70,attendance:95,study:2,sleep,practice:3},mode:'variable',alpha:5}).score;
 maxLocalJump=Math.max(maxLocalJump,Math.abs(run(grade+.000001)-run(grade-.000001)));
}
const result={formulaVersion:'v2',realRows:real.length,realCompleteRows:real.filter(r=>['attendance','study','sleep','practice'].every(k=>r[k]!==null)).length,synthetic:true,tested,invalid,zeroMismatch,drops,maxDrop,worst,maxGap,maxLocalJump,examples};
writeFileSync(new URL('加工结果/新变权测试结果.json',root),JSON.stringify(result,null,2));
const w=worst;
writeFileSync(new URL('新变权测试说明.md',root),`# 新变权公式测试结果\n\n本次直接调用平台后端 scoreReport，测试公式版本 v2。没有重新训练分类器，不能用此前61.1%的预测准确率表示本公式有效。\n\n## 真实数据可用性\n\n原有${real.length}条真实数据全部缺少出勤、学习时长、睡眠和实践，完整可评分记录为0。本次没有补造这些值，也没有擅自转换原始成绩量纲，因此没有给真实学生生成新综合分。\n\n## 合成情景测试\n\n共${tested}次评分，覆盖31种非空指标组合、α=0/1/3/5、成绩0至100逐分变化、出勤0/80/100、学习0/2/4小时、睡眠0/5/8/11/16小时。实践固定3次，未穷尽所有数值。\n\n- 非有限结果、超出0—100、权重和异常：${invalid}次。\n- α=0与等权不一致：${zeroMismatch}次。\n- 60与80附近±0.000001扰动的最大分差：${maxLocalJump}。局部检查支持连续性，不代表评分合理性。\n- 与等权最大绝对差：${maxGap.toFixed(3)}分。\n- 包含成绩指标的组合中，成绩增加1分而总分下降：${drops}次相邻比较；这些是网格案例，不是人群发生率。\n\n## 发现的问题\n\n最大下降案例：指标${w.selected.join('、')}，α=${w.alpha}；出勤${w.data.attendance}%，学习${w.data.study}小时，睡眠${w.data.sleep}小时，实践${w.data.practice}次。其他输入不变，成绩从${w.previousGrade}提高到${w.data.grade}，综合分从${w.previousScore.toFixed(4)}降到${w.currentScore.toFixed(4)}，下降${maxDrop.toFixed(4)}分。\n\n原因：成绩提高会把权重转向状态；当状态较差时，这个转移可能超过成绩提高带来的加分。公式连续不等于单调。未擅自更改现有公式。\n\n## 建议\n\n目前不宜把动态总分升降直接解释为学生进步或退步。建议固定权重的综合分用于纵向趋势，动态权重用于决定关注重点和反馈篇幅；或者另外设计并验证满足单调性的计分公式。固定一轮评估的参考权重也可用于该轮比较，但跨轮变化仍需说明。\n\n还需补齐真实问卷与行为数据、教师评价和用户试用，才能判断教育有效性。本次测试只能验证数值性质和揭示反例。\n`);
console.log(JSON.stringify({...result,examples:undefined},null,2));
