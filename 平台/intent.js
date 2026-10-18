const intentBox=document.createElement('section');intentBox.id='intent-section';
intentBox.innerHTML=`<span class="eyebrow">01 / 认识自己</span><h2>先画一张你的学习画像</h2><p class="muted">用一分钟选择你的目标和节奏。没有标准答案，你可以随时调整。</p><div class="grid"><label>最近的学习状态<select id="portrait-state"><option>成绩有起伏，想找到原因</option><option>整体稳定，想进一步提升</option><option>刚开始调整，想从小事做起</option></select></label><label>最常遇到的困难<select id="portrait-barrier"><option>不知道从哪里开始</option><option>计划太大，很难坚持</option><option>时间安排不稳定</option><option>投入不少，看不到变化</option></select></label><label>每天愿意尝试的时间<select id="portrait-time"><option value="5">5分钟，先开始</option value="15">15分钟，稳步推进</option><option value="25">25分钟，专注挑战</option></select></label></div><h3>这次，你想了解哪些方面？</h3><div id="portrait-goals" class="grid"><label><input type="checkbox" value="study"> 学业表现与学习投入</label><label><input type="checkbox" value="habit"> 学习节奏与休息</label><label><input type="checkbox" value="practice"> 课外实践与全面发展</label></div><label for="intent-text">还有什么想补充的？（选填）</label><textarea id="intent-text" maxlength="200" rows="2" placeholder="例如：我怀疑睡眠影响了成绩，希望同时看看学习投入"></textarea><button id="intent-match" class="primary">生成我的评估方案</button><p id="intent-status" role="status"></p><div id="portrait-summary"></div><div id="intent-result"></div><button id="intent-confirm" hidden>确认方案，继续填写数据 →</button>`;
document.querySelector('#data-section').before(intentBox);
const domainSets={study:['grade','attendance','study'],habit:['study','sleep','attendance'],practice:['grade','practice']};
let portraitVersion=0;
// Keep explicit rest concerns even when the model is unavailable or omits them.
function explicitRestPreference(note){
 const clauses=note.split(/[，。；！？,;!?\n]+/).map(s=>s.trim()).filter(Boolean);
 let result=null;
 for(const clause of clauses){
  if(!/睡眠|睡觉|失眠|熬夜|晚睡|早醒|入睡|作息/.test(clause))continue;
  result=/(?:不想|不需要|不用|不要|无需|不关注|不考虑|不评估|不评价|排除|忽略).{0,8}(?:睡眠|睡觉|失眠|熬夜|晚睡|早醒|入睡|作息)/.test(clause)?'exclude':'include';
 }
 return result;
}
function portrait(){return {state:$('portrait-state').value,barrier:$('portrait-barrier').value,minutes:Number($('portrait-time').value),domains:[...document.querySelectorAll('#portrait-goals input:checked')].map(c=>c.value),note:$('intent-text').value.trim()};}
intentBox.querySelectorAll('input,select,textarea').forEach(el=>el.addEventListener('input',()=>{portraitVersion++;$('report').hidden=true;lastReport=null;window.currentPortrait=null;$('intent-confirm').hidden=true;$('intent-result').replaceChildren();$('portrait-summary').replaceChildren();$('intent-status').textContent='画像已更新，请重新生成方案。';}));
$('intent-match').onclick=async()=>{
 const p=portrait();if(!p.domains.length&&!p.note){$('intent-status').textContent='请选择一个方向，或在补充文字中说明你想了解的问题。';return;}
 const version=++portraitVersion;const button=$('intent-match');button.disabled=true;$('intent-result').replaceChildren();$('intent-confirm').hidden=true;
 const restPreference=explicitRestPreference(p.note);const base=[...new Set(p.domains.flatMap(d=>domainSets[d]))];const reasons=new Map(base.map(id=>[id,'你选择的评估方向包含这一基础指标；可以在下面取消。']));
 if(restPreference==='include')reasons.set('sleep','你在补充描述中提到了睡眠或作息问题，因此加入睡眠时长。睡眠质量暂不能仅凭时长判断。');
 if(restPreference==='exclude')reasons.delete('sleep');
 $('intent-status').textContent='正在结合你的画像整理方案…';let assisted=false;
 try{const response=await fetch('/api/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:`用户画像：${p.state}；困难：${p.barrier}；每天可投入${p.minutes}分钟。用户明确选择的基础指标：${base.join('、')}。请为这些指标说明评估理由，可根据补充需求建议其他目录内指标。补充：${p.note||'无'}。`}),signal:AbortSignal.timeout(65000)});if(!response.ok)throw Error();const data=await response.json();if(!Array.isArray(data.indicators))throw Error();for(const item of data.indicators){if(fields.some(f=>f[0]===item.id&&f[0]!=='previous')&&typeof item.reason==='string')reasons.set(item.id,item.reason);}assisted=true;}catch{}
 if(restPreference==='include')reasons.set('sleep','对应你的补充诉求：睡眠或作息。后续报告会展示睡眠时长与相关建议；时长不能代替睡眠质量。');
 if(restPreference==='exclude')reasons.delete('sleep');
 if(version!==portraitVersion){button.disabled=false;return;}
 $('portrait-summary').textContent=`你的画像：${p.state} · ${p.barrier} · 每天从${p.minutes}分钟开始。${p.note?' 你补充的问题：'+p.note:''}`;
 for(const [id,reason] of reasons){const label=document.createElement('label'),input=document.createElement('input'),small=document.createElement('small');input.type='checkbox';input.checked=true;input.dataset.indicator=id;small.textContent=reason;label.append(input,document.createTextNode(' '+fields.find(f=>f[0]===id)[1]),document.createElement('br'),small);$('intent-result').append(label);}
 $('intent-status').textContent=assisted?'已结合你的方向和补充描述生成方案。请确认哪些指标适合你。':'智能分析暂不可用，已保留所选方向和可识别的睡眠诉求；其他补充内容请核对下方指标。';$('intent-confirm').hidden=false;button.disabled=false;
};
$('intent-confirm').onclick=()=>{const ids=[...intentBox.querySelectorAll('[data-indicator]:checked')].map(el=>el.dataset.indicator);if(!ids.length){$('intent-status').textContent='请至少保留一项指标。';return;}document.querySelectorAll('#choices input').forEach(c=>c.checked=ids.includes(c.value));$('report').hidden=true;lastReport=null;refreshExtras();window.currentPortrait={...portrait(),selected:ids};window.dispatchEvent(new Event('portrait-confirmed'));$('intent-status').textContent='方案已确认。请在下方填写真实数据，示例值可以修改。';$('data-section').scrollIntoView({behavior:'smooth'});};
