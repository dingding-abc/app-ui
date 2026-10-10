"""Generate an isolated 320px/multilingual layout fixture from real component sources."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def build(output):
    from build import CSS, ICONS
    from build_d import GLASS_CSS, gscreen
    from component_catalog import CSS as COMPONENT_CSS
    from site_support import SHARED_CSS, feedback_samples
    from ui_contract import type_css
    from design_tokens import css_vars
    data=json.loads((ROOT/'design-tokens.json').read_text(encoding='utf-8'))
    panels=[]
    for theme,t in data['themes'].items():
        for mode in ('light','dark','light_hc','dark_hc'):
            for scale in (1,1.41,1.75,2):
                label=f'{theme}/{mode}/{scale}'
                palette=css_vars(t[mode])+f';--dt-scale:{scale}'
                panels.append(f'''<section class="stress-mode" data-case="{label}" style="{palette}">
<h2>{label} · 320px</h2><div class="search">{ICONS['SEARCH']}<span>検索・搜索・Find a long saved record</span></div>
<div class="li"><div class="li-tx"><b>通知設定 · 长列表标题</b><span>辅助说明 · Multilingual description</span></div></div>
<button class="btn btn-danger">削除する · 删除记录</button><div class="alert"><div class="alert-btns"><button class="dg">削除する · 删除</button></div></div>
<div class="toast">{ICONS['CHECK']}<span>保存しました · 记录已保存</span></div>
<div class="tabbar">{''.join('<div class="tab'+(' on' if i==0 else '')+'">'+ICONS['HOME']+'<span>'+text+'</span></div>' for i,text in enumerate(['首页 Home','カレンダー','记录 Notes','設定 Settings']))}</div>
<div class="cc-section"><div class="cc-card"><input type="text" value="名称・Name"><p class="cc-success">✓ 已填写</p><p class="cc-error">请修正后重试</p><button disabled>禁用</button><button disabled aria-busy="true">提交中…</button></div></div>
<div class="stress-feedback">{feedback_samples(False)}</div>
</section>''')
        if theme=='D':
            for scale in (1,1.41,1.75,2):
                panels.append(f'<section class="stress-mode" data-case="D/glass/{scale}" style="{css_vars(t["light"])};--dt-scale:{scale}"><h2>D/glass/{scale} · 320px</h2><div class="screen dev">'+gscreen()+'</div></section>')
    style=CSS+GLASS_CSS+SHARED_CSS+COMPONENT_CSS+type_css()+'''
body{margin:0;padding:16px;background:#eee}.stress-grid{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}
.stress-mode{width:320px;max-width:100%;padding:16px;background:var(--bg);color:var(--ink);box-sizing:border-box}
.stress-mode>h2{font:16px/1.5 system-ui}.stress-mode>.toast svg{width:20px;height:20px;flex:none}
.stress-mode>.alert,.stress-mode .screen.dev{max-width:100%}.cc-card{margin-top:16px}
'''
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UI layout stress fixture</title><style>'+style+'</style><body><h1>实际组件 · 320px · 四模式 · 1/1.41/1.75/2倍文字</h1><main class="stress-grid">'+''.join(panels)+'</main></body></html>',encoding='utf-8')
    print(f'Generated {len(panels)} source-based layout cases: {output}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.tmp/ui-stress.html')
    build(parser.parse_args().output)
