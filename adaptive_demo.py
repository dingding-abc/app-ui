"""Adjustable HTML container demo; no device dimensions or posture APIs are implied."""
import json
from html import escape
from site_support import prepare_page

SCENARIOS = (
    ('outer', '外屏紧凑', 360, 700),
    ('inner', '内屏展开', 780, 700),
    ('fold', '部分折叠避让', 680, 560),
    ('split', '分屏窄窗', 330, 580),
    ('short', '低高度 / PiP', 600, 320),
    ('landscape', '横向宽窗', 860, 430),
)

def page():
    choices=''.join(f'<option value="{i}">{escape(name)}（演示 {w} × {h}）</option>'
                    for i,(_,name,w,h) in enumerate(SCENARIOS))
    presets=json.dumps([dict(id=key,width=w,height=h) for key,_,w,h in SCENARIOS],ensure_ascii=False)
    html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>自适应场景 · HTML 容器演示</title><style>
*{box-sizing:border-box}body{margin:0;background:#F1EEE8;color:#2A2723;font-family:system-ui,sans-serif}.board{max-width:1300px;margin:auto;padding:32px 20px}h1{line-height:1.4}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:end;padding:16px;background:#fff;border:1px solid #ccc;border-radius:14px}.control{display:grid;gap:4px;font-size:14px}.control select,.control input{min-height:44px;font:inherit;padding:7px;border:1px solid #777;border-radius:8px}.control input[type=number]{width:90px}
button{min-height:44px;min-width:44px;font:inherit;padding:8px 14px;border:1px solid #777;border-radius:99px;background:white;cursor:pointer}button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #24689c;outline-offset:2px}
.demo-scroll{overflow:auto;max-width:100%;padding:18px 0}.demo-frame{width:360px;height:700px;max-width:none;container-type:inline-size;border:3px solid #343434;border-radius:20px;background:#fff;position:relative;overflow:auto;resize:both;min-width:280px;min-height:240px;--safe-left:0px;--safe-right:0px;--safe-top:18px;--safe-bottom:18px;--hinge:0px}
.demo-inner{min-height:100%;padding:var(--safe-top) max(16px,var(--safe-right)) var(--safe-bottom) max(16px,var(--safe-left));display:grid;grid-template-columns:minmax(0,1fr);gap:16px;align-content:start}.list,.detail{min-width:0;background:#f5f7f8;border:1px solid #ccd3d9;border-radius:14px;padding:12px}.list button{display:block;width:100%;text-align:left;margin:6px 0;overflow-wrap:anywhere}.list button[aria-current=true]{border:2px solid #24689c;font-weight:bold}.detail label{display:grid;gap:6px}.detail textarea{width:100%;min-height:80px;resize:vertical;font:inherit;padding:8px}.detail p{overflow-wrap:anywhere}
.action{position:sticky;bottom:0;background:#f5f7f8;padding:8px 0;z-index:1;display:flex;gap:8px;flex-wrap:wrap;justify-content:center}.demo-frame[data-align=left] .action{justify-content:flex-start}.demo-frame[data-align=right] .action{justify-content:flex-end}.action button{background:#24689c;color:white;border-color:#24689c}.status{font-weight:bold}
.demo-frame{--fold-pad-left:16px;--fold-pad-right:16px;--fold-left:0px;--fold-right:0px;--fold-gap:16px;--fold-single-left:16px;--fold-single-right:16px}
@container (min-width:620px){.demo-inner{grid-template-columns:minmax(180px,35%) minmax(0,1fr)}.list{grid-column:1}.detail{grid-column:2}.demo-inner>h2,.demo-inner>.status{grid-column:1/-1}}
.demo-frame.fold:after{content:"";position:absolute;left:50%;top:0;bottom:0;width:max(2px,var(--hinge));transform:translateX(-50%);pointer-events:none;background:repeating-linear-gradient(0deg,#5559 0 8px,transparent 8px 16px)}
.demo-frame.fold .demo-inner{padding-left:var(--fold-pad-left);padding-right:var(--fold-pad-right);grid-template-columns:minmax(0,var(--fold-left)) var(--fold-gap) minmax(0,var(--fold-right));column-gap:0;row-gap:16px}.demo-frame.fold .demo-inner>h2{grid-column:1;grid-row:1}.demo-frame.fold .list{grid-column:1;grid-row:2/span 2}.demo-frame.fold .detail{grid-column:3;grid-row:1/span 2}.demo-frame.fold .status{grid-column:3;grid-row:3}
.demo-frame.fold.fold-single .demo-inner{grid-template-columns:minmax(0,1fr);padding-left:var(--fold-single-left);padding-right:var(--fold-single-right);gap:16px}.demo-frame.fold.fold-single .demo-inner>*{grid-column:1;grid-row:auto}.demo-frame.fold-unavailable .demo-inner{display:none}.demo-frame.fold-unavailable:before{content:"当前安全区与折线组合无法容纳 44px 操作；请增大演示宽度或减小安全区。";display:block;position:relative;z-index:1;max-width:240px;margin:24px auto;padding:12px;background:#fff;color:#222;border:1px solid #777;border-radius:10px}
@media(max-width:700px){.controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.control{min-width:0}}
</style></head><body><div class="board"><h1>自适应场景 · 同一任务跨容器</h1>
<p>宽高是可调的 HTML 演示尺寸，不是 iPhone Duo 官方尺寸或 SDK 姿态识别。布局按容器宽度变化；安全区与折线用于压力测试，操作按钮对齐只改变按钮位置。原生版需从系统读取 size class、安全区与真实姿态。</p>
<div class="controls">
<div class="control"><label for="scenario">场景</label><select id="scenario">__OPTIONS__</select></div>
<div class="control"><label for="width">演示宽度 px</label><input id="width" type="number" min="280" max="1200" value="360"></div>
<div class="control"><label for="height">演示高度 px</label><input id="height" type="number" min="240" max="1000" value="700"></div>
<div class="control"><label for="safe-left">左安全区 px</label><input id="safe-left" type="number" min="0" max="120" value="0"></div>
<div class="control"><label for="safe-right">右安全区 px</label><input id="safe-right" type="number" min="0" max="120" value="0"></div>
<div class="control"><label for="control-align">操作按钮对齐</label><select id="control-align"><option value="center">居中</option><option value="left">靠左</option><option value="right">靠右</option></select></div>
<div class="control"><label for="hinge">折线示意宽度 px</label><input id="hinge" type="number" min="0" max="80" value="20"></div>
</div><p id="layout-note" role="status" aria-live="polite">常规容器示意。</p>
<p>窗口可拖动右下角；切换场景后，所选项目、草稿与已确认值继续保留。主操作位于内容滚动区内。</p>
<div class="demo-scroll"><div class="demo-frame" id="frame"><div class="demo-inner"><h2>行程安排</h2><div class="list" aria-label="项目列表"><button type="button" data-item="a" aria-current="true">上午 · 日程安排</button><button type="button" data-item="b">下午 · 长标题示例 Example of a long itinerary item</button><button type="button" data-item="c">晚上 · 复盘</button></div><div class="detail"><h3 id="item-title">上午 · 日程安排</h3><label for="draft">草稿</label><textarea id="draft">准备出发</textarea><p>已确认：<span id="saved">准备出发</span></p><div class="action"><button id="save" type="button">确认当前草稿</button></div></div><p class="status" role="status" id="status">当前项目：上午</p></div></div></div>
<p>官方参考：<a href="https://developer.apple.com/iphone-duo/">iPhone Duo 入口</a> · <a href="https://developer.apple.com/videos/play/tech-talks/111466/">Design for iPhone Duo</a>。HTML 无法证明原生 size class、折叠姿态和系统组件避让行为。</p>
</div><script>
const presets=__PRESETS__;const frame=document.getElementById('frame');const byId=id=>document.getElementById(id);const fields=['width','height','safe-left','safe-right','hinge'];
const titles={a:'上午 · 日程安排',b:'下午 · 长标题示例 Example of a long itinerary item',c:'晚上 · 复盘'};const drafts={a:'准备出发',b:'',c:''},saved={a:'准备出发',b:'',c:''};let selected='a';
const clamp=(v,min,max)=>Math.max(min,Math.min(max,Number(v)||0));
function updateFold(){
  frame.classList.remove('fold-single','fold-unavailable');
  const note=byId('layout-note');
  if(!frame.classList.contains('fold')){note.textContent='常规容器示意。';return;}
  const width=frame.clientWidth,hinge=clamp(byId('hinge').value,0,80);
  const leftPad=Math.max(16,clamp(byId('safe-left').value,0,120));
  const rightPad=Math.max(16,clamp(byId('safe-right').value,0,120));
  const leftEnd=width/2-hinge/2-8,rightStart=width/2+hinge/2+8;
  const leftWidth=Math.max(0,leftEnd-leftPad),rightWidth=Math.max(0,width-rightPad-rightStart);
  const set=(key,value)=>frame.style.setProperty(key,value+'px');
  // A 44px control plus card padding and borders needs 70px; allow 10px
  // extra for the button's intrinsic glyph width and subpixel rounding.
  const minPaneWidth=80;
  if(leftWidth>=150 && rightWidth>=150){
    set('--fold-pad-left',leftPad);set('--fold-pad-right',rightPad);
    set('--fold-left',leftWidth);set('--fold-gap',rightStart-leftEnd);set('--fold-right',rightWidth);
    note.textContent='两栏分置折线两侧；中间警戒区不放置操作。';
  }else if(Math.max(leftWidth,rightWidth)>=minPaneWidth){
    frame.classList.add('fold-single');
    const onRight=rightWidth>=leftWidth;
    set('--fold-single-left',onRight?rightStart:leftPad);
    set('--fold-single-right',onRight?rightPad:width-leftEnd);
    note.textContent='当前空间使用'+(onRight?'右':'左')+'侧单栏，内容不跨越折线。';
  }else{
    frame.classList.add('fold-unavailable');
    note.textContent='当前参数无法容纳最小 44px 操作；请调整宽度、安全区或折线。';
  }
}
function render(){
  frame.style.width=clamp(byId('width').value,280,1200)+'px';
  frame.style.height=clamp(byId('height').value,240,1000)+'px';
  frame.style.setProperty('--safe-left',clamp(byId('safe-left').value,0,120)+'px');
  frame.style.setProperty('--safe-right',clamp(byId('safe-right').value,0,120)+'px');
  frame.style.setProperty('--hinge',clamp(byId('hinge').value,0,80)+'px');
  frame.classList.toggle('fold',presets[Number(byId('scenario').value)].id==='fold');
  frame.dataset.align=byId('control-align').value;
  updateFold();
}
byId('scenario').addEventListener('change',()=>{const p=presets[Number(byId('scenario').value)];byId('width').value=p.width;byId('height').value=p.height;render();});
fields.forEach(id=>byId(id).addEventListener('input',render));byId('control-align').addEventListener('change',render);
new ResizeObserver(updateFold).observe(frame);
document.querySelectorAll('[data-item]').forEach(button=>button.addEventListener('click',()=>{
  drafts[selected]=byId('draft').value;selected=button.dataset.item;
  document.querySelectorAll('[data-item]').forEach(b=>b.setAttribute('aria-current',String(b===button)));
  byId('item-title').textContent=titles[selected];byId('draft').value=drafts[selected];
  byId('saved').textContent=saved[selected]||'尚未确认';byId('status').textContent='当前项目：'+titles[selected];
}));
byId('draft').addEventListener('input',()=>{drafts[selected]=byId('draft').value;});
byId('save').addEventListener('click',()=>{saved[selected]=byId('draft').value;byId('saved').textContent=saved[selected]||'空内容';byId('status').textContent='已确认：'+titles[selected];});
render();
</script></body></html>'''
    html=html.replace('__OPTIONS__',choices).replace('__PRESETS__',presets)
    return prepare_page(html,'adaptive.html')
