import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {createModelAdapter,recommendationFormat} from './model-adapter.mjs';
import {createAccounts} from './accounts.mjs';
import {mkdirSync} from 'node:fs';
mkdirSync(new URL('./private/',import.meta.url),{recursive:true});
const accounts=createAccounts(fileURLToPath(new URL('./private/accounts.sqlite',import.meta.url)));
const root=new URL('../',import.meta.url);
const model=createModelAdapter({baseUrl:process.env.MODEL_BASE_URL||'http://127.0.0.1:11434/v1',model:process.env.MODEL_NAME||'qwen3:4b',apiKey:process.env.MODEL_API_KEY,requestOptions:process.env.MODEL_BASE_URL?{}:{reasoning_effort:"none",response_format:recommendationFormat}});
const assets=new Set(['index.html','style.css','app.js','enhance.js','intent.js','rewards.js','account.js']);
const types={html:'text/html; charset=utf-8',css:'text/css',js:'text/javascript; charset=utf-8'};
const server=http.createServer(async(req,res)=>{
  const reply=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(data));};
  try{
    if(await accounts.handle(req,res))return;
    if(req.method==='POST'&&req.url==='/api/recommend'){
      const origin=req.headers.origin;if(origin&&origin!==`http://${req.headers.host}`&&origin!==`https://${req.headers.host}`)return reply(403,{error:'ORIGIN_REJECTED'});
      let text='';for await(const chunk of req){text+=chunk;if(Buffer.byteLength(text)>4096)return reply(413,{error:'INPUT_TOO_LARGE'});}
      let body;try{body=JSON.parse(text);}catch{return reply(400,{error:'INVALID_JSON'});}
      if(typeof body.text!=='string'||!body.text.trim()||body.text.length>500)return reply(400,{error:'INVALID_INPUT'});
      try{return reply(200,await model.recommend(body.text));}catch{return reply(503,{error:'MODEL_UNAVAILABLE',message:'模型暂不可用，请确认本地千问已启动。'});}
    }
    if(req.method!=='GET')return reply(405,{error:'METHOD_NOT_ALLOWED'});
    const name=new URL(req.url,'http://localhost').pathname.slice(1)||'index.html';
    if(!assets.has(name))return reply(404,{error:'NOT_FOUND'});
    const content=await readFile(new URL(name,root));res.writeHead(200,{'Content-Type':types[name.split('.').pop()],'X-Content-Type-Options':'nosniff'});res.end(content);
  }catch{if(!res.headersSent)reply(500,{error:'SERVER_ERROR'});else res.end();}
});
server.listen(8787,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:8787'));


