"""Shared documentation shell and component contract for every generated page."""
import re
from html import escape
from design_tokens import css_vars, hc_css
from hour_picker import CSS as HOUR_CSS, SCRIPT as HOUR_SCRIPT, samples as hour_samples, standard as hour_standard
from widget_spec import CSS as WIDGET_CSS, samples as widget_samples, standard as widget_standard
from component_catalog import CSS as COMPONENT_CSS, SCRIPT as COMPONENT_SCRIPT, samples as component_samples

VERSION = '5.1'


def all_themes():
    from build import THEMES
    from build_d import THEME
    return sorted([*THEMES, THEME], key=lambda t: (len(t['letter']) > 1, t['letter']))


def navigation(current):
    links = [('index.html','总览'),('standards.html','设计与验收规范'),('standards.html#widgetkit','WidgetKit 小组件'),('standards.html#time-picker','时间选择（时/分）'),('components.html','组件索引'),('adaptive.html','自适应场景'),('reuse.html','复用与下载'),('icons.html','图标'),('devices.html','设备尺寸样张')]
    links += [(t['file'], t['jp']) for t in all_themes()]
    return '<nav class="kit-nav" aria-label="规范导航">' + ''.join(
        f'<a href="{f}"' + (' aria-current="page"' if f == current else '') + f'>{escape(n)}</a>' for f,n in links) + '</nav>'


SHARED_CSS = """
/* v5: semantic roles; paper decoration and operable boundaries are separate. */
:root{--space-1:4px;--space-2:8px;--space-3:12px;--space-4:16px;--space-6:24px;--space-8:32px;
--type-body:17px;--type-callout:16px;--type-subhead:15px;--type-footnote:13px;--type-caption:11px;--dt-scale:1}
.kit-nav{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 28px;font:13px/1.5 system-ui,sans-serif}
.kit-nav a{display:inline-flex;align-items:center;min-height:44px;padding:8px 12px;border-radius:9px;color:#554A40;background:#FDFCFA;border:1px solid #D8D0C0;text-decoration:none}
.kit-nav a[aria-current=page]{background:#554A40;color:#fff}
.kit-note{font:13px/1.7 system-ui,sans-serif;color:#554A40;margin:0 0 24px;padding:16px;background:#FDFCFA;border:1px solid #D8D0C0;border-radius:12px}
.kit-note a{color:#654631;text-decoration:underline}
a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--accent-ui,#554A40);outline-offset:3px}
.btn{height:auto;min-height:50px;padding:12px 16px;white-space:normal;line-height:1.5;text-align:center}
.btn-sm{min-height:44px;height:auto}
.btn:active:not(:disabled):not(.btn-disabled){transform:scale(.98)}
.btn-disabled,.btn:disabled{cursor:not-allowed}
.btn-loading{opacity:1}
.input,.row-field{height:auto;min-height:48px;padding-top:12px;padding-bottom:12px}
.input,.textarea,.cbx,.rdo,.ibtn{border-color:var(--control-border)}
.input.focus{border-color:var(--accent-ui)}
.chip{height:auto;min-height:32px;padding-top:6px;padding-bottom:6px;white-space:normal}
.chip[role=button]{min-height:44px}
.ctl-row{min-height:44px;gap:12px}.ctl-label{flex:1}
.cbx,.rdo,.toggle{flex-shrink:0;position:relative}
.toggle{border:1px solid var(--control-border)}.toggle::after{box-shadow:inset 0 0 0 1px var(--on-accent)}
.cbx::before,.rdo::before,.toggle::before{content:"";position:absolute;min-width:44px;min-height:44px;left:50%;top:50%;transform:translate(-50%,-50%)}
.seg span{min-height:44px;display:flex;align-items:center;justify-content:center;padding:8px;white-space:normal}
.cal-d{min-height:44px}.tab,.gtab .ti{min-height:44px}
.tab.on{border-top:2px solid var(--accent-ui)}
.tab.on,.gtab .ti.on{color:var(--accent-text)}
.btn-ghost,.alert-btns .em,.kw span,.sl-head b,.q-title,.notes h4,.col-tag .no{color:var(--accent-text)}
.kw span{border-color:var(--accent-ui)}
.rdo.on{border-color:var(--accent-ui)}.rdo.on::after{background:var(--accent-ui)}
.sl-fill{background:var(--accent-ui)}
.sched.t2 .chip,.chip.t2{color:var(--tone2-text)}.sched.t3 .chip,.chip.t3{color:var(--tone3-text)}
.field-msg,.field-label .req{color:var(--danger-text)}
.screen .li-tx b,.screen .ctl-label,.screen .q-text{font-size:calc(var(--type-body) * var(--dt-scale,1))}
.screen .sched h5,.screen .sched .bd h5{font-size:calc(var(--type-subhead) * var(--dt-scale,1))}
.screen .sched p,.screen .li-tx span{font-size:calc(var(--type-footnote) * var(--dt-scale,1))}
.screen .tab{font-size:calc(var(--type-caption) * var(--dt-scale,1))}
.scr-scroll{overflow-y:auto;min-height:0}.scr{min-height:0}
.phone{max-width:100%}.phone .q-text{font-size:calc(var(--type-body) * var(--dt-scale,1))}
.s-body{overflow-y:auto;min-height:0}.sheet{max-height:calc(100% - 20px);overflow-y:auto}
.sheet.full{overflow:hidden}.sheet.full>.btn{flex-shrink:0}.s-opt{height:auto;min-height:52px;padding:12px 0}
.s-nav .xi{width:44px;height:44px}.s-nav .save{display:inline-flex;align-items:center;min-height:44px}
.screen.ob-scr{overflow-y:auto}.ob{flex-shrink:0}
.banner.warn{background:var(--warning-soft);color:var(--warning-text)}.banner.warn .bi{color:var(--warning-text)}
.kit-status{padding:12px 16px;border-radius:9px;margin:8px 0;font-size:15px;line-height:1.6}
.kit-status.success{background:var(--success-soft);color:var(--success-text)}
.kit-status.warning{background:var(--warning-soft);color:var(--warning-text)}
.kit-status.info{background:var(--info-soft);color:var(--info-text)}
.board{max-width:100%;}.cols,.stage{flex-wrap:wrap}.col{max-width:100%}
.bh{flex-wrap:wrap;gap:24px}.bh-title{min-width:0}.screen{max-width:100%}
.kit-table-wrap{overflow-x:auto}.kit-doc{max-width:1000px;margin:auto;padding:32px 24px 64px}
.kit-doc h1{font-size:32px;margin:16px 0}.kit-doc h2{font-size:22px;margin:32px 0 12px}
.kit-doc p,.kit-doc li{font-size:16px;line-height:1.85}.kit-doc ul{padding-left:24px}
.kit-doc table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.7}
.kit-doc th,.kit-doc td{padding:12px;text-align:left;border-bottom:1px solid #D8D0C0;vertical-align:top}
@media(max-width:700px){.board{width:100%;padding:24px 16px}.bh-left{flex-wrap:wrap}.col{width:100%!important;flex-basis:100%}.cols{gap:24px}.stage{gap:24px}.sec-tag{flex-wrap:wrap}.bh-title h1{font-size:30px}.kit-doc{padding:24px 16px}.igrid{grid-template-columns:repeat(3,minmax(0,1fr))}.dd{flex-wrap:wrap}.dc-row{min-width:850px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.btn:active{transform:none!important}}
@media(prefers-reduced-transparency:reduce){.glass,.gnav,.gtab,.gbtn,.nav.glass,.tabbar.glass,.dglass .sheet{background:var(--surface)!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important}}
"""


def prepare_page(page, current, theme=None):
    page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">', 1)
    page = re.sub(r'<div class="nav-row">.*?</div>', '', page, flags=re.S)
    note = '<aside class="kit-note">v5 · 共用设计规范。这里展示组件外观，不连接业务服务；字号比例是排版演示。<a href="standards.html">查看交互规则与 iOS 验收要求</a></aside>'
    page = page.replace('<div class="board">', '<div class="board">' + navigation(current) + note, 1)
    if theme:
        base = theme['file']
        sibling = base if current.endswith('-ext.html') else base.replace('.html','-ext.html')
        page = page.replace(note, note + f'<p class="kit-note"><a href="{sibling}">查看本主题的' + ('基础组件' if current.endswith('-ext.html') else '扩展组件与深色样张') + '</a></p>', 1)
    extra = SHARED_CSS
    if current in ("index.html", "standards.html", "components.html", "adaptive.html", "reuse.html"):
        from build import THEMES, derive
        extra = ":root{" + css_vars(derive(THEMES[0]["vars"], True)) + "}" + extra
    if theme and theme.get('material') == 'glass':
        extra += '.tabbar{background:color-mix(in srgb,var(--surface) 90%,transparent);backdrop-filter:blur(24px)}@media(prefers-reduced-transparency:reduce){.tabbar{background:var(--surface);backdrop-filter:none}}'
    if theme:
        states = '<section class="notes"><h3>状态语义</h3><div class="kit-status success">✓ 已保存 · 操作成功</div><div class="kit-status warning">! 需要留意 · 请检查输入</div><div class="kit-status info">i 提示 · 更多操作信息</div><p>错误需说明原因及恢复操作；状态同时使用文字或图标，不只靠颜色。</p></section>'
        extra += HOUR_CSS + WIDGET_CSS + COMPONENT_CSS
        page = page.replace('<div class="foot">', states + widget_samples(current.endswith('-ext.html')) + hour_samples(current.endswith('-ext.html')) + component_samples('dark' if current.endswith('-ext.html') else 'light') + '<div class="foot">', 1)
        page = page.replace('</body>', '<script>' + HOUR_SCRIPT + COMPONENT_SCRIPT + '</script></body>', 1)
    page = page.replace('</head>', '<style>' + extra + '</style></head>', 1)
    page = page.replace('<button class="btn btn-disabled">', '<button class="btn btn-disabled" disabled>')
    page = page.replace('AX3 1.75', '排版压力 1.75×')
    page = page.replace('五个方向', '各个主题').replace('五方向 Token', '各主题 Token')
    return re.sub(r'[ \t]+(?=\r?$)', '', page, flags=re.M)


def index_page(icon_count):
    themes = all_themes()
    featured = ''
    previews = {'a-yohaku.html': 'yohaku.jpg', 'theme-sunny-day.html': 'sunny-day.jpg'}
    for t in themes:
        if t['file'] in previews:
            featured += f'''<article class="theme-card"><small>{escape(t['romaji'])}</small><h3>{escape(t['jp'])}</h3><p>{escape(t['desc'])}</p><a href="{t['file']}" aria-label="查看{escape(t['jp'])}基础样张"><img class="theme-preview" src="docs/previews/{previews[t['file']]}" alt="{escape(t['jp'])}浅色样张：按钮、表单、日期与列表" loading="lazy"></a><a href="{t['file']}">打开基础样张 →</a><a href="{t['file'].replace('.html','-ext.html')}">查看深色与扩展组件 →</a></article>'''
    cards = ''
    for t in themes:
        p = t['vars']
        dots = ''.join(f'<i style="background:{p[k]}" title="{k} {p[k]}"></i>' for k in ('bg','surface','ink','accent'))
        cards += f'<article class="theme-card"><small>{escape(t["romaji"])}</small><h2>{escape(t["jp"])}</h2><p>{escape(t["desc"])}</p><div class="dots">{dots}</div><a href="{t["file"]}">基础组件 →</a><a href="{t["file"].replace(".html","-ext.html")}">深色与扩展组件 →</a></article>'
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>日式简约 iOS UI · 设计规范 v{VERSION}</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#F1EEE8;color:#2A2723;font-family:system-ui,"PingFang SC","Microsoft YaHei",sans-serif}}.board{{width:1240px;margin:auto;padding:48px 32px}}h1{{font-size:36px;line-height:1.4}}.lead{{max-width:760px;font-size:17px;line-height:1.9;color:#554A40}}.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:32px 0}}.theme-card{{padding:24px;background:#FDFCFA;border:1px solid #DDD5C9;border-radius:16px;display:flex;flex-direction:column}}.theme-card small{{font-size:12px;letter-spacing:.12em;color:#675D51}}.theme-card h2{{margin:12px 0;font-size:26px}}.theme-card p{{font-size:15px;line-height:1.8;color:#554A40;flex:1}}.theme-card a,.resource{{color:#654631;display:block;padding:12px 0;min-height:44px;font-size:15px}}.dots{{display:flex;gap:8px;margin:12px 0}}.dots i{{width:26px;height:26px;border:1px solid #C4BAAD;border-radius:50%}}.resources{{padding:24px;background:#FDFCFA;border-radius:16px;line-height:1.8}}@media(max-width:950px){{.cards{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:600px){{.cards{{grid-template-columns:1fr}}}}</style></head><body><div class="board">
<h1>iPhone UI 样式</h1><p class="lead">按钮、表单、列表、日历和小组件的 HTML 参考样张。选一套配色，打开页面查看。</p>
<div class="resources"><b>使用顺序</b><p>先选配色，再按页面需要取用组件。字号、间距和交互规则集中放在设计规范中。</p><a class="resource" href="standards.html">设计原则、字体、语义颜色、组件与验收要求 →</a></div>
<div class="cards">{cards}</div><div class="resources"><a class="resource" href="components.html">交互组件索引 →</a><a class="resource" href="adaptive.html">自适应容器场景 →</a><a class="resource" href="reuse.html">完整源码与离线预览下载 →</a><a class="resource" href="icons.html">{icon_count} 枚线性图标 · 7 类 · 通用与原生 Tab 规则 →</a><a class="resource" href="devices.html">{len(themes)} 套主题 × 4 个 iPhone 16 尺寸样张 →</a><p>要增加配色，可使用仓库中的 skill 和 Python 脚本。现有组件会一并生成。</p><p>当前交付为 HTML 规范与色彩数据。自动检查记录见项目验收报告；浏览器视觉复验、原生 Dynamic Type、VoiceOver 和真机触控为独立验收项。</p></div></div></body></html>'''
    page = page.replace('</style>', '.featured{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin:24px 0 40px}.theme-preview{display:block;width:100%;height:auto;border-radius:8px}.featured h3{font-size:26px;margin:12px 0}@media(max-width:700px){.featured{grid-template-columns:1fr}}</style>', 1)
    intro = '<section aria-labelledby="featured-title"><h2 id="featured-title">样式预览</h2><p class="lead">先放两套浅色样张。打开主题页面，还可以看深色版本和试用页面底部的交互组件。</p><div class="featured">' + featured + '</div></section><h2>全部主题</h2>'
    page = page.replace('<div class="cards">', intro + '<div class="cards">', 1)
    return prepare_page(page, 'index.html')


def standards_page():
    content = '''<h1>设计与验收规范</h1><p>固定组件语义与交互习惯，允许主题变化。相同组件跨主题保持结构一致；不同业务流程按任务设计页面。</p>
<h2>颜色按用途取用</h2><div class="kit-table-wrap"><table><tr><th>用途</th><th>规则</th></tr>
<tr><td>品牌填充 accent / 彩底文字 on-accent</td><td>品牌色可以浅；配对文字至少 4.5:1。文字操作不直接使用品牌填充色。</td></tr>
<tr><td>强调文字 accent-text / 功能图标 accent-ui</td><td>普通文字至少 4.5:1；必要图形与控件边界至少 3:1。选中状态同时有字重、边线或标记。</td></tr>
<tr><td>分类、图表与状态</td><td>分类文字独立于装饰色；成功、警告、错误和信息同时提供文字或图标。图表保留单位、范围、数值及可读的数据替代，不只靠颜色。</td></tr>
<tr><td>浅色／深色／增强对比度</td><td>四种组合独立生成。增强对比度下文字目标 7:1，不能回退到另一模式的颜色。</td></tr></table></div>
<h2>文字与间距</h2><p>正文 17、操作说明 16、次标题 15、辅助说明 13、短标签 11；标题按用途使用 20 / 22 / 28 / 34。iOS 使用系统 Text Style，不将 HTML 比例等同于系统字号档位。可保留展示性书法或罗马字标识，功能文字随语言调整字体、字距与行高。</p><p>间距使用 4 / 8 / 12 / 16 / 24 / 32，页面边距默认 16。数字是起点，不强迫不同业务拥有相同布局。大字号时按钮、表单和卡片允许撑高，必要时由横向改纵向。</p>
<h2>组件与交互</h2><ul><li>每屏主要操作明确；按钮区分默认、按下、禁用与提交中。提交中防止重复提交，失败保留输入并提供重试。</li><li>常用操作命中区域至少 44×44pt。22pt 图形保留在足够大的点击区域内；不可用扩大区域造成相邻操作重叠。</li><li>输入框明确标签、必填、错误原因和恢复方式；弹出键盘后仍能看到当前输入与主要操作。</li><li>Sheet 区分取消与保存；有未保存内容时关闭需处理丢失风险；滚动到末尾的内容和操作不能被悬浮栏遮挡。</li><li>列表提供加载、空、失败、无权限与正常状态。HTML 样张不代表联网业务已经实现。</li></ul>
<h2>图标与材质</h2><p>通用自绘图标采用 24pt 网格、约 20pt 核心绘制区、1.6pt 圆头线条；箭头与勾号可按既有例外加粗。原生 Tab 优先采用系统组件与匹配的 SF Symbols 变体，允许填充图标。普通线性图标和原生 Tab 的例外需明确区分。</p><p>主题色与材质是两个维度。玻璃只用于导航与控件，不铺满内容卡片。HTML 毛玻璃仅为视觉示意；iOS 使用系统材质并响应降低透明度、减少动态效果。老系统回退到实色，不改变操作含义。</p>
<h2>验收顺序</h2><ol><li>P0：四种颜色组合、标签文字、按钮字色和功能图标对比度。</li><li>P1：主题覆盖、页面导航、图标规则、长文案及字号放大、命中区和文档一致性。</li><li>P2：新主题生成、重复构建稳定、配置校验、资源与导出数据可追溯。</li><li>iOS 工程：最小与最大支持设备、系统大字号、VoiceOver、键盘、深浅模式及减少动态效果。通过记录必须含版本、场景和实际结果。</li></ol><p>设备页面是预设尺寸下的 HTML 样张，不是模拟器或真机检测报告。安全区由系统读取，不把样张中的 62 / 34 常量写入产品。</p>
<h2>依据</h2><p><a href="https://developer.apple.com/design/human-interface-guidelines/typography">Apple 字体</a> · <a href="https://developer.apple.com/design/human-interface-guidelines/buttons">Apple 按钮</a> · <a href="https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass">Liquid Glass</a> · <a href="https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html">WCAG 文字对比度</a></p>'''
    content = content.replace('<h2>图标与材质</h2>', widget_standard() + hour_standard() + '<h2>图标与材质</h2>')
    page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>设计与验收规范 v5</title><style>body{margin:0;background:#F1EEE8;color:#2A2723;font-family:system-ui,sans-serif}a{color:#654631}</style></head><body><div class="board"><main class="kit-doc">' + content + '</main></div></body></html>'
    return prepare_page(page, 'standards.html')
