"""Hour-only and hour/minute wheel contracts shared by every theme."""
from html import escape

CONTRACT = dict(version=2, meaning='hour_of_day', minimum=0, maximum=23, step=1,
                sample_hour=9, wraps=True, commit='explicit_confirmation',
                row_min_pt=44, visible_rows=5, number_size_pt=22,
                colors=dict(background='surface', selection='fill', selected_text='ink',
                            other_text='sub', marker='accent_ui', boundary='control_border'))

TIME_CONTRACT = dict(version=2, meaning='local_time_of_day', hour=dict(minimum=0,maximum=23,step=1),
                     minute=dict(minimum=0,maximum=59,step=1,allowed_steps=[1,5,10,15,30]),
                     sample=dict(hour=9,minute=30), wraps=True, carry_between_columns=False,
                     commit='both_columns_together', invalid_initial_value='reject_without_rounding',
                     layout='two_columns', colors=CONTRACT['colors'])

CSS = """
.hp-section{margin:48px 0;letter-spacing:normal;font-family:system-ui,sans-serif}
.hp-section>h2{font-size:24px;color:var(--ink)}
.hp-section>p{font-size:15px;line-height:1.8;color:var(--sub)}
.hp-section>p a{color:var(--accent-text)}
.hp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,390px));gap:24px;margin:24px 0}
.hp-card{min-width:0;padding:20px;background:var(--surface);color:var(--ink);border:1px solid var(--control-border);border-radius:16px;--hp-row:max(44px,2.2em);font-size:calc(22px * var(--dt-scale,1))}
.hp-card h3{margin:8px 0;font-size:calc(20px * var(--dt-scale,1));line-height:1.5}
.hp-card .hp-mode,.hp-card .hp-hint,.hp-card .hp-result{font-size:calc(13px * var(--dt-scale,1));line-height:1.7;color:var(--sub);margin:8px 0}
.hp-card .hp-value{font-size:calc(17px * var(--dt-scale,1));margin:16px 0;color:var(--ink)}
.hp-frame{position:relative;margin:16px 0}
.hp-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.hp-columns>*{min-width:0}
.hp-column-label{display:block;text-align:center;font-size:calc(15px * var(--dt-scale,1));color:var(--sub);line-height:1.5;margin-top:12px}
.hp-columns .hp-frame{margin-top:8px}
.hp-band{pointer-events:none;position:absolute;top:calc(2 * var(--hp-row));height:var(--hp-row);left:0;right:0;background:var(--fill);border-block:1px solid var(--control-border);border-left:3px solid var(--accent-ui);border-radius:8px}
.hp-wheel{position:relative;height:calc(5 * var(--hp-row));padding-block:calc(2 * var(--hp-row));overflow-y:auto;overscroll-behavior:contain;scroll-snap-type:y mandatory;scrollbar-width:none;font-size:inherit;outline-offset:3px;touch-action:pan-y;overflow-anchor:none}
.hp-wheel::-webkit-scrollbar{display:none}
.hp-option{height:var(--hp-row);display:flex;align-items:center;justify-content:center;scroll-snap-align:center;font-variant-numeric:tabular-nums;color:var(--sub);cursor:pointer;line-height:1.4}
.hp-wheel:not([data-loop-ready]) .hp-option[aria-selected=true],.hp-option[data-active=true]{color:var(--ink);font-weight:700}
.hp-option small{font-size:calc(15px * var(--dt-scale,1));margin-left:12px}
.hp-wheel:focus-visible{outline:3px solid var(--accent-ui)}
.hp-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:16px}
.hp-actions button{flex:1;min-width:88px;min-height:44px;padding:10px 16px;border-radius:var(--r-btn);font:inherit;font-size:calc(17px * var(--dt-scale,1));line-height:1.5;cursor:pointer}
.hp-cancel{background:var(--surface);border:1px solid var(--control-border);color:var(--accent-text)}
.hp-confirm{background:var(--accent);color:var(--on-accent);border:1px solid var(--control-border)}
.hp-actions button:disabled{background:var(--fill);color:var(--sub);border:1px dashed var(--control-border);cursor:not-allowed}
@media(max-width:700px){.hp-grid{grid-template-columns:minmax(0,1fr)}}
"""

# This state logic is also exercised without a browser by test_picker_state.py.
STATE_SCRIPT = r"""
function wrapWheelIndex(index, count) {
  return ((Math.round(index) % count) + count) % count;
}
function recenterWheelPosition(position, count) {
  // Preserve sub-row position when relocating an equivalent repeating segment.
  return 3 * count + ((position % count) + count) % count;
}
function createWheelState(columns, initial) {
  let committed = [...initial];
  let draft = columns.map((values, i) => values.indexOf(initial[i]));
  if (draft.some(i => i < 0)) throw new RangeError('Initial value is not selectable');
  const moving = columns.map(() => false);
  return {
    index: col => draft[col],
    values: () => draft.map((i, col) => columns[col][i]),
    saved: () => [...committed],
    ready: () => moving.every(value => !value),
    begin: col => { moving[col] = true; },
    move: (col, index) => { draft[col] = wrapWheelIndex(index, columns[col].length); },
    settle: col => { moving[col] = false; },
    commit() {
      if (!this.ready()) return false;
      committed = this.values(); return true;
    },
    cancel() {
      draft = columns.map((values, i) => values.indexOf(committed[i]));
      moving.fill(false);
    }
  };
}
"""

# Each wheel tracks its own settling state; either moving column blocks confirmation.
SCRIPT = '(() => {\n' + STATE_SCRIPT + r"""
  document.querySelectorAll('[data-hour-picker], [data-time-picker]').forEach(card => {
    const wheels = Array.from(card.querySelectorAll('.hp-wheel'));
    const optionGroups = wheels.map(wheel => Array.from(wheel.querySelectorAll('[role="option"]')));
    const initial = card.hasAttribute('data-time-picker')
      ? [Number(card.dataset.timePicker), Number(card.dataset.initialMinute)]
      : [Number(card.dataset.hourPicker)];
    const state = createWheelState(optionGroups.map(options => options.map((o, i) => Number(o.dataset.value ?? i))), initial);
    const confirm = card.querySelector('.hp-confirm');
    const result = card.querySelector('.hp-result');
    const saved = card.querySelector('.hp-saved');
    const format = values => [values[0], values[1] ?? 0].map(n => String(n).padStart(2, '0')).join(':');
    const updateButton = () => {confirm.disabled = !state.ready();};
    const controls = wheels.map((wheel, col) => {
      const options = optionGroups[col];
      const count = options.length;
      // Seven visual cycles provide neighbours on both sides of 00. Only the
      // middle cycle retains option semantics; decorative copies are hidden to AT.
      const fragment = document.createDocumentFragment();
      const rows = [];
      for (let cycle = 0; cycle < 7; cycle++) {
        options.forEach(option => {
          const row = cycle === 3 ? option : option.cloneNode(true);
          if (cycle !== 3) {
            row.removeAttribute('id'); row.removeAttribute('aria-selected');
            row.setAttribute('role', 'presentation'); row.setAttribute('aria-hidden', 'true');
          }
          fragment.appendChild(row); rows.push(row);
        });
      }
      wheel.replaceChildren(fragment);
      wheel.dataset.loopReady = 'true';
      let timer;
      const rowHeight = () => options[0].getBoundingClientRect().height;
      function paint() {
        options.forEach((option, i) => option.setAttribute('aria-selected', String(i === state.index(col))));
        wheel.setAttribute('aria-activedescendant', options[state.index(col)].id);
        const visibleRow = Math.round(wheel.scrollTop / rowHeight());
        rows.forEach((row, i) => row.dataset.active = String(i === visibleRow));
      }
      function move(n) {
        clearTimeout(timer); state.move(col, n);
        wheel.scrollTop = (3 * count + state.index(col)) * rowHeight();
        paint();
        state.settle(col); updateButton();
      }
      wheel.addEventListener('scroll', () => {
        state.begin(col); updateButton();
        let position = wheel.scrollTop / rowHeight();
        if (position < count || position > 5 * count) {
          position = recenterWheelPosition(position, count);
          wheel.scrollTop = position * rowHeight();
        }
        state.move(col, position); paint();
        clearTimeout(timer);
        timer = setTimeout(() => move(Math.round(wheel.scrollTop / rowHeight())), 180);
      }, {passive:true});
      wheel.addEventListener('keydown', event => {
        const draft = state.index(col);
        const next = {ArrowUp:draft-1, ArrowDown:draft+1, Home:0, End:options.length-1,
                      PageUp:draft-5, PageDown:draft+5}[event.key];
        if (next !== undefined) {event.preventDefault(); move(next);}
      });
      rows.forEach((option, i) => option.addEventListener('click', () => {move(i); wheel.focus();}));
      move(state.index(col));
      if (typeof ResizeObserver !== 'undefined') {
        let lastHeight = rowHeight();
        new ResizeObserver(() => {
          const height = rowHeight();
          if (height !== lastHeight) {lastHeight = height; move(state.index(col));}
        }).observe(options[0]);
      }
      return {restore: () => move(state.index(col))};
    });
    card.querySelector('.hp-cancel').addEventListener('click', () => {
      state.cancel(); controls.forEach(control => control.restore());
      result.textContent = '已取消本次修改，保留 ' + format(state.saved()) + '。';
    });
    confirm.addEventListener('click', () => {
      if (!state.commit()) return;
      saved.textContent = format(state.saved());
      result.textContent = '已确认 ' + format(state.saved()) + '（仅当前页面演示）。';
    });
    updateButton();
    card.querySelector('.hp-cancel').disabled = false;
    result.textContent = '可滚动或使用方向键，各列停稳后确认。';
  });
})();
"""


def card(prefix, mode, hour=9):
    if type(hour) is not int or not CONTRACT['minimum'] <= hour <= CONTRACT['maximum']:
        raise ValueError('Hour must be an integer from 0 through 23')
    prefix = escape(prefix, quote=True)
    mode_class = {'light':'', 'light_hc':'hc', 'dark':'dark', 'dark_hc':'dark hc'}[mode]
    label = {'light':'浅色', 'light_hc':'浅色 · 增强对比度', 'dark':'深色', 'dark_hc':'深色 · 增强对比度'}[mode]
    options = ''.join(f'<div class="hp-option" id="{prefix}-{n}" role="option" aria-selected="{str(n == hour).lower()}" data-hour="{n}" aria-label="{n:02d} 时">{n:02d}<small aria-hidden="true">时</small></div>' for n in range(24))
    return f'''<article class="hp-card {mode_class}" data-hour-picker="{hour}" data-hour-mode="{mode}">
<p class="hp-mode">{label} · Sheet 内容示例</p><h3 id="{prefix}-title">选择提醒小时</h3>
<p class="hp-hint" id="{prefix}-hint">24 小时制 · 首尾循环，每次选择一个整点。滚动或使用 ↑ ↓，Home / End 到首尾。</p>
<p class="hp-value">已确认：<strong class="hp-saved">{hour:02d}:00</strong></p>
<div class="hp-frame"><div class="hp-band" aria-hidden="true"></div><div class="hp-wheel" role="listbox" tabindex="0" aria-labelledby="{prefix}-title" aria-describedby="{prefix}-hint" aria-activedescendant="{prefix}-{hour}">{options}</div></div>
<div class="hp-actions"><button type="button" class="hp-cancel" disabled>取消</button><button type="button" class="hp-confirm" disabled>确认</button></div>
<p class="hp-result" role="status" aria-live="polite">交互演示需要 JavaScript；已确认值为 {hour:02d}:00。</p></article>'''


def samples(dark=False):
    modes = ('dark','dark_hc') if dark else ('light','light_hc')
    return '<section class="hp-section" id="hour-picker"><h2>小时滚动选择</h2><p>居中一行表示当前草稿，确认后才更新已确认值。下方为展开的 Sheet 内容样张；不连接业务服务，刷新恢复 09:00。</p><div class="hp-grid">' + ''.join(card('hp-'+mode,mode) for mode in modes) + '</div><p><a href="standards.html#hour-picker">查看尺寸、状态、12 小时制与原生验收标准 →</a></p></section>' + '<section class="hp-section" id="time-picker"><h2>小时＋分钟 · 双列滚轮</h2><p>小时 00–23，分钟 00–59，每次 1 分钟；两列分别滚动，共同确认。小时23↔00、分钟59↔00首尾循环；分钟循环不自动改变小时。刷新恢复 09:30。</p><div class="hp-grid">' + ''.join(time_card('tp-'+mode,mode) for mode in modes) + '</div><p><a href="standards.html#time-picker">查看分钟步进、双列提交与验收规则 →</a></p></section>'


def time_card(prefix, mode, hour=9, minute=30, minute_step=1):
    if type(hour) is not int or not 0 <= hour <= 23:
        raise ValueError('Hour must be an integer from 0 through 23')
    if type(minute_step) is not int or minute_step not in TIME_CONTRACT['minute']['allowed_steps']:
        raise ValueError('Unsupported minute step')
    if type(minute) is not int or not 0 <= minute <= 59 or minute % minute_step:
        raise ValueError('Minute must match the range and step; rounding is not allowed')
    prefix = escape(prefix, quote=True)
    mode_class = {'light':'', 'light_hc':'hc', 'dark':'dark', 'dark_hc':'dark hc'}[mode]
    label = {'light':'浅色', 'light_hc':'浅色 · 增强对比度', 'dark':'深色', 'dark_hc':'深色 · 增强对比度'}[mode]
    columns = ''
    for unit, title, value, values in [('time-hour','小时',hour,range(24)), ('minute','分钟',minute,range(0,60,minute_step))]:
        column_id = prefix + '-' + unit
        options = ''.join(f'<div class="hp-option" role="option" id="{column_id}-{n}" data-{unit}="{n}" data-value="{n}" aria-selected="{str(n == value).lower()}" aria-label="{n:02d} {title}">{n:02d}</div>' for n in values)
        columns += f'<div><span class="hp-column-label" id="{column_id}-label">{title}</span><div class="hp-frame"><div class="hp-band" aria-hidden="true"></div><div class="hp-wheel hp-time-wheel" data-unit="{unit}" role="listbox" tabindex="0" aria-labelledby="{prefix}-title {column_id}-label" aria-describedby="{prefix}-hint" aria-activedescendant="{column_id}-{value}">{options}</div></div></div>'
    return f'''<article class="hp-card {mode_class}" data-time-picker="{hour}" data-initial-minute="{minute}" data-time-mode="{mode}">
<p class="hp-mode">{label} · Sheet 内容示例</p><h3 id="{prefix}-title">选择提醒时间</h3>
<p class="hp-hint" id="{prefix}-hint">24 小时制 · 分钟步进 {minute_step} · 首尾循环。分别滚动两列，Tab 切换，↑ ↓ 调整，Home / End 到首尾。</p>
<p class="hp-value">已确认：<strong class="hp-saved">{hour:02d}:{minute:02d}</strong></p>
<div class="hp-columns">{columns}</div>
<div class="hp-actions"><button type="button" class="hp-cancel" disabled>取消</button><button type="button" class="hp-confirm" disabled>确认</button></div>
<p class="hp-result" role="status" aria-live="polite">交互演示需要 JavaScript；已确认值为 {hour:02d}:{minute:02d}。</p></article>'''


def standard():
    return '''<section id="hour-picker"><h2>小时滚动选择 · Hour wheel</h2>
<p>适用于预约、提醒等“一天中的小时”。默认 00–23、步进 1、支持首尾双向循环；新建时由业务提供默认值，编辑时回显已保存值，09:00 仅为样张。整点制需明确提示；若业务需要分钟，必须提供分钟选择，不得悄悄截断。</p>
<div class="kit-table-wrap"><table><tr><th>项目</th><th>统一规则</th></tr>
<tr><td>结构与尺寸</td><td>标题 → 说明 → 小时滚轮 → 取消/确认。项目视觉基准：5 个可见行位，中间行选中；行高至少 44pt，数字起点 22pt，单位 15pt，内容边距 16pt，按钮至少 44pt。字号增大时行高同步增长；空间不足减少邻行或采用原生替代样式，保留当前值和操作。此为本项目基准，不是 Apple 固定尺寸。</td></tr>
<tr><td>颜色与识别</td><td>surface 承载，fill 选中带，ink 选中文字，sub 邻行；accent-ui 标记、control-border 边线。选中同时通过中间位置、字重和边线识别；不降低邻行透明度来制造灰字。确认按钮使用 accent / on-accent，四种模式沿用语义 Token。</td></tr>
<tr><td>滚动、确认、取消</td><td>拖动、惯性停止后吸附最近整行，每列恰好一个草稿值。滚动时确认暂不可用；取消始终可用并恢复原值。确认后更新调用方；关闭、返回或下拉退出等同取消。非破坏性选择无需再次弹确认框。页面演示仅本地更新，不代表业务保存成功。</td></tr>
<tr><td>边界与不可用</td><td>00 的上一项为23，23的下一项为00，支持双向连续滚动；不自动切换日期。业务限制需显示有效范围及原因；停用候选不允许确认，跳到有效候选须让用户知晓。无可选项时以说明和恢复操作替代滚轮。加载或保存失败保留原值与草稿；保存中防止重复提交。</td></tr>
<tr><td>本地化与数据</td><td>产品支持 12 小时制时跟随用户偏好，使用 1–12 与上午/下午列，内部仍为整数 0–23：上午12=0、下午12=12。单位随语言变化。“持续 N 小时”须单独定义最小值、最大值、步进及是否允许0，不使用上午/下午；时刻与时长不能共用含义不明的 hour 字段。日期、时区、夏令时由具体业务另行处理。</td></tr>
<tr><td>可访问与原生实现</td><td>标签读出“提醒小时”，值读出“09时”，支持调整动作与键盘；确认、取消有明确名称。原生优先 SwiftUI Picker 的 wheel 样式或 UIPickerView；完整时间使用系统日期时间选择器。遵从系统排版、VoiceOver、减少动态效果与安全区，勿以 HTML 尺寸强制重绘原生滚轮。</td></tr>
</table></div><p>基础页展示浅色/浅色增强对比度；扩展页展示深色/深色增强对比度。HTML 交互涵盖 24 小时整点选择，12 小时制、受限候选、业务加载/保存与弹层焦点恢复是原生实现验收项。</p>
<p><a href="b-aizome.html#hour-picker">藍染浅色样张 →</a> · <a href="b-aizome-ext.html#hour-picker">藍染深色样张 →</a></p>
<p>实现依据：<a href="https://developer.apple.com/design/human-interface-guidelines/pickers">Apple Pickers</a> · <a href="https://developer.apple.com/documentation/swiftui/pickerstyle/wheel">SwiftUI wheel</a>。项目尺寸与提交规则为本规范的约定。</p></section>''' + time_standard()


def time_standard():
    return '''<section id="time-picker"><h2>小时＋分钟 · 双列时间选择</h2>
<p>用于提醒、预约等需要精确到分钟的时刻。小时列 00–23，分钟列 00–59，默认步进 1，回显完整 HH:mm。与上方仅小时选择并列提供，按业务精度选择；09:30 是样张初始值。</p>
<div class="kit-table-wrap"><table><tr><th>项目</th><th>统一规则</th></tr>
<tr><td>两列布局</td><td>左侧小时、右侧分钟，两列等宽，中间留 12pt；各列独立标签、同一条水平选中位置。沿用至少44pt行高、5行位和22pt数字基准；大字号同步撑高。单位在列上方固定展示，避免每行重复挤占空间。范围、间距为本项目约定。</td></tr>
<tr><td>分钟步进</td><td>常规为1分钟；业务可显式选5、10、15、30分钟，从00开始，最大值分别为55、50、45、30。不得生成60。已有值不匹配步进时保留原值并提示重新选择，或允许细粒度编辑；禁止自动取整。生成器拒绝不匹配的初始值。</td></tr>
<tr><td>双列状态与提交</td><td>各列分别吸附、分别操作；任意一列滚动未停稳时确认不可用。确认一次性提交小时和分钟；取消、关闭恢复完整原值，不能只恢复一列。分钟00的上一项为59，59的下一项为00，支持首尾双向循环；不自动进退小时或日期。页面演示确认只改变当前页面显示。</td></tr>
<tr><td>数据与可访问性</td><td>保存 hour(0–23) 与 minute(0–59) 两个整数，展示补零。不把HH:mm字符串当作日期、时区或绝对时间。每列有“提醒时间—小时/分钟”的独立名称和当前值，支持Tab、方向键、Home/End；读屏可调整两列。原生采用系统时间选择器并按实际业务精度验收。</td></tr>
</table></div><p>四种配色均沿用小时组件的颜色、确认/取消和大字号规则。12小时制、时区/夏令时、受限业务时段和原生弹层焦点恢复仍需在具体App实现；本次HTML提供24小时制双列演示。</p>
<p><a href="a-yohaku.html#time-picker">余白小时＋分钟样张 →</a> · <a href="a-yohaku-ext.html#time-picker">余白深色样张 →</a> · <a href="#hour-picker">仅小时标准 →</a></p></section>'''
