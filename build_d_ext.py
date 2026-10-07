# -*- coding: utf-8 -*-
"""
D · 紫硝子 MURASAKI GLASS —— 扩展篇生成器
==========================================
目标：让 D 的扩展篇覆盖度与 A/B/C 完全对齐（深色 / Sheet / 空态 / 引导 / 图表），
      同时保住 D 唯一的不同点 —— 控件层的 Liquid Glass 材质。

做法（不另造一套版式）：
  1) 复用 build_ext.build_ext_page(t) —— 五大块的 HTML 与规则文案与 A/B/C 同源，
     结构天然同构；配色靠 :root 注入 D 的浅色 Token、`.dark` 作用域注入 D 的深色 Token，
     于是所有组件自动染成群紫，无需改任何组件 markup。
  2) 追加 D 专属玻璃层：
     - ext 页组件名与基础页不同（.sheet / .toast / .banner / .backdrop），
       GLASS_CSS 的 .gnav/.gtab 管不到它们，必须单独约束；
     - 再补一组 .screen.dev 玻璃样机（浅色/深色），展示 regular 与 clear 两个变体。

踩过的坑（已规避）：
  * `.toast` 玻璃底若写 `var(--ink)`，在 `.dark` 作用域里 --ink 是浅色
    → 浅底 + 浅字直接不可读。改用 `var(--toast-bg)`，两套作用域各自正确。
  * GLASS_CSS 含大量字面 %（color-mix / saturate），只能用 replace 注入，禁用 % 格式化。
  * 所有注入的 SVG 必须过 scan_unsized_svg，否则重演「巨大加号撑爆容器」。

Run: python build_d_ext.py
"""
import logging
import os

import build_ext as be
from site_support import prepare_page
from build_d import (D, GLASS_CSS, L, L_VARS, MIN, STRIVE, gscreen, hc_css,
                     ratio, scan_unsized_svg, vars_css)

OUT = os.path.dirname(os.path.abspath(__file__))
log = logging.getLogger("build_d_ext")
if not log.handlers:                      # 显式绑定，避免被上层 basicConfig 劫持
    log.setLevel(logging.INFO)
    log.propagate = False
    _fh = logging.FileHandler(os.path.join(OUT, "build_d_ext.log"), encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _sh = logging.StreamHandler()
    _sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(_fh)
    log.addHandler(_sh)

OUT_FILE = "d-murasaki-ext.html"

# ------------------------------------------------- 注入 D 的深色 Token 组 ----
# build_ext_page 通过 DARK[letter] 生成 .dark 作用域变量，通过 DARK_SWATCH[letter]
# 生成规则区的色板小样。D 的深色 Token 已由 build_d.derive() 求解完毕（含 on_*），
# 这里只补齐 ext 页额外用到、而 build_d 未定义的三个键。
_DARK_D = {k: v for k, v in D.items() if not k.startswith("hc_")}
_DARK_D.update(
    elev="#443E4E",          # 浮起层：比 fill_strong #3B3644 再高一档，维持三级 elevation
    toast_bg="#443E4E",
    toast_fg="#ECE8F0",
)
be.DARK["D"] = _DARK_D
be.DARK_SWATCH["D"] = [("紫墨", _DARK_D["bg"]), ("面", _DARK_D["surface"]),
                       ("浮", _DARK_D["elev"]), ("字", _DARK_D["ink"]),
                       ("群紫+", _DARK_D["accent"]), ("线", _DARK_D["line_strong"])]

# D 不在 contrast_patch.json 内（该文件只含 A/B/C），HC 值由 build_d.derive()
# 求解后放在 L/D 的 hc_* 键里，经 hc_css() 转成变量串交给扩展篇装配器。
THEME_D = dict(letter="D", file="d-murasaki.html", jp="紫硝子",
               romaji="MURASAKI GLASS", tagline="玻璃外壳与群紫内核",
               kanji="紫", vars=L_VARS,
               hc_light=hc_css(L), hc_dark=hc_css(D))

# ------------------------------------------------------ D 专属玻璃层 CSS ----
# 注意：这些选择器针对 ext 页自己的组件类名，且一律加 .dglass 前缀限定作用域，
# 避免污染 A/B/C（它们不会带这个 body class）。
EXT_GLASS_CSS = """
/* ===== D 拡張篇 · 控件层玻璃化 ===== */
/* Sheet：HIG 的 sheet 允许玻璃材质；圆角与抓手尺寸沿用 A/B/C 规则，只换材质 */
.dglass .sheet{
  background:color-mix(in srgb, var(--surface) 82%, transparent);
  backdrop-filter:blur(30px) saturate(180%);
  -webkit-backdrop-filter:blur(30px) saturate(180%);
  border-top:1px solid color-mix(in srgb, var(--line-strong) 70%, transparent);
  box-shadow:0 -14px 44px rgba(26,24,30,.16);
}
.dglass .sheet.full{border-top:0;box-shadow:0 -8px 30px rgba(26,24,30,.10)}
/* Toast / Banner：底色必须取 --toast-bg 而非 --ink，
   因为 .dark 作用域下 --ink 是浅色，用错会得到浅底+浅字 */
.dglass .toast{
  background:color-mix(in srgb, var(--toast-bg) 88%, transparent);
  backdrop-filter:blur(20px) saturate(160%);
  -webkit-backdrop-filter:blur(20px) saturate(160%);
}
.dglass .banner{
  background:color-mix(in srgb, var(--surface) 76%, transparent);
  backdrop-filter:blur(24px) saturate(180%);
  -webkit-backdrop-filter:blur(24px) saturate(180%);
}
.dglass .backdrop{background:rgba(26,24,30,.42)}
/* 玻璃样机：ext 页三栏布局，812 高即可，无需覆盖 GLASS_CSS 的 .screen.dev */
.dglass .gspec{position:relative}
"""

GLASS_NOTES = """
<div class="notes">
  <h3>玻璃层规则 <span class="en">Liquid Glass</span></h3>
  <h4>用在哪 / 不用在哪</h4>
  <ul>
    <li><b>只用于控件与导航层</b>：导航栏、Tab 栏、Sheet、Toast、浮动按钮</li>
    <li><b>内容层一律不用玻璃</b>：卡片、列表、表单、图表保留纸感实底。
        玻璃叠在文字下会持续干扰阅读，HIG 也不建议把玻璃当容器背景</li>
  </ul>
  <h4>两个变体（HIG）</h4>
  <ul>
    <li><code>regular</code>：默认，模糊 + 饱和提升，内容在其下滚动时保持可读</li>
    <li><code>clear</code>：更透明、模糊更弱，<b>只用于需要强调下层内容的场合</b>，
        不可用于承载正文的常态导航</li>
  </ul>
  <h4>硬性约束</h4>
  <ul>
    <li>Tab 栏<b>不放动作键</b>（HIG 明确）；加号等动作留在导航栏或内容区</li>
    <li>玻璃下方必须有真实内容穿过，否则材质无从体现 —— 故列表按 edge-to-edge 滚动</li>
    <li>深色下玻璃底色改取提亮后的 surface，透明度不变，避免发灰</li>
  </ul>
</div>
"""


def glass_spec(dark):
    """一台 D 玻璃样机。复用已验证的 gscreen()，不新写 markup。"""
    return ('<div class="screen dev gspec">%s</div>'
            % gscreen(dark=dark, n_events=7))


def build_glass_section():
    cols = ""
    for no, en, cn, dark in (("G1", "Glass Light", "玻璃 · 浅色", False),
                             ("G2", "Glass Dark", "玻璃 · 深色", True)):
        cols += ('<div class="col"><div class="col-tag"><span class="no">%s</span>'
                 '<span class="en">%s</span><span class="cn">%s</span></div>%s</div>'
                 % (no, en, cn, glass_spec(dark)))
    cols += ('<div class="col" style="width:auto;flex:1"><div class="col-tag">'
             '<span class="no">G3</span><span class="en">Rules</span>'
             '<span class="cn">规则</span></div>%s</div>' % GLASS_NOTES)
    return ('<div class="sec-tag"><h2>玻璃层与变体</h2>'
            '<span class="en">Liquid Glass — Regular / Clear</span></div>'
            '<div class="cols">%s</div>' % cols)


def main():
    page = be.build_ext_page(THEME_D)

    # --- 注入 body class + 玻璃 CSS ---
    if "<body>" not in page:
        raise SystemExit("未找到 <body>，无法注入 dglass 作用域")
    page = page.replace("<body>", '<body class="dglass">', 1)

    glass = (GLASS_CSS.replace("%(DARKVARS)s", vars_css(D))
                      .replace("%(HCVARS)s", hc_css(L)))
    page = page.replace("</head>",
                        "<style>%s\n%s</style>\n</head>" % (glass, EXT_GLASS_CSS), 1)

    # --- 在「空状态」之前插入 D 专属玻璃层区块 ---
    anchor = '<div class="sec-tag"><h2>空状态</h2>'
    if anchor not in page:
        raise SystemExit("未找到空状态锚点，插入位置失效")
    section = build_glass_section()
    page = page.replace(anchor, section + anchor, 1)

    page = prepare_page(page, OUT_FILE, THEME_D)
    path = os.path.join(OUT, OUT_FILE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    log.info("written %s (%.1f KB)", OUT_FILE, os.path.getsize(path) / 1024)

    # --- 自检 1：无约束 SVG（巨大加号的根因防线）---
    bad = scan_unsized_svg(section)
    if bad:
        log.error("玻璃区块存在未被 CSS 约束尺寸的 svg 容器: %s", bad)
        raise SystemExit(1)
    log.info("SVG SIZE SELF-CHECK OK (0 unsized containers)")

    # --- 自检 2：对比度硬门槛（浅 / 深）---
    fails = []
    for name, p in (("LIGHT", L), ("DARK", _DARK_D)):
        for tok, tgt in (("sub", STRIVE), ("faint", MIN)):
            r = min(ratio(p[tok], b) for b in (p["bg"], p["surface"]))
            if r < tgt - 0.01:
                fails.append("%s %s=%.2f<%.2f" % (name, tok, r, tgt))
        for base in ("accent", "danger", "stamp"):
            r = ratio(p["on_" + base], p[base])
            if r < 4.5:
                fails.append("%s on_%s=%.2f" % (name, base, r))
        log.info("%s: sub=%.2f faint=%.2f on-accent=%.2f", name,
                 ratio(p["sub"], p["bg"]), ratio(p["faint"], p["bg"]),
                 ratio(p["on_accent"], p["accent"]))
    if fails:
        log.error("对比度未达标: %s", fails)
        raise SystemExit(1)
    log.info("CONTRAST SELF-CHECK OK (0 fails)")

    # --- 自检 3：五大块齐全 ---
    need = ["深色模式 · 墨", "Sheet 弹层", "空状态", "引导页", "图表", "玻璃层与变体"]
    missing = [s for s in need if s not in page]
    if missing:
        log.error("缺章节: %s", missing)
        raise SystemExit(1)
    log.info("SECTIONS OK (%d 章: %s)", len(need), " / ".join(need))


if __name__ == "__main__":
    main()
