import test from 'node:test';
import assert from 'node:assert/strict';
import {createModelAdapter,validateRecommendation} from './model-adapter.mjs';
test('clarification prevents speculative indicators being applied',()=>assert.deepEqual(validateRecommendation({indicators:[{id:'grade',reason:'猜测'}],question:'想评估什么？'}).indicators,[]));
test('rejects invented indicators, duplicates and missing clarification',()=>{
  for(const indicators of [[{id:'IQ',reason:'x'}],[{id:'grade',reason:'x'},{id:'grade',reason:'y'}]]) assert.throws(()=>validateRecommendation({indicators,question:''}));
  assert.throws(()=>validateRecommendation({indicators:[],question:''}));
});
test('compatible endpoint request returns only validated recommendation',async()=>{
  const adapter=createModelAdapter({baseUrl:'http://localhost:8000/v1',model:'configured-qwen-model',fetchImpl:async(url,options)=>{
    assert.equal(url,'http://localhost:8000/v1/chat/completions');assert.equal(JSON.parse(options.body).messages[1].content,'想了解成绩');
    return {ok:true,json:async()=>({choices:[{message:{content:JSON.stringify({indicators:[{id:'grade',reason:'关注成绩'}],question:''})}}]})};
  }});
  assert.equal((await adapter.recommend('想了解成绩')).source,'model');
});
test('unconfigured model is explicit and invalid JSON fails closed',async()=>{
  await assert.rejects(createModelAdapter({}).recommend('成绩'),/NOT_CONFIGURED/);
  await assert.rejects(createModelAdapter({baseUrl:'https://example.com/v1',model:'test',fetchImpl:async()=>({ok:true,json:async()=>({choices:[{message:{content:'not json'}}]})})}).recommend('成绩'),/INVALID_JSON/);
});
