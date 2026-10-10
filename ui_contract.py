"""Shared UI semantics for CSS, exported data and generated guidance."""
from html import escape

# Keep 5.1's numeric typography API; richer roles are an additive export.
TYPE_SIZES = dict(body=17, callout=16, subhead=15, footnote=13, caption=11)
TYPE_ROLES = {
    'page_title': dict(size=28, weight=700, line_height=1.4, system_text_style='title1'),
    'section_title': dict(size=22, weight=700, line_height=1.4, system_text_style='title2'),
    'list_title': dict(size=17, weight=600, line_height=1.5, system_text_style='headline'),
    'field_value': dict(size=17, weight=400, line_height=1.5, system_text_style='body'),
    'action': dict(size=16, weight=600, line_height=1.5, system_text_style='callout'),
    'subhead': dict(size=15, weight=600, line_height=1.5, system_text_style='subheadline'),
    'auxiliary': dict(size=13, weight=400, line_height=1.6, system_text_style='footnote'),
    'navigation_label': dict(size=11, weight=500, line_height=1.5, system_text_style='caption2'),
}
SPACING = [4, 8, 12, 16, 24, 32]
LAYOUT = dict(min_target=44, component_gap=8, component_padding=16,
              section_gap=24, page_inset=16,
              exceptions=['device_safe_area_illustrations', 'icon_geometry',
                          'decorative_artwork', 'optical_borders_and_indicators'],
              theme_shapes=['r_card', 'r_in'], fixed_shapes=['r_btn', 'r_segment'])
FEEDBACK = dict(version=1, alignment='horizontal_center', top_reference='actual_safe_area_bottom',
                top_offset=8, unit='pt', hold_ms=1500, fade_ms=200, fade_property='opacity',
                fade_curve='ease-out', safe_area_applied_once=True, layout='overlay_no_space',
                pointer_events='none', foreground='accent_deep', background='accent_soft',
                reduced_motion='hide_without_animation', lifecycle='replace_cancel_old_callbacks',
                static_preview='persistent_no_timer', accessibility='extend_or_revisit_when_needed')
FEEDBACK_RULES = [
    f"提示水平居中，位于实际系统顶部安全区下沿再向下 {FEEDBACK['top_offset']}pt；避开摄像头、刘海、灵动岛和状态栏。容器已排除安全区时只加偏移，不能重复叠加。必要时只向下避开关键操作，保持居中。",
    "使用独立浮层，不占位、不压缩或推移内容、不额外预留空白；出现、淡出、移除均不改变底层布局、内容高度或滚动位置。浮层独立于内容滚动，非交互层不拦截触控、不抢输入或读屏焦点，无确认按钮。",
    f"从内容完整显示开始停留 {FEEDBACK['hold_ms']/1000:g} 秒，再以 {FEEDBACK['fade_ms']}ms opacity 1 → 0 缓出并移除；停留时间不包含淡出。不叠加位移或缩放。减少动态效果时到时直接隐藏。",
    "同时只有一条；相同信息合并，新信息替换并重新计时，取消旧计时器、淡出和回调，旧回调不能移除新提示。离开页面或卸载时清理。",
    "胶囊背景 accent_soft，文字与图标 accent_deep；普通模式至少 4.5:1，HC 至少 7:1。成功仅对应真实成功；简短反馈允许换行，不只靠颜色。",
    "错误恢复、持续离线／无权限及重要信息保留在页面或弹层；风险操作和选择器草稿仍需既有确认。使用平台状态播报，HTML 使用 role=status；读屏、大字体或长文本可延长停留或再次查看结果。",
    "当前 HTML 样张持续可见，无计时器或消失动画。真实时长、安全区、触控和 VoiceOver 须在消费 App 验证；59px 安全区及摄像头仅为示意，不是原生固定值。",
]


def feedback_markdown():
    return '\n\n'.join('- ' + rule for rule in FEEDBACK_RULES)


def feedback_standard():
    return ('<section id="transient-feedback"><h2>顶部轻提示</h2>'
            f'<p>保存成功、复制完成等简短非阻断反馈；项目默认完整停留 {FEEDBACK["hold_ms"]/1000:g} 秒，加 {FEEDBACK["fade_ms"]}ms 淡出。</p><ul>'
            + ''.join('<li>' + escape(rule) + '</li>' for rule in FEEDBACK_RULES)
            + '</ul><p>权威契约：ui_contract.py → FEEDBACK，导出 components.transient_feedback。'
            '<a href="docs/interaction-standard.md#顶部轻提示2026-10-10">接入与验收说明</a></p></section>')


def type_css():
    variables = [f'--type-{name}:{size}px' for name, size in TYPE_SIZES.items()]
    variables += [f'--spacing-{size}:{size}px' for size in SPACING]
    variables += [f'--layout-{name.replace("_","-")}:{LAYOUT[name]}px'
                  for name in ('component_gap','component_padding','section_gap','page_inset')]
    # Preserve the existing ordinal aliases rather than changing their meaning.
    variables += [f'--space-{index}:{size}px' for index, size in ((1,4),(2,8),(3,12),(4,16),(6,24),(8,32))]
    for name, role in TYPE_ROLES.items():
        key = name.replace('_', '-')
        variables += [f'--font-{key}:{role["size"]}px', f'--weight-{key}:{role["weight"]}',
                      f'--leading-{key}:{role["line_height"]}']
    groups = {
        'page_title': '.date-big,.gnav .gt,.tf-content h3,.s-nav .t',
        'section_title': '.sec-tag h2,.cc-section h3,.scr-sec h3',
        'list_title': '.li-tx b,.sched .bd h5,.gev h5,.tf-card h4,.cc-card h4,.alert h4,.sheet h4',
        'field_value': '.input,.row-field .rf-val,.textarea,.ctl-label,.q-text,.li .val,.cc-card input[type=text],.cc-card input[type=search]',
        'action': '.btn,.gbtn,.alert-btns button,.s-opt,.search,.toast,.tf-notice,.cc-card button,.cc-dialog button',
        'subhead': '.tf-row,.sl-head',
        'auxiliary': '.li-tx span,.sched .bd p,.gev p,.ctl-sub,.field-label,.field-msg,.rf-lab,.alert p,.tf-brand,.tf-saved',
        'navigation_label': '.tab,.gtab .ti',
    }
    rules = [':root{' + ';'.join(variables) + '}']
    for name, selectors in groups.items():
        key = name.replace('_', '-')
        rules.append(f':is({selectors})' + '{'
                     f'font-size:calc(var(--font-{key}) * var(--dt-scale,1));'
                     f'font-weight:var(--weight-{key});line-height:var(--leading-{key});' + '}')
    # Specific legacy phone selectors must use the same role at all sizes.
    rules.append('.screen .tab{font-size:calc(var(--font-navigation-label) * var(--dt-scale,1))}')
    return '\n'.join(rules)


def typography_standard():
    rows = ''.join(f'<tr><td>{name}</td><td>{r["size"]} / {r["weight"]} / {r["line_height"]}</td><td>{r["system_text_style"]}</td></tr>' for name, r in TYPE_ROLES.items())
    return ('<h2>文字与间距</h2><div class="kit-table-wrap"><table><tr><th>语义</th><th>字号 / 字重 / 行高</th><th>系统 Text Style</th></tr>' + rows + '</table></div>'
            '<p>ui_contract.py 是主要组件排版与间距来源；iOS 使用对应系统 Text Style，HTML 比例只作压力演示。书法、罗马字品牌、画板标题、图表标注与装饰插画可保留展示字号；不能用于替代功能文字。</p>'
            f'<p>主要组件使用 {" / ".join(map(str,SPACING))} 间距；组件内边距 {LAYOUT["component_padding"]}、组间 {LAYOUT["component_gap"]}、节间 {LAYOUT["section_gap"]}、页面边距 {LAYOUT["page_inset"]}。设备示意安全区、图标几何、装饰插画及边线/指示器的光学尺寸为明确例外。卡片 r_card 和输入 r_in 可随主题变化；独立按钮固定胶囊、图标按钮圆形，导航选中及分段控件固定 r_segment。大字号允许换行和撑高。</p>')
