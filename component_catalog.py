"""Shared local HTML component demonstrations, generated for every theme mode."""
from html import escape

CONTRACT = {
    'kind': 'browser-local-demonstration',
    'controls': ['switch', 'checkbox', 'radio', 'segmented', 'range', 'stepper', 'search', 'required-input', 'load-state', 'confirmation', 'menu', 'selection-sheet', 'progress', 'notification'],
    'native_implementation': 'pending',
}

CSS = r'''
.cc-section{background:var(--bg);color:var(--ink);padding:16px;border-radius:var(--r-card);font-size:calc(var(--type-body,17px) * var(--dt-scale,1))}.cc-section p{color:var(--ink)}
.cc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px;margin:20px 0}
.cc-card{background:var(--surface);color:var(--ink);border:1px solid var(--line-strong);border-radius:var(--r-card);padding:18px;min-width:0;line-height:1.5}
.cc-section h3{font-size:calc(22px * var(--dt-scale,1))}.cc-card h4{margin:0 0 10px;font-size:calc(20px * var(--dt-scale,1))}.cc-card p{overflow-wrap:anywhere}.cc-card label{display:block;margin:10px 0}.cc-card label.cc-choice,.cc-dialog label.cc-choice{display:flex;align-items:center;gap:8px;min-height:44px;padding:8px 0;white-space:normal}
.cc-card input[type=text],.cc-card input[type=search]{box-sizing:border-box;max-width:100%;width:100%;min-height:44px;padding:8px;border:1px solid var(--control-border);border-radius:var(--r-in);background:var(--bg);color:var(--ink);font:inherit}
.cc-card input[type=checkbox],.cc-card input[type=radio]{width:22px;height:22px;accent-color:var(--accent-ui);vertical-align:middle}
.cc-card input[type=range]{width:100%;accent-color:var(--accent-ui)}.cc-card button,.cc-dialog button{min-height:44px;min-width:44px;border:1px solid var(--control-border);border-radius:var(--r-btn);background:var(--surface);color:var(--ink);padding:8px 16px;font:inherit;cursor:pointer}
.cc-card button:disabled,.cc-dialog button:disabled{opacity:.5;cursor:not-allowed}.cc-card button.cc-primary,.cc-dialog button.cc-primary{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}
.cc-card button.cc-danger,.cc-dialog button.cc-danger{background:var(--danger);color:var(--on-danger);border-color:var(--danger)}
.cc-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0}.cc-row label{margin:0}.cc-fieldset{border:1px solid var(--line-strong);border-radius:var(--r-in);padding:10px;margin:10px 0}.cc-fieldset legend{padding:0 5px}
.cc-card [aria-invalid=true]{border-color:var(--danger-text)!important}.cc-error{color:var(--danger-text)}.cc-status{min-height:24px;font-weight:600}.cc-skeleton{height:18px;border-radius:8px;background:var(--fill-strong);animation:cc-pulse 1s ease-in-out infinite alternate}
.cc-card progress{width:100%;height:16px;accent-color:var(--accent-ui)}.cc-dialog{max-width:min(90vw,480px);max-height:90vh;overflow:auto;border:1px solid var(--control-border);border-radius:18px;background:var(--surface);color:var(--ink);padding:24px;box-shadow:0 12px 40px #0005;font-size:calc(var(--type-body,17px) * var(--dt-scale,1))}
.cc-dialog::backdrop{background:#0009}.cc-dialog h4{margin-top:0}.cc-dialog menu{display:flex;flex-wrap:wrap;gap:8px;padding:0;margin-bottom:0}.cc-dialog label{display:block;padding:8px 0}
.cc-card :focus-visible,.cc-dialog :focus-visible{outline:3px solid var(--accent-ui);outline-offset:3px}
@keyframes cc-pulse{from{opacity:.45}to{opacity:1}}@media(prefers-reduced-motion:reduce){.cc-skeleton{animation:none}}
'''

SCRIPT = r'''
document.querySelectorAll('[data-cc-demo]').forEach(root=>{
  const one=(s)=>root.querySelector(s);
  const status=one('[data-cc-status]');
  const say=(value)=>{status.textContent=value;};
  one('[data-cc-switch]').addEventListener('change',e=>say('通知：'+(e.target.checked?'开启':'关闭')));
  one('[data-cc-check]').addEventListener('change',e=>say('已选：'+(e.target.checked?'是':'否')));
  root.querySelectorAll('[data-cc-radio]').forEach(el=>el.addEventListener('change',()=>say('模式：'+el.value)));
  root.querySelectorAll('[data-cc-segment]').forEach(el=>el.addEventListener('change',()=>say('视图：'+el.value)));
  const range=one('[data-cc-range]'),rangeValue=one('[data-cc-range-value]');
  range.addEventListener('input',()=>{rangeValue.textContent=range.value+'%';});
  const step=one('[data-cc-step]'),down=one('[data-cc-down]'),up=one('[data-cc-up]');
  const setStep=(n)=>{let v=Math.max(0,Math.min(5,n));step.textContent=String(v);down.disabled=v===0;up.disabled=v===5;};
  down.addEventListener('click',()=>setStep(Number(step.textContent)-1));up.addEventListener('click',()=>setStep(Number(step.textContent)+1));setStep(2);
  const search=one('[data-cc-search]'),clear=one('[data-cc-clear]'),searchResult=one('[data-cc-search-result]');
  const updateSearch=()=>{let q=search.value.trim();searchResult.textContent=q ? (['日程','天气','提醒'].filter(x=>x.includes(q)).join('、')||'无匹配项目') : '输入关键词后筛选本地演示数据';clear.disabled=!search.value;};
  search.addEventListener('input',updateSearch);clear.addEventListener('click',()=>{search.value='';updateSearch();search.focus();});updateSearch();
  const required=one('[data-cc-required]'),error=one('[data-cc-error]');
  one('[data-cc-validate]').addEventListener('click',()=>{let valid=!!required.value.trim();required.setAttribute('aria-invalid',String(!valid));error.textContent=valid?'✓ 已填写':'请输入名称后重试';say(valid?'输入已验证':'输入有误');if(!valid)required.focus();});
  const load=one('[data-cc-load]'),loadResult=one('[data-cc-load-result]');let loading=false;
  root.querySelectorAll('[data-cc-load-mode]').forEach(button=>button.addEventListener('click',()=>{if(loading)return;loading=true;load.disabled=true;loadResult.textContent='正在加载…';loadResult.classList.add('cc-skeleton');const mode=button.dataset.ccLoadMode;setTimeout(()=>{loadResult.classList.remove('cc-skeleton');loadResult.textContent=mode==='success'?'成功：3 条本地演示数据':mode==='empty'?'空：没有匹配记录':'失败：演示请求失败，可重试';load.disabled=false;loading=false;},250); }));
  load.addEventListener('click',()=>{one('[data-cc-load-mode=success]').click();});
  const confirm=one('[data-cc-confirm]'),menu=one('[data-cc-menu]'),sheet=one('[data-cc-sheet]');let opener=null,confirmed=0;
  const open=(dialog,button)=>{opener=button;dialog.showModal();dialog.querySelector('button,[type=radio]')?.focus();};
  const close=(dialog)=>{dialog.close();opener?.focus();opener=null;};
  [confirm,menu,sheet].forEach(dialog=>{dialog.addEventListener('cancel',e=>{e.preventDefault();close(dialog);});dialog.addEventListener('close',()=>{opener?.focus();opener=null;});});
  one('[data-cc-open-confirm]').addEventListener('click',e=>open(confirm,e.currentTarget));
  one('[data-cc-confirm-cancel]').addEventListener('click',()=>close(confirm));
  one('[data-cc-confirm-ok]').addEventListener('click',()=>{confirmed++;say('已执行危险操作 '+confirmed+' 次');close(confirm);});
  one('[data-cc-open-menu]').addEventListener('click',e=>open(menu,e.currentTarget));
  one('[data-cc-menu-cancel]').addEventListener('click',()=>close(menu));
  menu.querySelectorAll('[data-cc-action]').forEach(b=>b.addEventListener('click',()=>{say('已选择：'+b.dataset.ccAction);close(menu);}));
  let saved='上午';const chosen=one('[data-cc-chosen]');
  one('[data-cc-open-sheet]').addEventListener('click',e=>{sheet.querySelectorAll('[data-cc-option]').forEach(r=>r.checked=r.value===saved);open(sheet,e.currentTarget);});
  one('[data-cc-sheet-cancel]').addEventListener('click',()=>close(sheet));
  one('[data-cc-sheet-ok]').addEventListener('click',()=>{saved=sheet.querySelector('[data-cc-option]:checked').value;chosen.textContent=saved;say('已保存时段：'+saved);close(sheet);});
});
'''

def samples(mode):
    label=escape(mode)
    mode_class=' dark' if mode=='dark' else ''
    return f'''<section class="notes cc-section{mode_class}" id="components-{label}"><h3>可操作组件 · {label}</h3><p>本页只改变浏览器内的演示状态。禁用项无法写入；加载使用固定本地数据。原生组件实现仍待 iOS 工程。</p>
<div data-cc-demo class="cc-grid">
<div class="cc-card"><h4>选择与数值</h4><label class="cc-choice"><input data-cc-switch type="checkbox" role="switch"> 通知开关</label><label class="cc-choice"><input data-cc-check type="checkbox"> 同步日历</label><label class="cc-choice"><input type="checkbox" disabled> 禁用选项</label><fieldset class="cc-fieldset"><legend>通知频率</legend><label class="cc-choice"><input data-cc-radio type="radio" name="frequency-{label}" value="每天" checked> 每天</label><label class="cc-choice"><input data-cc-radio type="radio" name="frequency-{label}" value="每周"> 每周</label></fieldset><fieldset class="cc-fieldset"><legend>视图</legend><label class="cc-choice"><input data-cc-segment type="radio" name="view-{label}" value="列表" checked> 列表</label><label class="cc-choice"><input data-cc-segment type="radio" name="view-{label}" value="日历"> 日历</label></fieldset><label>亮度 <output data-cc-range-value>50%</output><input data-cc-range type="range" min="0" max="100" value="50"></label><div class="cc-row"><span>数量</span><button type="button" data-cc-down aria-label="数量减一">−</button><output data-cc-step>2</output><button type="button" data-cc-up aria-label="数量加一">＋</button></div></div>
<div class="cc-card"><h4>输入与结果</h4><label>搜索演示数据<input data-cc-search type="search" autocomplete="off"></label><button type="button" data-cc-clear>清除</button><p data-cc-search-result aria-live="polite"></p><label>名称 <span aria-hidden="true">*</span><input data-cc-required type="text" required aria-describedby="error-{label}"></label><p class="cc-error" id="error-{label}" data-cc-error aria-live="polite"></p><button type="button" data-cc-validate>验证名称</button><p><label>禁用输入<input type="text" value="不可修改" disabled></label></p><div class="cc-row"><button type="button" data-cc-load>加载</button><button type="button" data-cc-load-mode="success">成功</button><button type="button" data-cc-load-mode="empty">空数据</button><button type="button" data-cc-load-mode="error">失败／重试</button></div><p data-cc-load-result aria-live="polite">选择本地演示状态</p></div>
<div class="cc-card"><h4>动作与反馈</h4><div class="cc-row"><button type="button" data-cc-open-confirm class="cc-danger">删除项目…</button><button type="button" data-cc-open-menu>更多操作</button><button type="button" data-cc-open-sheet>选择时段</button></div><p>已选时段：<strong data-cc-chosen>上午</strong></p><p class="cc-status" data-cc-status role="status" aria-live="polite">等待操作</p><label>进度示意 <progress max="100" value="60">60%</progress> 60%</label><p>加载占位与活动状态有文字说明。</p><div class="cc-skeleton" aria-hidden="true"></div><p>🔒 无权限：请联系管理员取得访问权限。</p><p>✓ 操作通知包含明确文字。</p></div>
<dialog class="cc-dialog" data-cc-confirm aria-labelledby="confirm-title-{label}"><h4 id="confirm-title-{label}">删除演示项目？</h4><p>此操作会更新本页演示计数。</p><menu><button type="button" data-cc-confirm-cancel>取消</button><button type="button" class="cc-danger" data-cc-confirm-ok>确认删除</button></menu></dialog>
<dialog class="cc-dialog" data-cc-menu aria-label="更多操作"><h4>更多操作</h4><button type="button" data-cc-action="分享">分享</button><button type="button" data-cc-action="复制">复制</button><button type="button" data-cc-menu-cancel>取消</button></dialog>
<dialog class="cc-dialog" data-cc-sheet aria-label="选择时段"><h4>选择时段</h4><label class="cc-choice"><input data-cc-option type="radio" name="time-{label}" value="上午"> 上午</label><label class="cc-choice"><input data-cc-option type="radio" name="time-{label}" value="下午"> 下午</label><menu><button type="button" data-cc-sheet-cancel>取消</button><button type="button" class="cc-primary" data-cc-sheet-ok>保存</button></menu></dialog>
</div><noscript>这些交互演示需要 JavaScript；当前只能查看静态规范。</noscript></section>'''
