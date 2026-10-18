import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createAccounts} from './accounts.mjs';
test('accounts isolate records, recompute scores, deduplicate and survive restart',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'zhixing-test-'));let api=createAccounts(join(dir,'test.sqlite'));
 const server=http.createServer((req,res)=>api.handle(req,res));await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const url=`http://127.0.0.1:${server.address().port}`;
 async function request(path,body,cookie,extra={}){const r=await fetch(url+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',...(cookie?{cookie}:{}),...extra},body:body===undefined?undefined:JSON.stringify(body)});return {status:r.status,body:await r.json(),cookie:r.headers.get('set-cookie')?.split(';')[0]}}
 try{
  assert.equal((await request('/api/history')).status,401);
  const a=await request('/api/account/register',{name:'测试甲',password:'test-password-123'});assert.equal(a.status,200);assert.ok(a.cookie);
  assert.equal((await request('/api/account/me',undefined,a.cookie)).body.user.name,'测试甲');
  assert.equal((await request('/api/account/login',{name:'测试甲',password:'wrong-password'})).status,401);
  const b=await request('/api/account/register',{name:'测试乙',password:'test-password-456'});
  const body={id:'00000000-0000-4000-8000-000000000001',report:{selected:['grade','sleep'],data:{grade:80,previous:70,attendance:95,study:2,sleep:8,practice:3},mode:'equal',alpha:1,score:999}};
  assert.equal((await request('/api/history',body,a.cookie)).status,200);
  assert.equal((await request('/api/history',body,a.cookie)).status,200);
  let records=(await request('/api/history',undefined,a.cookie)).body.records;assert.equal(records.length,1);assert.equal(records[0].score,90);
  assert.equal((await request('/api/history',undefined,b.cookie)).body.records.length,0);
  assert.equal((await request('/api/history',body,a.cookie,{origin:'https://untrusted.example'})).status,403);
  assert.equal((await request('/api/history',{...body,report:{...body.report,data:{...body.report.data,sleep:-1}}},a.cookie)).status,400);
  api.close();api=createAccounts(join(dir,'test.sqlite'));records=(await request('/api/history',undefined,a.cookie)).body.records;assert.equal(records.length,1);
  await request('/api/account/logout',{},a.cookie);assert.equal((await request('/api/history',undefined,a.cookie)).status,401);
 }finally{await new Promise(resolve=>server.close(resolve));api.close();rmSync(dir,{recursive:true,force:true})}
});
