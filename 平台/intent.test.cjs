const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
async function run(note, fail=false, model=[]){
 const nodes=new Map();
 function node(){return {value:'',hidden:false,children:[],dataset:{},checked:false,append(...xs){this.children.push(...xs)},replaceChildren(){this.children=[]},addEventListener(){},before(){},scrollIntoView(){},querySelectorAll(selector){return selector==='[data-indicator]:checked'?nodes.get('intent-result').children.flatMap(l=>l.children).filter(i=>i.dataset?.indicator&&i.checked):[]}};}
 const get=id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id)};
 get('portrait-state').value='成绩有起伏';get('portrait-barrier').value='时间安排不稳定';get('portrait-time').value='5';get('intent-text').value=note;
 const choices=['grade','attendance','study','sleep','practice'].map(value=>({value,checked:false}));
 const document={createElement:node,createTextNode:text=>({text}),getElementById:get,querySelector:()=>node(),querySelectorAll:s=>s==='#portrait-goals input:checked'?[{value:'study'}]:s==='#choices input'?choices:[]};
 const context=vm.createContext({document,$:get,fields:choices.map(c=>[c.value,c.value]),lastReport:null,refreshExtras(){},Event:class{},AbortSignal,window:{dispatchEvent(){}},fetch:async()=>{if(fail)throw Error('offline');return {ok:true,json:async()=>({indicators:model})}}});
 vm.runInContext(fs.readFileSync(__dirname+'/intent.js','utf8'),context);
 await get('intent-match').onclick();get('intent-confirm').onclick();
 return {ids:choices.filter(c=>c.checked).map(c=>c.value),context};
}
(async()=>{
 for(const failure of [true,false]){
  const r=await run('我最近睡眠不好，想看看睡眠问题',failure);
  assert.ok(r.ids.includes('sleep'),'explicit sleep must survive offline or model omission');
  assert.ok(r.context.window.currentPortrait.selected.includes('sleep'));
 }
 const excluded=await run('不用评估睡眠',false,[{id:'sleep',reason:'model suggested'}]);
 assert.ok(!excluded.ids.includes('sleep'),'explicit exclusion overrides model');
 const irrelevant=await run('我想提高成绩',true);assert.ok(!irrelevant.ids.includes('sleep'));
 console.log('PASS: questionnaire -> recommendation -> confirmed selection, model omission, offline fallback, exclusion and unrelated text. DOM simulation.');
})().catch(e=>{console.error(e);process.exitCode=1});
