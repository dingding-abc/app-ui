"""WidgetKit documentation and static shape previews, not a widget extension."""
CONTRACT = dict(version=1, platform='WidgetKit',
                outer_shape='system_owned', nested_shape='ContainerRelativeShape',
                text_action='capsule', icon_action='circle',
                preview_families=['systemSmall','systemMedium','accessoryCircular','accessoryRectangular','accessoryInline'],
                app_only_components=['hour_picker','time_picker'],
                preview_geometry=dict(outer_radius=28,padding=16,inner_radius=12),
                native_geometry='read_system_family_and_content_margins',
                rendering_modes=['fullColor','accented','vibrant'], native_validation='pending')

CSS = """
.wg-section{margin:48px 0;font-family:system-ui,sans-serif;letter-spacing:normal;color:var(--ink)}
.wg-section>h2{font-size:24px;margin-bottom:12px}.wg-section>p{font-size:15px;line-height:1.8;color:var(--sub)}
.wg-section a{color:var(--accent-text)}
.wg-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin:24px 0}
.wg-mode{min-width:0;background:var(--bg);padding:20px;border-radius:20px;color:var(--ink)}
.wg-mode h3{font-size:17px;margin:0 0 16px}.wg-caption{font-size:13px;line-height:1.7;color:var(--sub);margin:12px 0}
.wg-previews{display:flex;flex-wrap:wrap;align-items:start;gap:16px}
.wg-frame{--wg-demo-outer:28px;--wg-demo-padding:16px;box-sizing:border-box;min-width:0;background:var(--surface);border-radius:var(--wg-demo-outer);padding:var(--wg-demo-padding);border:1px solid var(--line-strong);display:flex;flex-direction:column;gap:12px}
.wg-frame.small{width:184px;max-width:100%;min-height:184px}
.wg-frame.medium{width:100%;max-width:384px;min-height:184px}
.wg-title{font-size:calc(13px * var(--dt-scale,1));color:var(--sub);line-height:1.5}
.wg-time{font-size:calc(28px * var(--dt-scale,1));font-weight:700;line-height:1.2;font-variant-numeric:tabular-nums;color:var(--ink)}
.wg-inner{border-radius:calc(var(--wg-demo-outer) - var(--wg-demo-padding));background:var(--fill);color:var(--ink);padding:12px;font-size:calc(15px * var(--dt-scale,1));line-height:1.6}
.wg-actions{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:auto}
.wg-action{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:10px 16px;border-radius:var(--r-btn);background:var(--accent);color:var(--on-accent);font-size:calc(15px * var(--dt-scale,1));font-weight:600;line-height:1.5;box-sizing:border-box}
.wg-action.secondary{background:var(--surface);color:var(--accent-text);border:1px solid var(--control-border)}
.wg-action.icon{width:44px;height:44px;padding:0;flex:none;border-radius:var(--r-icon);font-size:24px}
.wg-lock{display:flex;align-items:center;flex-wrap:wrap;gap:12px;color:var(--ink);margin-top:16px}
.wg-lock-circle{width:68px;height:68px;border:3px solid currentColor;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px}
.wg-lock-rect{max-width:180px;font-size:15px;line-height:1.5}.wg-lock-inline{width:100%;font-size:13px;line-height:1.5}
@media(max-width:900px){.wg-grid{grid-template-columns:minmax(0,1fr)}}
"""


def samples(dark=False):
    modes = [('dark','dark','深色'),('dark_hc','dark hc','深色 · 增强对比度')] if dark else [('light','','浅色'),('light_hc','hc','浅色 · 增强对比度')]
    cards = ''
    for mode,classes,label in modes:
        cards += f'''<article class="wg-mode {classes}" data-widget-mode="{mode}"><h3>{label}</h3>
<div class="wg-previews">
<div class="wg-frame small" data-widget-family="systemSmall" role="img" aria-label="小尺寸桌面小组件外观：胶囊文字操作和圆形图标操作">
<span class="wg-title">今日提醒</span><strong class="wg-time">09:30</strong><div class="wg-actions"><span class="wg-action">完成</span><span class="wg-action icon" aria-hidden="true">＋</span></div></div>
<div class="wg-frame medium" data-widget-family="systemMedium" role="img" aria-label="中尺寸桌面小组件外观：内部卡片与外层容器圆角协调，按钮为胶囊形">
<span class="wg-title">下一项 · 09:30</span><div class="wg-inner">晨间阅读<br>为自己留出 20 分钟</div><div class="wg-actions"><span class="wg-action">标记完成</span><span class="wg-action secondary">打开日程</span></div></div></div>
<p class="wg-caption">容器内卡片随外框圆角协调；独立文字操作为胶囊，图标操作为圆形。</p>
<div class="wg-lock" role="img" aria-label="锁屏单色布局示意：圆形、矩形和行内，不展示桌面品牌底色">
<div class="wg-lock-circle" data-widget-family="accessoryCircular">2 / 3</div>
<div class="wg-lock-rect" data-widget-family="accessoryRectangular">下一项 09:30<br>晨间阅读</div>
<div class="wg-lock-inline" data-widget-family="accessoryInline">09:30 · 晨间阅读</div></div>
<p class="wg-caption">锁屏布局仅为单色示意；真实颜色、尺寸和背景由系统呈现。</p></article>'''
    return '<section class="wg-section" id="widgetkit"><h2>WidgetKit · 桌面与锁屏小组件</h2><p>外观样张，操作标签不执行动作。尺寸与圆角数字仅用于HTML展示，原生由WidgetKit管理；滚轮选择器保留在App内。</p><div class="wg-grid">' + cards + '</div><p><a href="standards.html#widgetkit">查看小组件圆角、按钮形状与原生验收规则 →</a></p></section>'


def standard():
    return '''<section id="widgetkit"><h2>WidgetKit · 小组件形状与按钮</h2>
<p>此处指iPhone桌面/锁屏小组件，区别于App内控件。小组件用于快速获取信息或执行简短操作；小时/分钟滚轮属于App内界面，小组件显示时间摘要，编辑通过链接进入App。</p>
<div class="kit-table-wrap"><table><tr><th>对象</th><th>本项目规则</th><th>原生实现与边界</th></tr>
<tr><td>小组件外框</td><td>使用系统连续圆角容器，不将主题卡片的12/14/18pt直接当作Widget外框。</td><td>WidgetKit负责最终外形；使用containerBackground(for: .widget)区分背景，遵从系统内容边距。HTML示意外角28、内距16不是Apple固定参数。</td></tr>
<tr><td>靠近外框的内部卡片</td><td>圆角与外框协调，保持同心关系；不要与独立按钮混用半径。</td><td>优先ContainerRelativeShape；CSS仅以外角减内距近似，无法等同原生连续曲线。</td></tr>
<tr><td>独立文字按钮</td><td>App与Widget共用胶囊轮廓，随按钮高度变化；六套主题只改变配色，不另设8–14pt按钮圆角。主要/次要/禁用状态保持同一形状。</td><td>本项目明确选用Capsule作为系列规范，不声称Apple所有按钮都必须胶囊。优先系统Button样式及buttonBorderShape(.capsule)。</td></tr>
<tr><td>图标操作、文字操作和分段控件</td><td>独立图标按钮用圆形；纯文字操作、系统Alert行按钮和分段控件保留各自结构，不套用胶囊外框。</td><td>用SF Symbols和明确的辅助标签；分段控件圆角独立于按钮Token，不能跟随胶囊值膨胀。</td></tr>
<tr><td>不同Widget尺寸与颜色模式</td><td>按systemSmall/Medium/Large及accessoryCircular/Rectangular/Inline分别排版；锁屏不照搬桌面品牌底色。保留标签与形状识别。</td><td>读取widgetFamily、系统内容边距及widgetRenderingMode；单独验收fullColor、accented、vibrant和背景移除状态。当前HTML仅示意小/中尺寸与三类锁屏布局，Large和系统着色待原生实现。</td></tr>
<tr><td>点击与真实数据</td><td>执行动作使用Button/Toggle与App Intent；打开App使用Link/widgetURL。小组件不承载本项目的HTML滚轮、任意滚动表单或App Sheet。</td><td>按目标系统与Widget family核对交互可用性；状态切换使用Toggle，操作失败恢复真实状态。HTML不包含Widget扩展、时间线或真实Intent。</td></tr>
</table></div><p>按钮命中区以44×44pt为本项目起点，视觉尺寸随family调整，不能让相邻区域重叠。需用真实WidgetKit预览/设备验证曲率、边距、字号、锁屏着色和操作；HTML的border-radius不是原生外观验收。</p>
<p><a href="a-yohaku.html#widgetkit">余白Widget样张 →</a> · <a href="a-yohaku-ext.html#widgetkit">深色样张 →</a></p>
<p>依据：<a href="https://developer.apple.com/design/human-interface-guidelines/widgets">Apple Widgets</a> · <a href="https://developer.apple.com/documentation/swiftui/containerrelativeshape">ContainerRelativeShape</a> · <a href="https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities">Widget交互</a>。</p></section>'''
