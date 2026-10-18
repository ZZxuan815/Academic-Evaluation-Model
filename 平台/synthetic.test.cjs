const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const names=['inputs','choices','direction','mode','alpha','report','score','comparison','tags','feedback','details','radar','error','evaluate','sample','recommend','export','grade','previous','attendance','study','sleep','practice'];
const elements=Object.fromEntries(names.map(id=>[id,{value:'',innerHTML:'',textContent:'',hidden:false,addEventListener(){}}]));
Object.values(elements).forEach(el=>{let value='';Object.defineProperty(el,'value',{get:()=>value,set:v=>value=String(v)});});
elements.direction.value='all';elements.mode.value='variable';elements.alpha.value='5';
const order=['grade','attendance','study','sleep','practice'];
const choices=order.map(value=>({value,checked:true,addEventListener(){}}));
const document={getElementById:id=>elements[id],querySelectorAll:s=>s==='#choices input:checked'?choices.filter(c=>c.checked):s==='#choices input'?choices:Object.values(elements)};
const context=vm.createContext({document,console,Math,Number,Error,setTimeout});
vm.runInContext(fs.readFileSync(__dirname+'/app.js','utf8'),context);
const getReport=()=>JSON.parse(vm.runInContext('JSON.stringify(lastReport)',context));
const fill=r=>{for(const k of ['grade','previous','attendance','study','sleep','practice'])elements[k].value=String(r.data[k]);choices.forEach(c=>c.checked=r.selected.includes(c.value));elements.mode.value=r.mode;elements.alpha.value=String(r.alpha);};
const records=JSON.parse(fs.readFileSync(path.join(__dirname,'..','数据实验','加工结果','合成学生五次评估.json'),'utf8'));
(async()=>{
 const {scoreReport}=await import('./server/accounts.mjs');
 const failures=[];
 for(const r of records){
  const label=`${r.person} 第${r.visit}次 ${r.pattern}`;
  try{
   fill(r);elements.evaluate.onclick();
   assert.equal(elements.error.textContent,'',`${label} 网页报错: ${elements.error.textContent}`);
   assert.equal(elements.report.hidden,false,`${label} 报告未生成`);
   const fe=getReport();
   assert.equal(fe.formulaVersion,'v3',`${label} 公式版本`);
   assert.deepEqual([...fe.selected].sort(),[...r.selected],`${label} 指标集合`);
   assert.ok(Math.abs(fe.score-r.score)<=1e-9,`${label} 网页分数 ${fe.score} ≠ 记录 ${r.score}`);
   assert.ok(Math.abs(Number(elements.score.textContent)-r.score)<=0.0500001,`${label} 显示分数 ${elements.score.textContent} ≠ 记录 ${r.score}`);
   const jsonAw=Object.fromEntries(r.selected.map((id,i)=>[id,r.attentionWeights[i]]));
   for(let i=0;i<fe.selected.length;i++)assert.ok(Math.abs(fe.attentionWeights[i]-jsonAw[fe.selected[i]])<=1e-9,`${label} 关注比例 ${fe.selected[i]}`);
   for(const w of fe.weights)assert.ok(Math.abs(w-1/fe.selected.length)<=1e-12,`${label} 固定等权`);
   elements.mode.value='equal';elements.evaluate.onclick();
   assert.equal(elements.error.textContent,'',`${label} 等权模式报错`);
   const eq=getReport();
   assert.ok(Math.abs(eq.score-fe.score)<=1e-9,`${label} 切换反馈模式后评分改变`);
   for(const w of eq.attentionWeights)assert.ok(Math.abs(w-1/eq.selected.length)<=1e-12,`${label} 等权模式关注比例`);
   const be=scoreReport({data:r.data,selected:r.selected,mode:r.mode,alpha:r.alpha});
   assert.ok(Math.abs(be.score-r.score)<=1e-9,`${label} 后端分数 ${be.score} ≠ 记录 ${r.score}`);
   assert.equal(be.group,r.group,`${label} 历史分组`);
   assert.ok(Math.abs(be.score-fe.score)<=1e-9,`${label} 前后端评分不一致`);
   for(let i=0;i<be.attentionWeights.length;i++)assert.ok(Math.abs(be.attentionWeights[i]-r.attentionWeights[i])<=1e-12,`${label} 后端关注比例`);
  }catch(e){failures.push(e.message);}
 }
 if(failures.length){
  console.error(`FAIL: ${failures.length}/${records.length} 条合成记录未通过`);
  failures.slice(0,10).forEach(f=>console.error(' - '+f));
  process.exit(1);
 }
 console.log(`PASS: ${records.length} 条合成记录（180人×5次，6情景）全部通过：网页填写生成报告、显示分数、关注比例、切换反馈模式不改分、前后端评分与历史分组一致。DOM 模拟执行，非浏览器渲染。`);
})();
