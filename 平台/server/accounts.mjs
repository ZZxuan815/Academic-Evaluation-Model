import {DatabaseSync} from 'node:sqlite';
import {randomBytes,randomUUID,scrypt as scryptCallback,timingSafeEqual,createHash} from 'node:crypto';
import {promisify} from 'node:util';
import {mkdirSync} from 'node:fs';
const scrypt=promisify(scryptCallback);
const digest=s=>createHash('sha256').update(s).digest('hex');
export function createAccounts(path){
 const db=new DatabaseSync(path);
 db.exec(`PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT UNIQUE,salt TEXT,hash TEXT); CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user TEXT,expires INTEGER); CREATE TABLE IF NOT EXISTS reports(id TEXT,user TEXT,created TEXT,payload TEXT,PRIMARY KEY(user,id));`);
 const attempts=new Map();
 const cookie=(token,age)=>`zhixing_session=${token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${age}`;
 function user(req){const token=(req.headers.cookie||'').split(';').map(v=>v.trim()).find(v=>v.startsWith('zhixing_session='))?.slice(16);return token?db.prepare('SELECT users.id,users.name FROM sessions JOIN users ON users.id=sessions.user WHERE token=? AND expires>?').get(digest(token),Date.now()):null;}
 async function handle(req,res){
  if(!req.url.startsWith('/api/account')&&!req.url.startsWith('/api/history'))return false;
  const send=(code,obj,headers={})=>{res.writeHead(code,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',...headers});res.end(JSON.stringify(obj));return true};
  if(req.method!=='GET'&&req.headers.origin&&req.headers.origin!==`http://${req.headers.host}`&&req.headers.origin!==`https://${req.headers.host}`)return send(403,{error:'请求来源不匹配'});
  let body={};
  if(req.method==='POST'){
   if(!req.headers['content-type']?.startsWith('application/json'))return send(415,{error:'请使用 JSON 请求'});
   const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>16384)return send(413,{error:'内容过长'});chunks.push(chunk)}
   try{body=JSON.parse(Buffer.concat(chunks).toString('utf8'));if(!body||typeof body!=='object')throw Error()}catch{return send(400,{error:'请求格式错误'})}
  }
  if(req.method==='POST'&&['/api/account/register','/api/account/login'].includes(req.url)){
   const key=req.socket.remoteAddress;const now=Date.now();let bucket=attempts.get(key);if(!bucket||now>bucket.until){bucket={count:0,until:now+900000};attempts.set(key,bucket)}if(++bucket.count>20)return send(429,{error:'尝试过于频繁，请15分钟后重试'});
   const {name,password}=body;if(typeof name!=='string'||! /^[\p{L}\p{N}_-]{2,24}$/u.test(name)||typeof password!=='string'||password.length<8||password.length>128)return send(400,{error:'用户名需2—24位中文、字母、数字或下划线；密码需8—128位'});
   let u=db.prepare('SELECT * FROM users WHERE name=?').get(name);
   if(req.url.endsWith('/register')){
    if(u)return send(409,{error:'用户名已被使用'});
    const salt=randomBytes(16).toString('hex');const hash=(await scrypt(password,salt,64)).toString('hex');
    u={id:randomUUID(),name};try{db.prepare('INSERT INTO users VALUES(?,?,?,?)').run(u.id,name,salt,hash)}catch{return send(409,{error:'用户名已被使用'})}
   }else{
    const hash=await scrypt(password,u?.salt||'unknown-user-salt',64);
    if(!u||!timingSafeEqual(hash,Buffer.from(u.hash,'hex')))return send(401,{error:'用户名或密码不正确'});
   }
   const token=randomBytes(32).toString('hex');db.prepare('DELETE FROM sessions WHERE expires<?').run(now);db.prepare('INSERT INTO sessions VALUES(?,?,?)').run(digest(token),u.id,now+604800000);
   return send(200,{user:{name:u.name}}, {'Set-Cookie':cookie(token,604800)});
  }
  const u=user(req);
  if(req.url==='/api/account/me'&&req.method==='GET')return send(200,{user:u?{name:u.name}:null});
  if(!u)return send(401,{error:'请先登录'});
  if(req.url==='/api/account/logout'&&req.method==='POST'){
   const token=(req.headers.cookie||'').match(/zhixing_session=([^;]+)/)?.[1];if(token)db.prepare('DELETE FROM sessions WHERE token=?').run(digest(token));return send(200,{ok:true},{'Set-Cookie':cookie('',0)});
  }
  if(req.url==='/api/history'&&req.method==='GET')return send(200,{records:db.prepare('SELECT id,created,payload FROM reports WHERE user=? ORDER BY created,id').all(u.id).map(r=>({id:r.id,created:r.created,...JSON.parse(r.payload)}))});
  if(req.url==='/api/history'&&req.method==='POST'){
   try{
    const payload=scoreReport(body.report);if(typeof body.id!=='string'||! /^[a-f0-9-]{36}$/.test(body.id))throw Error();
    db.prepare('INSERT OR IGNORE INTO reports VALUES(?,?,?,?)').run(body.id,u.id,new Date().toISOString(),JSON.stringify(payload));return send(200,{ok:true});
   }catch{return send(400,{error:'评估数据不完整或超出范围，请重新生成报告'})}
  }
  return send(404,{error:'接口不存在'});
 }
 return {handle,close:()=>db.close()};
}
export function scoreReport(report){
 const ranges={grade:100,previous:100,attendance:100,study:12,sleep:16,practice:100};
 if(!report||!Array.isArray(report.selected)||!report.selected.length||new Set(report.selected).size!==report.selected.length||report.selected.some(k=>!Object.hasOwn(ranges,k)||k==='previous'))throw Error();
 const data={};for(const [k,max] of Object.entries(ranges)){const v=report.data?.[k];if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>max)throw Error();data[k]=v;}
 const {mode,alpha}=report;if(!['equal','variable'].includes(mode)||typeof alpha!=='number'||!Number.isFinite(alpha)||alpha<0||alpha>5)throw Error();
 const selected=[...report.selected].sort(),z={grade:data.grade/100,attendance:data.attendance/100,study:Math.min(data.study/4,1),sleep:Math.max(0,1-Math.abs(data.sleep-8)/8),practice:Math.min(data.practice/5,1)};
 const raw=selected.map(k=>mode==='equal'?1:({grade:0.45-0.20*(data.grade/100),attendance:(0.40-0.15*(data.grade/100))/2,study:(0.40-0.15*(data.grade/100))/2,sleep:0.15+0.35*(data.grade/100),practice:0.15}[k])**(alpha/5)),sum=raw.reduce((a,b)=>a+b,0),attentionWeights=raw.map(v=>v/sum),weights=selected.map(()=>1/selected.length),score=selected.reduce((s,k,i)=>s+100*z[k]*weights[i],0);
 return {data,selected,mode,alpha,weights,attentionWeights,score,formulaVersion:'v3',group:JSON.stringify([selected,'equal','v3'])};
}
