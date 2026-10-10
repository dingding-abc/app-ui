# -*- coding: utf-8 -*-
"""
D · 紫硝子 MURASAKI GLASS —— 生成器（v3：换色系为群紫）

v3 变更（本轮）：
  原「墨硝子」的 accent 直接沿用方向 A 的焦茶 #8A6248、底色也几乎同款，
  作为第四个并行方向缺乏独立辨识度（等于「A 加了层玻璃」）。
  改为传统「群紫」#6B4A7A —— A/B/C 已占用焦茶(暖棕橙)/藍(蓝)/松葉(绿)，
  紫是色相上唯一未占用的区间。同时把次级色 tone2/tone3 的暖棕换成薊(mauve-rose)/灰藍，
  避免日程卡竖条把 A 的焦茶从侧门带回来。
  文件随之更名 d-sumiglass.html -> d-murasaki.html。

v2 修正的三个问题：
  1) index.html 缺 D 入口      -> 已永久写入 build_ext.py 的 build_index_v2()
  2) D 页格式与前三套不一致    -> 改为复用 build.py 的 CSS / HEADER_TPL / PAGE_TPL / BODY
  3) 巨大加号 / 超宽导航栏     -> 根因：图标 SVG 只有 viewBox 无 width/height，
                                  全靠成对 CSS 规则约束；v1 漏写 -> 退化为默认 300x150 撑爆容器。
                                  v2 起所有新类名显式声明 svg 尺寸，并有构建期自检兜底。

设计依据：Apple HIG（见 knowledge/concepts/ios26-liquid-glass-hig.md）
Run: python build_d.py
"""
import logging
import os
import re

from build import (CSS as BASE_CSS, HEADER_TPL, PAGE_TPL, BODY as BASE_BODY,
                   STATUSBAR, ICONS, cal_grid, design_notes)

OUT = os.path.dirname(os.path.abspath(__file__))
log = logging.getLogger("build_d")
if not log.handlers:                      # 显式绑定，避免被上层 basicConfig 劫持
    log.setLevel(logging.INFO)
    log.propagate = False
    _fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    _fh = logging.FileHandler(os.path.join(OUT, "build_d.log"), encoding="utf-8")
    _fh.setFormatter(_fmt)
    _sh = logging.StreamHandler()
    _sh.setFormatter(_fmt)
    log.addHandler(_fh)
    log.addHandler(_sh)

# ------------------------------------------------------------ color utils --
import colorsys
from design_tokens import finish_palette, hc_css as semantic_hc_css, luminance
from site_support import prepare_page

MIN, STRIVE = 4.6, 7.0


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(r, g, b):
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def hsl(hx):
    r, g, b = [c / 255 for c in _rgb(hx)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def from_hsl(h, s, l):
    return _hex(*colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), s))


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(hx):
    r, g, b = _rgb(hx)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def nudge(base, bgs, target, darker):
    """只调明度 L、锁定 H/S —— 达标同时保住色相气质（禁止写死色值）"""
    h, s, l = hsl(base)
    for _ in range(600):
        c = from_hsl(h, s, l)
        if all(ratio(c, b) >= target for b in bgs):
            return c
        l += -0.004 if darker else 0.004
        if l <= 0 or l >= 1:
            break
    return None


# ------------------------------------------------------------ D2 palette --
L_BASE = dict(
    page_bg="#E4E0EA", bg="#F6F4F8", surface="#FCFBFD", fill="#EDE9F2",
    fill_strong="#DCD5E4", ink="#221F28", sub_seed="#6A6472", faint_seed="#97919E",
    line="#E6E1EC", line_strong="#D3CADC",
    accent="#6B4A7A", accent_deep="#563963", accent_soft="#EFE8F3",
    danger="#B4493A", danger_soft="#F6EDE8", stamp="#C14436",
    sun="#C25B4E", sat="#5E7A99",
    # 次级色改为同族冷调：薊(mauve-rose) / 灰藍(blue-gray)。
    # 刻意不用暖棕 —— 否则日程卡竖条会把方向 A 的焦茶从侧门带回来。
    tone2="#9A6B86", soft2="#F2E9EE",
    tone3="#4E6A86", soft3="#E6ECF2",
)
D_BASE = dict(
    page_bg="#100F13", bg="#1A181E", surface="#24212A", fill="#2D2935",
    fill_strong="#3B3644", ink="#ECE8F0", sub_seed="#B3ABC0", faint_seed="#8E8698",
    line="#332F3B", line_strong="#47424F",
    accent="#B79BC6", accent_deep="#CDB6D8", accent_soft="#2E2836",
    danger="#D0705F", danger_soft="#2F1F1C", stamp="#D56055",
    sun="#E08573", sat="#8CA8C9",
    tone2="#C79AB0", soft2="#3A2A33",
    tone3="#93A5B3", soft3="#2A313A",
)
RADII = dict(r_card="12px", r_in="9px")


def derive(base, is_light):
    return finish_palette(base, is_light)


L = derive(L_BASE, True)
D = derive(D_BASE, False)
L_VARS = dict(L, **RADII)


def vars_css(p, skip=("hc_",)):
    return ";".join("--%s:%s" % (k.replace("_", "-"), v)
                    for k, v in p.items() if not k.startswith(skip))


def hc_css(p):
    return semantic_hc_css(p, luminance(p["bg"]) > .5)


# ------------------------------------------------- filled tab icons (HIG) --
def _f(d):
    return ('<svg viewBox="0 0 24 24" fill="currentColor" stroke="none">'
            '<path d="%s"/></svg>' % d)


FILLED = dict(
    HOME=_f("M11.1 2.7a1.5 1.5 0 0 1 1.8 0l8.3 6.4c.5.4.8 1 .8 1.6v9.1a1.8 1.8 0 0 1-1.8 1.8h-4.9a1.4 1.4 0 0 1-1.4-1.4v-5.1h-3.8v5.1a1.4 1.4 0 0 1-1.4 1.4H3.8A1.8 1.8 0 0 1 2 19.8v-9.1c0-.6.3-1.2.8-1.6z"),
    NOTE=_f("M5.6 2.6h8.2a1.4 1.4 0 0 1 1 .4l5 5c.3.3.4.6.4 1v11a1.8 1.8 0 0 1-1.8 1.8H5.6a1.8 1.8 0 0 1-1.8-1.8V4.4a1.8 1.8 0 0 1 1.8-1.8zm8.2 2.2v3.8h3.8zM7.6 12.6h8.8v1.9H7.6zm0 4.2h6v1.9h-6z"),
    CAL=_f("M6.2 2.6a1.2 1.2 0 0 1 1.2 1.2v.6h2.2v-.6a1.2 1.2 0 0 1 2.4 0v.6h1.6v-.6a1.2 1.2 0 0 1 2.4 0v.6h.4a2.2 2.2 0 0 1 2.2 2.2v11.2a2.2 2.2 0 0 1-2.2 2.2H5.8a2.2 2.2 0 0 1-2.2-2.2V6.6a2.2 2.2 0 0 1 2.2-2.2h.4v-.6a1.2 1.2 0 0 1 1.2-1.2zM5.6 10v10.2h12.8V10zm3 2.8h2.2v2.2H8.6zm4.8 0h2.2v2.2h-2.2zM8.6 15.8h2.2V18H8.6zm4.8 0h2.2V18h-2.2z"),
    SEARCH=_f("M10.8 2.4a8.4 8.4 0 0 1 6.7 13.5l4 4a1.4 1.4 0 0 1-2 2l-4-4A8.4 8.4 0 1 1 10.8 2.4zm0 3a5.4 5.4 0 1 0 0 10.8 5.4 5.4 0 0 0 0-10.8z"),
    USER=_f("M12 2.4a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 11.6c4.9 0 8.9 3.1 8.9 7v1.2a1.2 1.2 0 0 1-1.2 1.2H4.3a1.2 1.2 0 0 1-1.2-1.2v-1.2c0-3.9 4-7 8.9-7z"),
)

# ------------------------------------------------------- glass extension ---
# 所有新增类名一律显式声明 svg 尺寸，杜绝 v1 的「裸 SVG 撑爆容器」问题
GLASS_CSS = r"""
/* ===== D 紫硝子 MURASAKI GLASS · iOS 26 Liquid Glass 扩展层 ===== */

/* 玻璃屏专用：A/B/C 的 .screen 靠内容撑高且无定位上下文，
   玻璃层需要固定设备高度 + position:relative 才能正确挂靠 */
.screen.dev{position:relative;height:812px;padding-bottom:0}

/* 玻璃控件层：regular 变体（模糊 + 提亮），仅用于导航/Tab 栏 */
.glass{background:color-mix(in srgb,var(--bg) 68%,transparent);
  backdrop-filter:blur(26px) saturate(180%);-webkit-backdrop-filter:blur(26px) saturate(180%)}
/* clear 变体：只允许用于富内容之上（HIG 规定） */
.glass-clear{background:rgba(255,255,255,.22);
  backdrop-filter:blur(14px) saturate(160%);-webkit-backdrop-filter:blur(14px) saturate(160%);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 2px 10px rgba(0,0,0,.16)}

/* 玻璃导航栏：紧贴状态栏（.statusbar 实际高 46px）下方 */
.gnav{position:relative;z-index:30;padding:8px 16px 12px;
  border-bottom:1px solid color-mix(in srgb,var(--ink) 9%,transparent)}
.gnav .gt{font-size:calc(27px * var(--dt-scale,1));font-weight:700;letter-spacing:.05em;line-height:1.15;color:var(--ink)}
.gnav .gs{font-size:calc(11px * var(--dt-scale,1));letter-spacing:.16em;color:var(--sub);margin-top:2px}
.gnav .gact{position:absolute;right:16px;top:8px;width:44px;height:44px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;color:var(--sub);
  background:color-mix(in srgb,var(--ink) 7%,transparent)}
.gnav .gact svg{width:17px;height:17px}          /* ← v1 缺失导致巨大加号 */

/* 浮起胶囊 Tab 栏（真机安全区与 home indicator 的核算见 devices.html） */
.gtab{position:relative;margin:8px 16px 24px;z-index:30;min-height:54px;height:auto;flex:none;
  border-radius:var(--r-btn);display:flex;align-items:stretch;padding:4px;
  background:color-mix(in srgb,var(--bg) 70%,transparent);
  backdrop-filter:blur(26px) saturate(180%);-webkit-backdrop-filter:blur(26px) saturate(180%);
  box-shadow:0 10px 28px rgba(30,24,14,.17),inset 0 1px 0 rgba(255,255,255,.55)}
.gtab .ti{flex:1;min-height:44px;display:flex;flex-direction:column;align-items:center;
  gap:4px;justify-content:center;font-size:calc(var(--type-caption) * var(--dt-scale,1));letter-spacing:.04em;color:var(--faint);min-width:0;overflow-wrap:anywhere}
.gtab .ti svg{width:22px;height:22px}
.gtab .ti.on{color:var(--accent-text)}
.gtab .ti .dot{width:4px;height:4px;border-radius:2px}
.gtab .ti.on .dot{background:var(--accent)}

/* 内容层（和纸卡，HIG 允许内容层用实色） */
.gscroll{position:relative;flex:1;min-height:0;overflow-y:auto;padding-bottom:16px}
.gcard{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-card)}
.ghero{margin:16px 16px 12px;min-height:120px;height:auto;border-radius:var(--r-card);position:relative;
  overflow:hidden;background:linear-gradient(135deg,#E4B37C 0%,#D08C68 36%,#8B6E96 72%,#5A6DA4 100%)}
.ghero .sun{position:absolute;right:26px;top:22px;width:42px;height:42px;border-radius:50%;
  background:rgba(255,244,220,.92);box-shadow:0 0 26px rgba(255,238,200,.7)}
.ghero .tx{position:absolute;left:18px;bottom:13px;color:#fff}
.ghero .tx b{display:block;font-size:calc(19px * var(--dt-scale,1));font-weight:700;letter-spacing:.06em;
  text-shadow:0 1px 8px rgba(0,0,0,.3)}
.ghero .tx span{display:block;font-size:calc(11px * var(--dt-scale,1));opacity:.94;margin-top:3px;letter-spacing:.08em;
  text-shadow:0 1px 6px rgba(0,0,0,.32)}
.ghero .pill{position:absolute;right:12px;bottom:11px;height:28px;padding:0 12px;border-radius:8px;
  display:flex;align-items:center;gap:6px;font-size:calc(11px * var(--dt-scale,1));font-weight:600;color:#fff}
.ghero .pill svg{width:12px;height:12px}

.gev{display:flex;gap:11px;margin:0 16px 9px;padding:13px 14px;align-items:flex-start}
.gev .bar{width:3px;align-self:stretch;border-radius:2px;flex:none;background:var(--accent)}
.gev.t2 .bar{background:var(--tone2)}
.gev.t3 .bar{background:var(--tone3)}
.gev .tm{font-size:calc(10px * var(--dt-scale,1));color:var(--faint);width:42px;flex:none;line-height:1.55}
.gev .tm b{display:block;font-size:calc(13.5px * var(--dt-scale,1));font-weight:700;color:var(--ink)}
.gev h5{font-size:calc(13.5px * var(--dt-scale,1));font-weight:600;letter-spacing:.03em;color:var(--ink)}
.gev p{font-size:calc(10.5px * var(--dt-scale,1));color:var(--faint);margin-top:3px;letter-spacing:.04em}
.gnote{margin:12px 16px 0;padding:15px 16px;display:flex;gap:14px;align-items:center;
  background:var(--fill);border:1px solid var(--line);border-radius:var(--r-card)}
.gnote .t{writing-mode:vertical-rl;font-size:calc(12.5px * var(--dt-scale,1));letter-spacing:.24em;line-height:1.9;color:var(--sub)}
.gnote .k{font-size:calc(9px * var(--dt-scale,1));letter-spacing:.2em;color:var(--faint);flex:1}
.gcta{margin:14px 16px 0}
.gbtn{height:50px;display:flex;align-items:center;justify-content:center;gap:8px;
  font-size:calc(15px * var(--dt-scale,1));font-weight:600;letter-spacing:.06em;border:none;cursor:pointer}
.gbtn svg{width:15px;height:15px}                /* ← v1 缺失 */
.gbtn.cap{border-radius:var(--r-btn)}
.gbtn.rect{border-radius:var(--r-btn)}
.gbtn.primary{background:var(--accent);color:var(--on-accent);
  box-shadow:0 3px 10px color-mix(in srgb,var(--accent) 26%,transparent)}

/* 深色（.dark 语义与 A/B/C ext 一致） */
.dark{%(DARKVARS)s}
.dark .gtab{box-shadow:0 10px 28px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.09)}
.dark .glass-clear{background:rgba(255,255,255,.16)}

/* increased contrast 变体不在此处：必须位于 :root{VARS} 之后才不被覆盖，
   故由 main() 通过 PAGE_TPL 的 $A11Y 占位符注入（见 a11y_block）。 */

/* D 专属说明块 */
.dnote{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-card);
  padding:16px 18px;margin-top:14px}
.dnote h4{font-size:calc(13px * var(--dt-scale,1));font-weight:700;letter-spacing:.05em;margin-bottom:9px;color:var(--ink)}
.dnote h4 span{font-size:calc(9.5px * var(--dt-scale,1));letter-spacing:.18em;color:var(--faint);margin-left:8px;font-weight:600}
.dnote p{font-size:calc(12px * var(--dt-scale,1));line-height:1.95;color:var(--sub)}
.dnote p b{color:var(--ink);font-weight:600}
.dnote code{font-family:ui-monospace,Consolas,monospace;font-size:calc(11px * var(--dt-scale,1));
  background:var(--fill);padding:1px 5px;border-radius:4px;color:var(--ink)}
.dnote .ok{color:#4E7A55;font-weight:700}
.dnote .no{color:var(--danger);font-weight:700}
.dgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}
"""


# ------------------------------------------------------- glass demo block --
def gscreen(dark=False, cta=True, n_events=7):
    # 7 条日程：内容总高须越过浮动 Tab 栏顶边，玻璃才有真实内容可折射（edge-to-edge）
    ev = [("09:30", "30分", "朝の打ち合わせ", "会議室 A · 3名", ""),
          ("11:00", "1時間", "デザインレビュー", "オンライン", "t2"),
          ("14:20", "45分", "資料の整理", "自席 · 集中", "t3"),
          ("16:00", "20分", "夕方の散歩", "近所 · ひとり", "t2"),
          ("19:30", "1時間", "読書", "居間 · 静かに", "t3"),
          ("21:00", "15分", "明日の準備", "書斎", ""),
          ("22:30", "30分", "就寝前の記録", "寝室 · 静かに", "t2")][:n_events]
    evs = "".join('<div class="gev gcard %s"><div class="bar"></div>'
                  '<div class="tm"><b>%s</b>%s</div>'
                  '<div><h5>%s</h5><p>%s</p></div></div>' % (c, t, d, h, p)
                  for t, d, h, p, c in ev)
    tabs = [("朝", "HOME"), ("記録", "NOTE"), ("暦", "CAL"), ("探索", "SEARCH"), ("私", "USER")]
    tabhtml = "".join('<div class="ti%s">%s<span>%s</span><span class="dot"></span></div>'
                      % (" on" if i == 0 else "", FILLED[k], jp)
                      for i, (jp, k) in enumerate(tabs))
    return (
        STATUSBAR.replace("{WIFI}", ICONS["WIFI"])
        + '<div class="gnav glass"><div class="gt">朝</div>'
          '<div class="gs">9月17日 木曜 · ASA</div>'
          '<div class="gact">' + ICONS["PLUS"] + '</div></div>'
        + '<div class="gscroll">'
          '<div class="ghero"><div class="sun"></div>'
          '<div class="tx"><b>晴れ · 24°</b><span>東京 · 紫外線 やや強い</span></div>'
          '<div class="pill glass-clear">' + ICONS["INFO"] + '24°</div></div>'
        + evs
        + '<div class="gnote"><div class="t">朝の光</div>'
          '<div class="k">TODAY’S NOTE — 静けさや岩にしみ入る蝉の声</div></div>'
        + ('<div class="gcta"><div class="gbtn cap primary">' + ICONS["PLUS"]
           + '新しい予定</div></div>' if cta else '')
        + '</div>'
        + '<div class="gtab">' + tabhtml + '</div>'
    )


def col(no, en, cn, inner, dark=False, dev=False):
    """与 build.py 完全同构的 .col / .col-tag / .screen 结构
    dev=True 时附加 .dev：给玻璃层提供固定设备高度与定位上下文"""
    cls = (" dark" if dark else "") + (" dev" if dev else "")
    return ('<div class="col">'
            '<div class="col-tag"><span class="no">%s</span><span class="en">%s</span>'
            '<span class="cn">%s</span></div>'
            '<div class="screen%s">%s</div></div>'
            % (no, en, cn, cls, inner))


def sec_tag(jp, en):
    return '<div class="sec-tag"><h2>%s</h2><span class="en">%s</span></div>' % (jp, en)


D_EXTRA = (
    sec_tag("玻璃导航示意", "Material Preview · 375 pt")
    + '<div class="cols">'
    + col("01", "Glass Shell · Light", "玻璃外壳 · 浅色", gscreen(), dev=True)
    + col("02", "Glass Shell · Dark", "玻璃外壳 · 深色", gscreen(dark=True), dark=True, dev=True)
    + '<div class="col"><div class="dnote"><h4>材质与原生实现</h4>'
      '<p>群紫是主题配色，玻璃是导航与控件层的材质选项。其他主题也可采用玻璃，内容卡片继续使用实色。</p>'
      '<p>HTML 的模糊与透明度只模拟外观，不代表原生 Liquid Glass 的折射、动态效果或系统适配已完成。</p>'
      '<p>Tab 只负责导航；创建动作位于内容或工具栏。原生 Tab 可以使用 SF Symbols 填充变体。</p>'
      '<p>安全区、栏高和系统偏好由原生框架读取。颜色覆盖浅色、深色与各自的增强对比度；透明背景仍需实际合成检验。</p>'
      '<p>明暗默认跟随系统，产品确有需要时可提供覆盖设置。减少动态效果和降低透明度必须有回退。</p>'
      '<p>本机框是参考样张。设备矩阵见设备尺寸页；真机、大字号与 VoiceOver 为独立待验项目。</p>'
      '</div></div></div>'
)

# D 页正文 = A/B/C 同构的组件样例（复用 build.py 的 BODY，格式天然统一）+ D 专属玻璃层区块
D_BODY = D_EXTRA + BASE_BODY.replace("__STATUSBAR__", STATUSBAR).replace("__CALGRID__", cal_grid())

THEME = dict(
    file="d-murasaki.html", letter="D", jp="紫硝子", romaji="MURASAKI GLASS",
    cn_short="群紫 · 玻璃示意", material="glass",
    tagline="玻璃外壳与群紫内核",
    desc=("群紫色主题搭配导航玻璃示意；内容保持纸感与清晰层次。"
          "配色与材质分别定义，其他主题也可采用系统玻璃。原生效果需在 iOS 工程中验证。"),
    keywords=["硝子", "群紫", "iOS 26"],
    kanji="紫",
    swatches=[("薄紫", "#F6F4F8"), ("紙白", "#FCFBFD"), ("墨紫", "#1A181E"),
              ("群紫", "#6B4A7A"), ("臙脂", "#B4493A"), ("藤", "#EFE8F3")],
    radii="卡片 12 / 按钮 胶囊 / 输入 9",
    vars=L_VARS,
)


# --------------------------------------------------------------- selftest --
def scan_unsized_svg(html):
    """v1 的根因防线：任何 svg 都必须被某条 CSS 规则约束尺寸，否则默认尺寸会撑爆容器。
    这里检查每个含 <svg 的类名，是否在 CSS 里有对应的 svg 尺寸规则。"""
    css = GLASS_CSS + BASE_CSS
    sized = set()
    for m in re.finditer(r'([^{}]+?)\s+svg\s*\{[^}]*width\s*:', css):
        # 收集整条选择器里出现的所有类名（含祖先），
        # 例如 `.toast .ic svg{width:10px}` 同时覆盖 toast 与 ic
        for sel in m.group(1).split(","):
            sized.update(re.findall(r'\.([\w-]+)', sel))
    bad = []
    # D 自定义区块里用到的 svg 容器类
    for cls in ("gact", "ti", "gbtn", "pill", "ibtn", "tab", "toast", "bi"):
        if cls not in sized and ('class="%s"' % cls) in html:
            bad.append(cls)
    return bad


def main():
    header = HEADER_TPL.substitute(
        KANJI=THEME["kanji"], LETTER=THEME["letter"], JP=THEME["jp"],
        ROMAJI=THEME["romaji"], TAGLINE=THEME["tagline"], CN_SHORT=THEME["cn_short"],
        DESC=THEME["desc"], KW="".join("<span>%s</span>" % k for k in THEME["keywords"]),
        SW="".join('<div class="sw"><div class="dot" style="background:%s"></div>'
                   '<div class="nm">%s</div><div class="hx">%s</div></div>' % (c, n, c)
                   for n, c in THEME["swatches"]),
        RADII=THEME["radii"],
    )
    # 注意：GLASS_CSS 含大量字面 %（color-mix 68% / saturate 180% 等），
    # 不能用 % 格式化，否则 "unsupported format character"。用 replace 精确注入。
    glass = GLASS_CSS.replace("%(DARKVARS)s", vars_css(D))
    # HC 必须位于 :root{VARS} 之后，否则同特异性下被后者覆盖（A/B/C 基础篇曾因此失效）。
    # 结构对齐 build_ext.a11y_css_ext：手动类 + 系统偏好自动激活，浅/深各一套。
    a11y = (":root{--dt-scale:1}\n"
            ".hc{" + hc_css(L) + "}\n"
            ".dark.hc{" + hc_css(D) + "}\n"
            ".dark .hc{" + hc_css(D) + "}\n"
            "@media (prefers-contrast: more){\n"
            "  :root{" + hc_css(L) + "}\n"
            "  .dark{" + hc_css(D) + "}\n"
            "}\n")
    body = D_BODY.format(**ICONS).replace('__DESIGN_NOTES__', design_notes(THEME))
    page = PAGE_TPL.substitute(
        TITLE="%s %s — 日式简约 iOS UI 方向 %s（iOS 26 Liquid Glass）"
              % (THEME["jp"], THEME["romaji"], THEME["letter"]),
        CSS=BASE_CSS + "\n" + glass, A11Y=a11y,
        VARS=vars_css(L_VARS), HEADER=header, BODY=body,
        LETTER=THEME["letter"], JP=THEME["jp"], ROMAJI=THEME["romaji"],
    )
    page = prepare_page(page, THEME["file"], THEME)
    path = os.path.join(OUT, THEME["file"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    log.info("written %s (%.1f KB)", THEME["file"], os.path.getsize(path) / 1024)

    # --- 自检 1：无约束 SVG（v1 巨大加号的根因）---
    bad = scan_unsized_svg(body)
    if bad:
        log.error("存在未被 CSS 约束尺寸的 svg 容器: %s", bad)
        raise SystemExit(1)
    log.info("SVG SIZE SELF-CHECK OK (0 unsized containers)")

    # --- 自检 2：对比度硬门槛 ---
    fails = []
    for name, p, light in (("LIGHT", L, True), ("DARK", D, False)):
        bgs = [p["bg"], p["surface"]]
        for tok, tgt in (("sub", STRIVE), ("faint", MIN)):
            r = min(ratio(p[tok], b) for b in bgs)
            if r < 4.5:
                fails.append("%s %s=%.2f" % (name, tok, r))
        for base in ("accent", "danger", "stamp"):
            if ratio(p["on_" + base], p[base]) < 4.5:
                fails.append("%s on_%s=%.2f" % (name, base, ratio(p["on_" + base], p[base])))
        log.info("%s: sub=%.2f faint=%.2f on-accent=%.2f", name,
                 ratio(p["sub"], p["bg"]), ratio(p["faint"], p["bg"]),
                 ratio(p["on_accent"], p["accent"]))
    if fails:
        log.error("对比度未达标: %s", fails)
        raise SystemExit(1)
    log.info("CONTRAST SELF-CHECK OK (0 fails)")


if __name__ == "__main__":
    main()
