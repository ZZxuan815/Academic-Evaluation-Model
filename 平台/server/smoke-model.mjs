const cases=[
 ['我想了解成绩和睡眠，不考虑实践活动',['grade','sleep'],['practice']],
 ['只评估出勤情况',['attendance'],['grade','study','sleep','practice']],
 ['我不知道想评估什么',[],[]]
];
let failures=0;
for(const [text,required,excluded] of cases){
 const start=Date.now();
 try{const response=await fetch('http://127.0.0.1:8787/api/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text}),signal:AbortSignal.timeout(65000)});const result=await response.json();const ids=(result.indicators||[]).map(i=>i.id);const ok=response.ok&&required.every(id=>ids.includes(id))&&excluded.every(id=>!ids.includes(id))&&(required.length>0||Boolean(result.question));if(!ok)failures++;console.log(JSON.stringify({text,ok,elapsedMs:Date.now()-start,result}));}catch(error){failures++;console.log(JSON.stringify({text,ok:false,error:error.message}));}
}
process.exitCode=failures?1:0;
