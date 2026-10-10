# -*- coding: utf-8 -*-
"""
JP Minimal UI Kit - iOS design direction samples generator
Generates: a-yohaku.html / b-aizome.html / c-wakatake.html / index.html
Run: python build.py
"""
import logging
import os
from html import escape
from string import Template

OUT = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(OUT, "build.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("build")

# ----------------------------------------------------- color utils (shared) --
# 四套方向（A/B/C/D）共用同一套对比度求解器。
# 规则：只调 HSL 的明度 L、锁定色相 H 与饱和度 S —— 达标同时保住配色气质。
#       禁止写死 on_accent / sub / faint 等色值，一律由 derive() 推导。
import colorsys
from design_tokens import finish_palette, hc_css as semantic_hc_css
from theme_registry import load_custom
from site_support import prepare_page

MIN, STRIVE = 4.6, 7.0          # MIN=HIG 底线 4.5:1 取 4.6；STRIVE=小字力争 7:1


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


def derive(base, is_light):
    return finish_palette(base, is_light)


# ---------------------------------------------------------------- themes ----
THEMES = [
    dict(
        file="a-yohaku.html", letter="A", jp="余白", romaji="YOHAKU",
        cn_short="暖纸 · MUJI 风",
        tagline="MUJI 式的未晒白纸面",
        desc="以生成和纸般的暖白余白为底，焦茶作主色、柿子色只在警示处点睛。克制、素朴、有温度，适合生活方式 / 手帐笔记 / 电商类 App。",
        keywords=["素朴", "温度", "触感"],
        kanji="余",
        swatches=[("生成り", "#F6F3ED"), ("白", "#FDFCFA"), ("墨", "#26251F"),
                  ("焦茶", "#8A6248"), ("柿", "#B4493A"), ("砂", "#E7E2D7")],
        radii="卡片 14 / 按钮 胶囊 / 输入 9",
        vars=dict(
            page_bg="#EAE5DC", bg="#F6F3ED", surface="#FDFCFA", fill="#EFEBE1",
            fill_strong="#DED7C9", ink="#26251F",
            sub_seed="#565249", faint_seed="#746D62",
            line="#E8E3D8", line_strong="#D8D0C0",
            accent="#8A6248", accent_deep="#6F4C36", accent_soft="#F4EDE5",
            danger="#B4493A", danger_soft="#F7EDE9",
            sun="#C25B4E", sat="#5E7A99",
            tone2="#A68A5B", soft2="#EFE7D5", tone3="#6E7F8D", soft3="#E3E8EB",
            stamp="#C14436", r_card="14px", r_in="9px",
        ),
    ),
    dict(
        file="b-aizome.html", letter="B", jp="藍染", romaji="AIZOME",
        cn_short="蓝染 · 商务工具",
        tagline="白瓷与蓝染的秩序感",
        desc="冷调白瓷底，取传统蓝染色作唯一强调色，发丝线与利落小圆角带来秩序与信赖感。信息密度高而不喧哗，适合商务 / 金融 / 效率工具类 App。",
        keywords=["清潔", "秩序", "信頼"],
        kanji="藍",
        swatches=[("白磁", "#F5F7FA"), ("白", "#FFFFFF"), ("藍墨", "#1A2330"),
                  ("藍", "#2E5A87"), ("臙脂", "#B44A40"), ("淡藍", "#E4E9F0")],
        radii="卡片 12 / 按钮 胶囊 / 输入 7",
        vars=dict(
            page_bg="#E6E9EE", bg="#F5F7FA", surface="#FFFFFF", fill="#EDF1F6",
            fill_strong="#DBE2EB", ink="#1A2330",
            sub_seed="#4B5563", faint_seed="#637182",
            line="#E4E9F0", line_strong="#D2DAE5",
            accent="#2E5A87", accent_deep="#24476C", accent_soft="#E7EEF7",
            danger="#B44A40", danger_soft="#F9EEEC",
            sun="#C25B52", sat="#5B7FA6",
            tone2="#4E8D7A", soft2="#E2F0EB", tone3="#7D6E9E", soft3="#EBE7F4",
            stamp="#C53D34", r_card="12px", r_in="7px",
        ),
    ),
    dict(
        file="c-wakatake.html", letter="C", jp="若竹", romaji="WAKATAKE",
        cn_short="抹茶 · 治愈自然",
        tagline="低饱和抹茶与呼吸感",
        desc="以若竹与苔的低饱和绿为主色，圆角放大、留白更足，营造治愈与呼吸感。适合健康 / 冥想 / 日记 / 天气类 App。",
        keywords=["自然", "癒し", "呼吸"],
        kanji="若",
        swatches=[("若白", "#F4F7F0"), ("白", "#FCFDF9"), ("黒緑", "#222A1F"),
                  ("松葉", "#5E7A50"), ("柿", "#B4523C"), ("薄青", "#E1E8D9")],
        radii="卡片 18 / 按钮 胶囊 / 输入 12",
        vars=dict(
            page_bg="#E7EBE1", bg="#F4F7F0", surface="#FCFDF9", fill="#EBF0E5",
            fill_strong="#D9E1D1", ink="#222A1F",
            sub_seed="#4D5747", faint_seed="#687361",
            line="#E2E9DA", line_strong="#CEDAC4",
            accent="#5B764E", accent_deep="#4A6340", accent_soft="#F2F6EE",
            danger="#B4523C", danger_soft="#FBF5F2",
            sun="#C25B4E", sat="#5E7D99",
            tone2="#A68A5B", soft2="#F0E9D8", tone3="#6E85A3", soft3="#E4EAF2",
            stamp="#C14436", r_card="18px", r_in="12px",
        ),
    ),
    dict(
        file="e-seiji.html", letter="E", jp="青磁", romaji="SEIJI",
        cn_short="青瓷 · 安静长读",
        tagline="雨过天青的瓷釉",
        desc="以淡青竹与亚麻两色为空气：青瓷釉作主色、亚麻作次级色，整页统一在偏青的暖白里。低饱和青绿营造安静的阅读氛围，发丝线与中等圆角让长文不显拥挤，适合长时间阅读 / 阅读器 / 笔记 / 知识管理类 App。",
        keywords=["静謐", "澄浄", "余韻"],
        kanji="瓷",
        swatches=[("青白", "#F2F7F5"), ("白", "#FCFDFD"), ("墨青", "#1E2C29"),
                  ("淡青竹", "#A3C4B8"), ("朱", "#C24135"), ("亜麻", "#F3F1E9")],
        radii="卡片 16 / 按钮 胶囊 / 输入 10",
        vars=dict(
            page_bg="#E2ECE8", bg="#F2F7F5", surface="#FCFDFD", fill="#E8F2EE",
            fill_strong="#D3E4DD", ink="#1E2C29",
            sub_seed="#53655D", faint_seed="#748B81",
            line="#DFECE7", line_strong="#CADED5",
            accent="#467C68", accent_deep="#356453", accent_soft="#EAF5F1",
            danger="#B44A3E", danger_soft="#F7ECEB",
            sun="#C35B4B", sat="#5C7699",
            tone2="#92865D", soft2="#F3F1E9", tone3="#697F96", soft3="#EAEEF3",
            stamp="#C24135", r_card="16px", r_in="10px",
        ),
    ),
    dict(
        file="f-sakura.html", letter="F", jp="桜色", romaji="SAKURA",
        cn_short="桜粉 · 晨光柔和",
        tagline="花曇りのやわらかな光",
        desc="底色取自桜色 #FEEFEA 与 #F5E6E1 —— 暖白里带一丝粉，像樱花季清晨的薄光。主色「淡桜」#EBB4AC 刻意保持清透高明度（L 0.80，六套中唯一），按钮走墨字而非白字，因此色感轻盈不沉。适合日记 / 相册 / 手帐 / 花艺 / 生活方式类 App。",
        keywords=["花曇", "やわらか", "淡光"],
        kanji="桜",
        swatches=[("桜白", "#FEEFEA"), ("白", "#FFFAF7"), ("墨", "#3A2A28"),
                  ("淡桜", "#EBB4AC"), ("朱", "#C24135"), ("灰藍", "#7C93A6")],
        radii="卡片 18 / 按钮 胶囊 / 输入 10",
        vars=dict(
            page_bg="#F5E6E1", bg="#FEEFEA", surface="#FFFAF7", fill="#FBE9E4",
            fill_strong="#F2D9D2", ink="#3A2A28",
            sub_seed="#7A5C58", faint_seed="#9B7E79",
            line="#F4E0DA", line_strong="#E7C9C1",
            accent="#EBB4AC", accent_deep="#D89A91", accent_soft="#FDF1EE",
            danger="#B44A3F", danger_soft="#F8ECEA",
            sun="#C25B4E", sat="#7C93A6",
            tone2="#9E8A72", soft2="#F2EBE0", tone3="#7C93A6", soft3="#E8EEF3",
            stamp="#C24135", r_card="18px", r_in="10px",
        ),
    ),
]

THEMES.extend(load_custom())

# ------------------------------------------------------------------ icons ----
def _svg(inner, sw=1.6):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')

ICONS = dict(
    SEARCH=_svg('<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2"/>'),
    HEART=_svg('<path d="M20.8 5.6a5.2 5.2 0 0 0-7.4 0L12 7l-1.4-1.4a5.2 5.2 0 1 0-7.4 7.4l1.4 1.4L12 21.8l7.4-7.4 1.4-1.4a5.2 5.2 0 0 0 0-7.4z"/>'),
    SHARE=_svg('<path d="M4 12.5V20a1.8 1.8 0 0 0 1.8 1.8h12.4A1.8 1.8 0 0 0 20 20v-7.5"/><polyline points="16 6.3 12 2.3 8 6.3"/><line x1="12" y1="2.5" x2="12" y2="15"/>'),
    PLUS=_svg('<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>', 1.8),
    CHECK=_svg('<polyline points="20 6 9 17 4 12"/>', 2.2),
    INFO=_svg('<circle cx="12" cy="12" r="9.2"/><line x1="12" y1="11" x2="12" y2="16.4"/><circle cx="12" cy="7.9" r="0.5" fill="currentColor" stroke="none"/>'),
    WARN=_svg('<path d="M10.3 3.6 1.9 18a2 2 0 0 0 1.7 3h16.8a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17.4" r="0.5" fill="currentColor" stroke="none"/>'),
    CHEVR='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 5.5 15.5 12 9 18.5"/></svg>',
    CHEV_L='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="14.5 5.5 8 12 14.5 18.5"/></svg>',
    USER=_svg('<path d="M20 21v-1.8a4.2 4.2 0 0 0-4.2-4.2H8.2A4.2 4.2 0 0 0 4 19.2V21"/><circle cx="12" cy="7.2" r="4.2"/>'),
    BELL=_svg('<path d="M18 8.4a6 6 0 0 0-12 0c0 7-2.8 8.9-2.8 8.9h17.6S18 15.4 18 8.4"/><path d="M13.7 20.7a2 2 0 0 1-3.4 0"/>'),
    LOCK=_svg('<rect x="4" y="10.6" width="16" height="10.6" rx="2.2"/><path d="M7.8 10.6V7a4.2 4.2 0 0 1 8.4 0v3.6"/>'),
    HOME=_svg('<path d="M3.2 9.8 12 2.8l8.8 7v10a1.6 1.6 0 0 1-1.6 1.6H4.8a1.6 1.6 0 0 1-1.6-1.6z"/><polyline points="9.2 21.4 9.2 14.2 14.8 14.2 14.8 21.4"/>'),
    CAL=_svg('<rect x="3.2" y="4.8" width="17.6" height="16.8" rx="2.2"/><line x1="16.2" y1="2.4" x2="16.2" y2="7"/><line x1="7.8" y1="2.4" x2="7.8" y2="7"/><line x1="3.2" y1="10.2" x2="20.8" y2="10.2"/>'),
    NOTE=_svg('<path d="M14 2.6H6.4a2.2 2.2 0 0 0-2.2 2.2v14.4a2.2 2.2 0 0 0 2.2 2.2h11.2a2.2 2.2 0 0 0 2.2-2.2V7.4z"/><polyline points="14 2.6 14 7.4 19.8 7.4"/>'),
    SLIDERS=_svg('<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1.4" y1="14" x2="6.6" y2="14"/><line x1="9.4" y1="8" x2="14.6" y2="8"/><line x1="17.4" y1="16" x2="22.6" y2="16"/>'),
    WIFI=('<svg width="15" height="11" viewBox="0 0 15 11" fill="none">'
          '<path d="M7.5 10.4 9.7 7.7a3.4 3.4 0 0 0-4.4 0z" fill="currentColor"/>'
          '<path d="M4.1 5.9a5.5 5.5 0 0 1 6.8 0" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" fill="none"/>'
          '<path d="M1.8 3.4a8.8 8.8 0 0 1 11.4 0" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" fill="none"/></svg>'),
)

# -------------------------------------------------------------------- css ----
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body{background:var(--page-bg);color:var(--ink);letter-spacing:.01em;
  font-family:"Hiragino Sans","Yu Gothic","Noto Sans JP","PingFang SC","Microsoft YaHei",-apple-system,sans-serif}
svg{display:block}
button{font-family:inherit}
.board{width:1240px;margin:0 auto;padding:56px 32px 20px}

/* ===== board header ===== */
.bh{display:flex;justify-content:space-between;align-items:flex-start;gap:26px}
.bh-left{display:flex;gap:24px;flex:1;min-width:0}
.appicon{width:92px;height:92px;border-radius:22px;background:var(--bg);border:1px solid var(--line);
  display:flex;align-items:center;justify-content:center;box-shadow:0 8px 20px rgba(0,0,0,.08);
  flex:none;position:relative;overflow:hidden}
.appicon .kanji{font-size:calc(36px * var(--dt-scale,1));font-weight:700;color:var(--accent-text)}
.appicon::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:var(--accent);opacity:.85}
.kicker{font-size:calc(10.5px * var(--dt-scale,1));letter-spacing:.3em;color:var(--faint);text-transform:uppercase;margin-bottom:12px}
.bh-title h1{font-size:calc(42px * var(--dt-scale,1));font-weight:700;letter-spacing:.1em;display:flex;align-items:baseline;gap:16px}
.bh-title h1 .romaji{font-size:calc(13px * var(--dt-scale,1));font-weight:400;letter-spacing:.34em;color:var(--faint)}
.bh-title .cn{margin-top:8px;font-size:calc(15px * var(--dt-scale,1));color:var(--sub);letter-spacing:.08em}
.bh-title .desc{margin-top:14px;font-size:calc(13.5px * var(--dt-scale,1));line-height:2;color:var(--sub);max-width:520px}
.kw{display:flex;gap:8px;margin-top:16px}
.kw span{font-size:calc(11px * var(--dt-scale,1));letter-spacing:.18em;color:var(--accent-text);border:1px solid var(--accent);
  border-radius:20px;padding:4px 13px;opacity:.9}
.tate{writing-mode:vertical-rl;font-size:calc(11px * var(--dt-scale,1));letter-spacing:.55em;color:var(--faint);
  height:150px;flex:none;padding-top:6px}
.swatches{display:flex;gap:14px;flex:none;flex-wrap:wrap}
/* i18n: 色名拉丁化后远超 64px（实测 Gerösteter Tee=83 / Roasted Tea=68 / Unbleached=67）。
   固定 width 会截断，改 min-width + auto；日文名最长 36px，min-width 仍主导 => 渲染等价。 */
.sw{text-align:center;min-width:64px;width:auto}
.sw .dot{width:44px;height:44px;border-radius:50%;margin:0 auto 8px;border:1px solid rgba(0,0,0,.09);
  box-shadow:inset 0 0 0 3px rgba(255,255,255,.35)}
.sw .nm{font-size:calc(11px * var(--dt-scale,1));color:var(--sub);letter-spacing:.08em}
.sw .hx{font-size:calc(9.5px * var(--dt-scale,1));color:var(--faint);font-family:ui-monospace,Consolas,monospace;margin-top:2px}
.tokens{display:flex;gap:10px;flex-wrap:wrap;border-top:1px solid var(--line);
  padding-top:20px;margin:30px 0 0}
.tk{font-size:calc(11.5px * var(--dt-scale,1));color:var(--sub);border:1px solid var(--line);border-radius:8px;
  padding:7px 13px;background:var(--surface);letter-spacing:.03em}
.tk b{color:var(--ink);margin-right:7px;font-weight:600}

/* ===== section tags ===== */
.sec-tag{display:flex;align-items:baseline;gap:16px;margin:52px 2px 20px}
.sec-tag h2{font-size:calc(20px * var(--dt-scale,1));letter-spacing:.2em;font-weight:700}
.sec-tag .en{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.26em;color:var(--faint);text-transform:uppercase}
.sec-tag::after{content:"";flex:1;height:1px;background:var(--line);align-self:center}
.cols{display:flex;gap:24px;align-items:flex-start}
.col{width:375px;flex:none}
.col-tag{display:flex;align-items:baseline;gap:10px;margin-bottom:14px;padding:0 2px}
.col-tag .no{font-size:calc(11px * var(--dt-scale,1));color:var(--accent-text);letter-spacing:.2em;font-weight:700}
.col-tag .en{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.22em;text-transform:uppercase;color:var(--faint)}
.col-tag .cn{font-size:calc(12.5px * var(--dt-scale,1));color:var(--sub);letter-spacing:.12em;margin-left:auto}

/* ===== phone screen shell ===== */
.screen{width:375px;background:var(--bg);border-radius:26px;border:1px solid var(--line);
  box-shadow:0 12px 36px rgba(20,18,14,.10);overflow:hidden;padding-bottom:28px}
.statusbar{height:46px;display:flex;justify-content:space-between;align-items:center;
  padding:0 26px;font-size:calc(14.5px * var(--dt-scale,1));font-weight:700}
.sb-right{display:flex;align-items:center;gap:6px}
.sig{display:flex;gap:2px;align-items:flex-end}
.sig i{width:3px;background:var(--ink);border-radius:1px;display:block}
.sig i:nth-child(1){height:4px}.sig i:nth-child(2){height:6px}
.sig i:nth-child(3){height:8px}.sig i:nth-child(4){height:10px}
.wifi{display:flex;color:var(--ink)}
.bat{width:23px;height:11.5px;border:1.4px solid var(--ink);border-radius:3.5px;position:relative;opacity:.85}
.bat::before{content:"";position:absolute;right:-3.6px;top:2.8px;width:1.8px;height:4px;
  background:var(--ink);border-radius:0 1px 1px 0}
.bat i{position:absolute;left:1.4px;top:1.4px;bottom:1.4px;width:13px;background:var(--ink);
  border-radius:1.5px;display:block}
.sec{padding:0 22px;margin-top:26px}
.statusbar + .sec{margin-top:16px}
.sec-h{display:flex;align-items:baseline;gap:10px;margin-bottom:16px}
.sec-h .jp{font-size:calc(13px * var(--dt-scale,1));font-weight:700;letter-spacing:.2em}
.sec-h .en{font-size:calc(9.5px * var(--dt-scale,1));letter-spacing:.22em;text-transform:uppercase;color:var(--faint);margin-left:auto}
.stack > * + *{margin-top:12px}
.mt4{margin-top:4px}.mt12{margin-top:12px}.mt16{margin-top:16px}
.mt20{margin-top:20px}.mt24{margin-top:24px}.mb16{margin-bottom:16px}

/* ===== buttons ===== */
.btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:50px;
  border-radius:var(--r-btn);font-size:calc(16px * var(--dt-scale,1));font-weight:600;letter-spacing:.05em;
  border:1px solid transparent;cursor:pointer;transition:transform .12s ease,filter .12s ease}
.btn:hover{filter:brightness(1.06)}
.btn:active{transform:scale(.985)}
.btn-primary{background:var(--accent);color:var(--on-accent)}
.btn-secondary{background:var(--surface);border-color:var(--line-strong);color:var(--ink)}
.btn-soft{background:var(--accent-soft);color:var(--accent-deep)}
.btn-ghost{background:transparent;color:var(--accent-text)}
.btn-ghost:hover{background:var(--accent-soft)}
.btn-danger{background:var(--danger-soft);color:var(--danger-text)}
.btn-disabled{background:var(--fill);color:var(--faint);cursor:default}
.btn-disabled:hover{filter:none}
.btn-loading{background:var(--accent);color:var(--on-accent);opacity:.72}
.spinner{width:16px;height:16px;border:2px solid var(--on-accent);opacity:.75;border-top-color:transparent;
  border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.btn-row{display:flex;gap:10px}
.btn-row > .btn{flex:1;width:auto}
.btn-sm{height:36px;font-size:calc(13px * var(--dt-scale,1))}
.icon-btns{display:flex;gap:12px;margin-top:18px}
.ibtn{width:44px;height:44px;border-radius:50%;background:var(--surface);border:1px solid var(--line-strong);
  display:flex;align-items:center;justify-content:center;color:var(--sub);cursor:pointer;
  transition:background .15s}
.ibtn:hover{background:var(--fill)}
.ibtn.fill{background:var(--accent);border-color:var(--accent-text);color:var(--on-accent)}
.ibtn.fill:hover{filter:brightness(1.08);background:var(--accent)}
.ibtn svg{width:19px;height:19px}

/* ===== controls ===== */
.seg{display:flex;background:var(--fill);border-radius:var(--r-segment);padding:2.5px;gap:2px}
.seg span{flex:1;text-align:center;padding:7.5px 0;font-size:calc(13px * var(--dt-scale,1));letter-spacing:.06em;
  border-radius:var(--r-segment-item);color:var(--sub);cursor:pointer}
.seg .on{background:var(--surface);color:var(--ink);font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.ctl{margin-top:18px}
.ctl-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0}
.ctl-row + .ctl-row{border-top:1px solid var(--line)}
.ctl-label{font-size:calc(14.5px * var(--dt-scale,1));letter-spacing:.03em}
.ctl-sub{font-size:calc(11.5px * var(--dt-scale,1));color:var(--faint);margin-top:2px}
.toggle{width:51px;height:31px;border-radius:16px;background:var(--accent);position:relative;
  flex:none;cursor:pointer;transition:background .2s}
.toggle::after{content:"";position:absolute;width:27px;height:27px;border-radius:50%;background:#fff;
  top:2px;right:2px;box-shadow:0 1px 3px rgba(0,0,0,.18);transition:left .2s,right .2s}
.toggle.off{background:var(--fill-strong)}
.toggle.off::after{right:auto;left:2px}
.cbx{width:22px;height:22px;border-radius:calc(var(--r-in) - 2px);border:1.5px solid var(--line-strong);
  background:var(--surface);flex:none;display:flex;align-items:center;justify-content:center;cursor:pointer}
.cbx svg{width:13px;height:13px;color:var(--on-accent)}
.cbx.on{background:var(--accent);border-color:var(--accent-text)}
.rdo{width:22px;height:22px;border-radius:50%;border:1.5px solid var(--line-strong);
  background:var(--surface);flex:none;display:flex;align-items:center;justify-content:center;cursor:pointer}
.rdo.on{border-color:var(--accent-text)}
.rdo.on::after{content:"";width:11px;height:11px;border-radius:50%;background:var(--accent)}
.sl-wrap{margin-top:20px}
.sl-head{display:flex;justify-content:space-between;font-size:calc(14.5px * var(--dt-scale,1));margin-bottom:12px;letter-spacing:.03em}
.sl-head b{font-weight:600;color:var(--accent-text);font-size:calc(13px * var(--dt-scale,1))}
.slider{position:relative;height:26px;display:flex;align-items:center}
.sl-track{width:100%;height:4px;background:var(--fill-strong);border-radius:2px;position:relative}
.sl-fill{position:absolute;left:0;top:0;bottom:0;width:62%;background:var(--accent);border-radius:2px}
.sl-knob{position:absolute;left:62%;top:50%;transform:translate(-50%,-50%);width:24px;height:24px;
  border-radius:50%;background:#fff;border:1px solid var(--line-strong);box-shadow:0 1px 5px rgba(0,0,0,.15)}

/* ===== inputs ===== */
.field{margin-bottom:17px}
.field-label{display:flex;justify-content:space-between;align-items:baseline;
  font-size:calc(13px * var(--dt-scale,1));color:var(--sub);margin-bottom:8px;letter-spacing:.05em}
.field-label .req{color:var(--danger);font-size:calc(10.5px * var(--dt-scale,1));letter-spacing:.15em}
.field-label .hint{color:var(--faint);font-size:calc(11px * var(--dt-scale,1))}
.input{height:48px;border:1px solid var(--line-strong);border-radius:var(--r-in);
  background:var(--surface);padding:0 14px;font-size:calc(15px * var(--dt-scale,1));display:flex;align-items:center;color:var(--ink)}
.ph{color:var(--faint)}
.input.focus{border-color:var(--accent-text);box-shadow:0 0 0 3px var(--accent-soft)}
.input.error{border-color:var(--danger);box-shadow:0 0 0 3px var(--danger-soft)}
.field-msg{font-size:calc(12px * var(--dt-scale,1));margin-top:7px;color:var(--danger);letter-spacing:.02em}
.field-msg.ok{color:var(--tone2-text)}
.search{height:auto;min-height:44px;background:var(--fill);border-radius:var(--r-btn);display:flex;align-items:center;
  gap:8px;padding:8px 16px;font-size:calc(16px * var(--dt-scale,1));color:var(--faint);overflow-wrap:anywhere}
.search svg{width:16px;height:16px;flex:none;color:var(--sub)}
.textarea{min-height:86px;border:1px solid var(--line-strong);border-radius:var(--r-in);
  background:var(--surface);padding:13px 14px;font-size:calc(14.5px * var(--dt-scale,1));line-height:1.7}
.row-field{display:flex;align-items:center;justify-content:space-between;gap:10px;height:56px;
  border:1px solid var(--line-strong);border-radius:var(--r-in);padding:0 14px;
  background:var(--surface);cursor:pointer}
.rf-tx{display:flex;flex-direction:column;gap:3px}
.rf-lab{font-size:calc(11.5px * var(--dt-scale,1));color:var(--faint);letter-spacing:.1em}
.rf-val{font-size:calc(15px * var(--dt-scale,1));font-weight:600;letter-spacing:.03em}
.chev{color:var(--faint);display:flex}
.chev svg{width:16px;height:16px}

/* ===== feedback ===== */
.toast-stage{display:flex;justify-content:center;padding:8px 0 16px}
.toast{display:flex;align-items:center;gap:8px;background:var(--accent-soft);color:var(--accent-deep);font-size:calc(16px * var(--dt-scale,1));
  letter-spacing:.05em;padding:12px 16px;border-radius:var(--r-btn);box-shadow:0 8px 24px rgba(0,0,0,.24);max-width:100%;overflow-wrap:anywhere}
.toast .ic{width:18px;height:18px;border-radius:50%;background:transparent;flex:none;
  display:flex;align-items:center;justify-content:center}
.toast .ic svg{width:10px;height:10px}
.stage{background:rgba(28,26,22,.4);border-radius:var(--r-card);padding:34px 24px;display:flex;justify-content:center}
.alert{width:292px;background:var(--surface);border-radius:18px;overflow:hidden;text-align:center;
  box-shadow:0 18px 44px rgba(0,0,0,.28)}
.alert h4{font-size:calc(16.5px * var(--dt-scale,1));padding:22px 20px 8px;letter-spacing:.04em}
.alert p{font-size:calc(13px * var(--dt-scale,1));color:var(--sub);padding:0 22px 20px;line-height:1.8}
.alert-btns{display:flex;border-top:1px solid var(--line)}
.alert-btns button{flex:1;height:48px;background:none;border:none;font-size:calc(15.5px * var(--dt-scale,1));color:var(--sub);
  letter-spacing:.06em;cursor:pointer;font-family:inherit}
.alert-btns button:hover{background:var(--fill)}
.alert-btns button + button{border-left:1px solid var(--line)}
.alert-btns .em{color:var(--accent-text);font-weight:700}
.alert-btns .dg{color:var(--danger-text);font-weight:600}
.banner{display:flex;gap:10px;align-items:flex-start;background:var(--accent-soft);
  border-radius:var(--r-in);padding:12px 14px;font-size:calc(12.5px * var(--dt-scale,1));line-height:1.7;color:var(--accent-deep)}
.banner .bi{flex:none;margin-top:1px;color:var(--accent-text)}
.banner .bi svg{width:15px;height:15px}
.banner.warn{background:var(--danger-soft);color:var(--danger)}
.banner.warn .bi{color:var(--danger)}
.badge-row{display:flex;align-items:center;gap:16px;margin-top:16px}
.chip{height:30px;display:inline-flex;align-items:center;padding:0 14px;border-radius:15px;
  background:var(--fill);font-size:calc(12.5px * var(--dt-scale,1));color:var(--sub);letter-spacing:.05em;
  border:1px solid transparent;cursor:pointer}
.chip.on{background:var(--accent-soft);color:var(--accent-deep);border-color:var(--accent-text);font-weight:600}
.bdg{min-width:19px;height:19px;border-radius:10px;background:var(--danger);color:var(--on-danger);font-size:calc(11px * var(--dt-scale,1));
  font-weight:700;display:inline-flex;align-items:center;justify-content:center;padding:0 5px}
.dot-red{width:9px;height:9px;border-radius:50%;background:var(--danger);display:inline-block}
.tag-new{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.14em;color:var(--on-stamp);background:var(--stamp);border-radius:4px;
  padding:3px 7px;font-weight:700}

/* ===== calendar ===== */
.cal{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-card);padding:16px 14px 12px}
.cal-h{display:flex;align-items:center;justify-content:space-between;padding:0 6px 12px}
.cal-h .m{font-size:calc(14.5px * var(--dt-scale,1));font-weight:700;letter-spacing:.1em}
.cal-h .nav{color:var(--faint);display:flex;gap:16px;cursor:pointer}
.cal-h .nav svg{width:16px;height:16px}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr)}
.cal-wd{text-align:center;font-size:calc(10.5px * var(--dt-scale,1));color:var(--faint);padding:4px 0 8px;letter-spacing:.05em}
.cal-wd.sun{color:var(--sun)}.cal-wd.sat{color:var(--sat)}
.cal-d{height:40px;display:flex;flex-direction:column;align-items:center;justify-content:center;
  font-size:calc(13.5px * var(--dt-scale,1));color:var(--ink);position:relative}
.cal-d .n{width:29px;height:29px;display:flex;align-items:center;justify-content:center;border-radius:50%;
  cursor:pointer}
.cal-d.sun{color:var(--sun)}.cal-d.sat{color:var(--sat)}
.cal-d.sel .n{background:var(--accent);color:var(--on-accent);font-weight:700}
.cal-d .ev{width:4px;height:4px;border-radius:50%;background:var(--accent);position:absolute;bottom:1px}
.cal-d .ev.t2{background:var(--tone2)}
.cal-legend{display:flex;gap:16px;justify-content:center;margin-top:8px;font-size:calc(10px * var(--dt-scale,1));color:var(--faint);
  letter-spacing:.06em}
.cal-legend i{width:5px;height:5px;border-radius:50%;background:var(--accent);display:inline-block;
  margin-right:5px;vertical-align:1px}
.cal-legend i.t2{background:var(--tone2)}

/* ===== list & schedule ===== */
.list{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-card);overflow:hidden}
.li{display:flex;align-items:center;gap:12px;padding:0 14px;height:62px;cursor:pointer;transition:background .15s}
.li:hover{background:var(--fill)}
.li + .li{border-top:1px solid var(--line)}
.li-ic{width:34px;height:34px;border-radius:9px;background:var(--accent-soft);color:var(--accent-text);
  display:flex;align-items:center;justify-content:center;flex:none}
.li-ic svg{width:17px;height:17px}
.li-tx b{display:block;font-size:calc(14.5px * var(--dt-scale,1));font-weight:600;letter-spacing:.03em}
.li-tx span{display:block;font-size:calc(11.5px * var(--dt-scale,1));color:var(--faint);margin-top:2px}
.li .right{margin-left:auto;display:flex;align-items:center;gap:8px;color:var(--faint)}
.li .right svg{width:15px;height:15px}
.li .val{font-size:calc(13px * var(--dt-scale,1));color:var(--sub)}
.sched{display:flex;gap:12px;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r-card);padding:14px 15px}
.sched .bar{width:3px;border-radius:2px;background:var(--accent);flex:none}
.sched.t2 .bar{background:var(--tone2)}
.sched.t3 .bar{background:var(--tone3)}
/* i18n: 本地化时间格式 "14:30 Uhr"=50px / "7:00 a. m."=49px 超 48px（实测）。
   改 min-width + auto；现内容 "15:00"(14.5px)≈37px，min-width 仍主导 => 渲染等价。 */
.sched .tm{font-size:calc(11px * var(--dt-scale,1));color:var(--faint);flex:none;min-width:48px;width:auto;letter-spacing:.03em;line-height:1.6}
.sched .tm b{display:block;font-size:calc(14.5px * var(--dt-scale,1));color:var(--ink);font-weight:700}
.sched .bd{flex:1;min-width:0}
.sched .bd h5{font-size:calc(14.5px * var(--dt-scale,1));font-weight:600;letter-spacing:.03em}
.sched .bd p{font-size:calc(11.5px * var(--dt-scale,1));color:var(--faint);margin-top:3px}
.sched .chip{height:22px;font-size:calc(10.5px * var(--dt-scale,1));padding:0 9px;border-radius:11px;margin-top:7px;
  background:var(--accent-soft);color:var(--accent-deep);cursor:default}
.sched.t2 .chip{background:var(--soft2);color:var(--tone2-text)}
.sched.t3 .chip{background:var(--soft3);color:var(--tone3-text)}

/* ===== demo phone ===== */
.demo-row{display:flex;gap:36px;align-items:flex-start}
.phone{width:395px;height:832px;border-radius:52px;background:#171614;padding:9px;flex:none;
  box-shadow:0 26px 64px rgba(20,18,14,.30)}
.phone-in{width:100%;height:100%;border-radius:44px;background:var(--bg);overflow:hidden;position:relative}
.island{position:absolute;top:11px;left:50%;transform:translateX(-50%);width:112px;height:31px;
  background:#0c0b0a;border-radius:17px;z-index:10}
.home-bar{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);width:134px;height:5px;
  border-radius:3px;background:var(--ink);opacity:.28;z-index:10}
.scr{position:absolute;inset:0;display:flex;flex-direction:column}
.scr-scroll{flex:1;overflow:hidden;padding:0 20px}
.scr-head{display:flex;justify-content:space-between;align-items:center;padding:8px 2px 14px}
.greet{font-size:calc(12px * var(--dt-scale,1));color:var(--faint);letter-spacing:.16em}
.date-big{font-size:calc(27px * var(--dt-scale,1));font-weight:700;letter-spacing:.05em;margin-top:5px}
.avatar{width:38px;height:38px;border-radius:50%;border:1px solid var(--line-strong);
  background:var(--surface);display:flex;align-items:center;justify-content:center;color:var(--sub)}
.avatar svg{width:18px;height:18px}
.week{display:flex;justify-content:space-between;padding:8px 10px 10px;margin:2px 0 0;
  border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.wk{width:40px;text-align:center;display:flex;flex-direction:column;gap:6px;align-items:center}
.wk span{font-size:calc(10.5px * var(--dt-scale,1));color:var(--faint);letter-spacing:.05em}
.wk b{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:calc(14px * var(--dt-scale,1));font-weight:600;color:var(--ink)}
.wk.sat b{color:var(--sat)}.wk.sun b{color:var(--sun)}
.wk.sel b{background:var(--accent);color:var(--on-accent);font-weight:700;box-shadow:0 4px 10px rgba(0,0,0,.18)}
.wk.sel span{color:var(--accent-text);font-weight:600}
.scr-sec{display:flex;align-items:baseline;justify-content:space-between;margin:20px 2px 12px}
.scr-sec h3{font-size:calc(15px * var(--dt-scale,1));font-weight:700;letter-spacing:.16em}
.scr-sec h3 i{font-style:normal;font-weight:400;color:var(--faint);font-size:calc(11px * var(--dt-scale,1));letter-spacing:.08em}
.scr-sec a{font-size:calc(11px * var(--dt-scale,1));color:var(--faint);letter-spacing:.1em;cursor:pointer}
.quote{display:flex;gap:14px;justify-content:space-between;background:var(--surface);
  border:1px solid var(--line);border-radius:var(--r-card);padding:16px 18px;margin-top:22px}
.tate-sm{writing-mode:vertical-rl;font-size:calc(10px * var(--dt-scale,1));letter-spacing:.4em;color:var(--faint)}
.q-title{font-size:calc(10.5px * var(--dt-scale,1));letter-spacing:.24em;color:var(--accent-text);font-weight:600}
.q-text{font-size:calc(14.5px * var(--dt-scale,1));line-height:2;margin-top:7px;letter-spacing:.08em}
.q-by{font-size:calc(11px * var(--dt-scale,1));color:var(--faint);margin-top:7px;letter-spacing:.06em}
.tabbar{height:82px;background:var(--surface);border-top:1px solid var(--line);
  display:flex;padding:8px 6px 24px;flex:none}
.tab{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;gap:4px;font-size:calc(9.5px * var(--dt-scale,1));
  letter-spacing:.08em;color:var(--faint);cursor:pointer}
/* i18n: Tab 标签单行截断。德语 Einstellungen=66px / 可用 73px（实测余量仅 7px），DT 放大即溢出。
   min-width:0 让 flex 子项可收缩；:last-child 精确命中标签，避开 devices.html 的 .ic 图标 span。 */
.tab span:last-child{display:block;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tab svg{width:22px;height:22px}
.tab.on{color:var(--accent-text);font-weight:600}
.tab-plus b{width:46px;height:46px;border-radius:50%;background:var(--accent);color:var(--on-accent);
  display:flex;align-items:center;justify-content:center;box-shadow:0 6px 16px rgba(0,0,0,.22);
  margin-top:-18px}
.tab-plus b svg{width:20px;height:20px}

/* ===== notes ===== */
.notes{flex:1;background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:30px 34px}
.notes h3{font-size:calc(17px * var(--dt-scale,1));letter-spacing:.14em;display:flex;align-items:baseline;gap:12px}
.notes h3 .en{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.26em;color:var(--faint);text-transform:uppercase}
.notes h4{font-size:calc(12px * var(--dt-scale,1));letter-spacing:.24em;color:var(--accent-text);margin:24px 0 8px;font-weight:700}
.notes ul{list-style:none}
.notes li{font-size:calc(13px * var(--dt-scale,1));color:var(--sub);line-height:2.1;padding-left:16px;position:relative}
.notes li::before{content:"";position:absolute;left:0;top:14px;width:5px;height:5px;border-radius:50%;
  background:var(--accent);opacity:.55}
.notes li b{color:var(--ink);font-weight:600}
.foot{margin:70px 0 46px;text-align:center;font-size:calc(10px * var(--dt-scale,1));letter-spacing:.34em;color:var(--faint)}
"""

# ==========================================================================
# i18n 多语言适配层（2026-09-17 追加）
# --------------------------------------------------------------------------
# 全部规则以 html[lang|=…] 限定作用域。本项目 11 个页面均声明 lang="zh-CN"，
# 故对现有交付物**渲染零影响**；仅当页面改为拉丁语系 lang 时生效。
#
# 采用「显式白名单」而非 :not([lang|="zh"]) 反选：页面若漏写 lang 属性，
# 白名单方案会退回 CJK 默认（安全），反选方案会误套拉丁排版（危险）。
#
# LAT_LANG_SEL 是**语种列表的唯一事实源**，build_ext / build_devices 均须 import 复用，
# 禁止在其它文件另抄一份。新增语言只改这里。
#
# 实测依据：skills/jp-min-ui-build/SKILL.md 第九章 + tmp/i18n_facts.txt / i18n_fixed.txt
# ==========================================================================
LAT_LANGS = ["en", "es", "fr", "de", "it", "pt", "nl", "sv", "da", "nb",
             "fi", "pl", "cs", "ro", "hu", "tr", "id", "vi"]
LAT_LANG_SEL = "html:is(" + ",".join('[lang|="%s"]' % c for c in LAT_LANGS) + ")"

FF_CJK = ('"Hiragino Sans","Yu Gothic","Noto Sans JP","PingFang SC",'
          '"Microsoft YaHei",-apple-system,sans-serif')
FF_LAT = ('-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI","Noto Sans",'
          '"Helvetica Neue","Hiragino Sans","PingFang SC","Microsoft YaHei",sans-serif')

# 本文件（build.CSS）所辖选择器的降档规则
I18N_CSS = """
:root{--ff-cjk:%(CJK)s;--ff-lat:%(LAT)s}

/* 1. 字体栈：拉丁语系改用拉丁优先栈。
      实测拉丁字形在日文优先栈下由 Hiragino Sans 渲染，宽 +3~6px（约 +5%）且字形非最优。 */
%(S)s body{font-family:var(--ff-lat)}

/* 2. 行高：CJK 1.9-2.2 → 拉丁 1.5。
      拉丁沿用 CJK 行高会过松，且同高度容纳行数变少 → 挤压 .scr-scroll 内容量，
      连带使 devices.html 的 edge-to-edge 判定失真。
      注：.a11y-t(1.4) / .a11y-s(1.5) 本就是拉丁档位，不在此列。 */
%(S)s :is(.bh-title .desc,.q-text,.notes li){line-height:1.5}
%(S)s .alert p{line-height:1.55}

/* 3. 字距两层制：文档/标识层 .1~.55em 对拉丁必须降档。
      实测 .14em 使德语 Benachrichtigungen 129→164px（+27%）。
      UI 组件层（.01~.08em）拉丁可原样保留，不在此处理。
      例外（保留原字距，不降档）：
        · .tag-new("NEW") —— ≤12 字符全大写短标签，无溢出风险。
        · .romaji / .kanji —— YOHAKU·AIZOME·WAKATAKE·MURASAKI 与 余白·藍染·若竹·紫硝子。
          这两个是**跨语种字串完全相同的固定设计资产**（本地化时只换 .bh-title h1 的
          显示名，不换方向标识），且 .romaji 本就是全大写拉丁字形，.34em 宽字距
          正是它的视觉身份；对其降档会破坏品牌识别而非修正溢出。
          判据：降档只用于「字串随语言变长的本地化文本」，不用于固定标识。 */
/* 3a 长文本/标题 → .02em */
%(S)s :is(.bh-title h1,.sec-tag h2,.col-tag .cn,.rf-lab,.cal-h .m,.greet,
          .scr-sec h3,.scr-sec a,.notes h3,.field-label .req){letter-spacing:.02em}
/* 3b 全大写短标签（随语言本地化的那些）→ .06em */
%(S)s :is(.kicker,.kw span,.sec-tag .en,.col-tag .en,.sec-h .en,
          .q-title,.notes h3 .en,.notes h4,.foot){letter-spacing:.06em}

/* 4. 竖排 fallback：vertical-rl 是 CJK 专属手法。
      .tate 的 .55em 字距（实测 6.05px）下拉丁文不可读；转水平后 height 须放开。
      .kanji（36px 汉字单字装饰）保留为图形元素，不参与本地化 —— 是否替换属内容决策。 */
%(S)s :is(.tate,.tate-sm){writing-mode:horizontal-tb;height:auto;letter-spacing:.06em;
  max-width:22em;padding-top:0;text-orientation:mixed}
""".replace("%(S)s", LAT_LANG_SEL).replace("%(CJK)s", FF_CJK).replace("%(LAT)s", FF_LAT)

CSS = CSS + "\n" + I18N_CSS

# ----------------------------------------------------------------- markup ----
STATUSBAR = ('<div class="statusbar"><span>9:41</span><span class="sb-right">'
             '<span class="sig"><i></i><i></i><i></i><i></i></span>'
             '<span class="wifi">{WIFI}</span>'
             '<span class="bat"><i></i></span></span></div>')

CAL_DATES = (
    [(None, "")] * 2
    + [(1, ""), (2, ""), (3, ""), (4, ""), (5, "sat")]
    + [(6, "sun"), (7, ""), (8, ""), (9, ""), (10, ""), (11, ""), (12, "sat")]
    + [(13, "sun"), (14, ""), (15, ""), (16, ""), (17, "sel"), (18, ""), (19, "sat")]
    + [(20, "sun"), (21, ""), (22, ""), (23, ""), (24, ""), (25, ""), (26, "sat")]
    + [(27, "sun"), (28, ""), (29, ""), (30, "")]
)
EVENTS = {18: "", 22: "t2", 25: ""}

def cal_grid():
    cells = ['<div class="cal-wd sun">日</div><div class="cal-wd">月</div>'
             '<div class="cal-wd">火</div><div class="cal-wd">水</div>'
             '<div class="cal-wd">木</div><div class="cal-wd">金</div>'
             '<div class="cal-wd sat">土</div>']
    for d, cls in CAL_DATES:
        if d is None:
            cells.append('<div class="cal-d"></div>')
            continue
        ev = ""
        if d in EVENTS:
            t2 = " t2" if EVENTS[d] == "t2" else ""
            ev = f'<i class="ev{t2}"></i>'
        cells.append(f'<div class="cal-d {cls}"><span class="n">{d}</span>{ev}</div>')
    return "".join(cells)

BODY = """
<div class="sec-tag"><h2>组件样例</h2><span class="en">Component Gallery · 375 pt</span></div>

<div class="cols">

  <!-- ============ 01 Buttons & Controls ============ -->
  <div class="col">
    <div class="col-tag"><span class="no">01</span><span class="en">Buttons · Controls</span><span class="cn">按钮 · 控件</span></div>
    <div class="screen">
      __STATUSBAR__
      <div class="sec">
        <div class="sec-h"><span class="jp">ボタン</span><span class="en">Buttons</span></div>
        <div class="stack">
          <button class="btn btn-primary">続ける</button>
          <button class="btn btn-secondary">キャンセル</button>
          <div class="btn-row">
            <button class="btn btn-soft">下書き保存</button>
            <button class="btn btn-ghost">破棄</button>
          </div>
          <button class="btn btn-danger">削除する</button>
          <button class="btn btn-disabled">利用不可</button>
          <button class="btn btn-loading"><span class="spinner"></span>送信中…</button>
          <div class="btn-row mt4">
            <button class="btn btn-secondary btn-sm">タグ S</button>
            <button class="btn btn-primary btn-sm">保存 S</button>
          </div>
        </div>
        <div class="icon-btns">
          <span class="ibtn">{SEARCH}</span>
          <span class="ibtn">{HEART}</span>
          <span class="ibtn">{SHARE}</span>
          <span class="ibtn fill">{PLUS}</span>
        </div>
      </div>
      <div class="sec">
        <div class="sec-h"><span class="jp">コントロール</span><span class="en">Controls</span></div>
        <div class="seg"><span class="on">すべて</span><span>未読</span><span>完了</span></div>
        <div class="ctl">
          <div class="ctl-row"><div><div class="ctl-label">通知</div><div class="ctl-sub">プッシュ通知を受け取る</div></div><div class="toggle"></div></div>
          <div class="ctl-row"><div><div class="ctl-label">ダークモード</div><div class="ctl-sub">現在：ライト</div></div><div class="toggle off"></div></div>
          <div class="ctl-row"><div class="ctl-label">利用規約に同意する</div><div class="cbx on">{CHECK}</div></div>
          <div class="ctl-row"><div class="ctl-label">メールマガジンを購読</div><div class="cbx"></div></div>
          <div class="ctl-row"><div class="ctl-label">配送 · 標準（無料）</div><div class="rdo on"></div></div>
          <div class="ctl-row"><div class="ctl-label">配送 · お急ぎ</div><div class="rdo"></div></div>
        </div>
        <div class="sl-wrap">
          <div class="sl-head"><span>音量</span><b>62%</b></div>
          <div class="slider"><div class="sl-track"><div class="sl-fill"></div></div><div class="sl-knob"></div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ============ 02 Inputs & Feedback ============ -->
  <div class="col">
    <div class="col-tag"><span class="no">02</span><span class="en">Inputs · Feedback</span><span class="cn">输入 · 反馈</span></div>
    <div class="screen">
      __STATUSBAR__
      <div class="sec">
        <div class="sec-h"><span class="jp">入力</span><span class="en">Text Fields</span></div>
        <div class="field">
          <div class="field-label"><span>名前</span><span class="req">必須</span></div>
          <div class="input"><span class="ph">山田 太郎</span></div>
        </div>
        <div class="field">
          <div class="field-label"><span>メールアドレス</span></div>
          <div class="input focus">y.taro@example.com</div>
          <div class="field-msg ok">確認メールを送信しました</div>
        </div>
        <div class="field">
          <div class="field-label"><span>パスワード</span></div>
          <div class="input error">••••••</div>
          <div class="field-msg">8文字以上で入力してください</div>
        </div>
        <div class="field">
          <div class="search">{SEARCH}<span>商品・メモを検索</span></div>
        </div>
        <div class="field">
          <div class="row-field"><div class="rf-tx"><span class="rf-lab">生年月日</span><span class="rf-val">1994年5月8日</span></div><span class="chev">{CHEVR}</span></div>
        </div>
        <div class="field">
          <div class="field-label"><span>メモ</span><span class="hint">0 / 200</span></div>
          <div class="textarea"><span class="ph">こちらに詳細をご記入ください…</span></div>
        </div>
      </div>
      <div class="sec">
        <div class="sec-h"><span class="jp">フィードバック</span><span class="en">Feedback</span></div>
        <div class="toast-stage"><div class="toast"><span class="ic">{CHECK}</span>保存しました</div></div>
        <div class="stage">
          <div class="alert">
            <h4>この項目を削除しますか？</h4>
            <p>この操作は取り消せません。<br>よろしければ「削除」をタップしてください。</p>
            <div class="alert-btns"><button>キャンセル</button><button class="dg">削除</button></div>
          </div>
        </div>
        <div class="banner mt16"><span class="bi">{INFO}</span><span>新しいバージョン（2.1.0）が利用可能です。</span></div>
        <div class="banner warn mt12"><span class="bi">{WARN}</span><span>通信が不安定です。時間をおいて再度お試しください。</span></div>
        <div class="badge-row">
          <span class="chip">タグ</span><span class="chip on">選択中</span>
          <span class="bdg">3</span><span class="dot-red"></span><span class="tag-new">NEW</span>
        </div>
      </div>
    </div>
  </div>

  <!-- ============ 03 Date & Lists ============ -->
  <div class="col">
    <div class="col-tag"><span class="no">03</span><span class="en">Date · Lists</span><span class="cn">日期 · 列表</span></div>
    <div class="screen">
      __STATUSBAR__
      <div class="sec">
        <div class="sec-h"><span class="jp">日付</span><span class="en">Date &amp; Time</span></div>
        <div class="row-field mb16"><div class="rf-tx"><span class="rf-lab">日付を選択</span><span class="rf-val">2026年9月17日（木）</span></div><span class="chev">{CHEVR}</span></div>
        <div class="cal">
          <div class="cal-h"><span class="nav">{CHEV_L}</span><span class="m">2026年 9月</span><span class="nav">{CHEVR}</span></div>
          <div class="cal-grid">__CALGRID__</div>
          <div class="cal-legend"><span><i></i>選択 · 今日</span><span><i class="t2"></i>予定あり</span></div>
        </div>
        <div class="chips mt16" style="display:flex;gap:8px;flex-wrap:wrap">
          <span class="chip">09:00</span><span class="chip">09:30</span><span class="chip on">10:00</span><span class="chip">10:30</span><span class="chip">11:00</span>
        </div>
      </div>
      <div class="sec">
        <div class="sec-h"><span class="jp">リスト</span><span class="en">Lists</span></div>
        <div class="list">
          <div class="li"><span class="li-ic">{USER}</span><div class="li-tx"><b>プロフィール</b><span>名前 · アイコン · 自己紹介</span></div><span class="right">{CHEVR}</span></div>
          <div class="li"><span class="li-ic">{BELL}</span><div class="li-tx"><b>通知設定</b></div><span class="right"><span class="bdg">3</span>{CHEVR}</span></div>
          <div class="li"><span class="li-ic">{LOCK}</span><div class="li-tx"><b>プライバシー</b></div><span class="right"><span class="val">公開</span>{CHEVR}</span></div>
        </div>
        <div class="stack mt16">
          <div class="sched"><span class="bar"></span><div class="tm"><b>15:00</b>90分</div><div class="bd"><h5>デザインレビュー</h5><p>会議室 B · 3 名</p><span class="chip">ワーク</span></div></div>
          <div class="sched t2"><span class="bar"></span><div class="tm"><b>19:30</b>60分</div><div class="bd"><h5>ヨガクラス</h5><p>オンライン</p><span class="chip">予定</span></div></div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="sec-tag"><h2>整屏示例 · 日程アプリ「朝」</h2><span class="en">Sample Screen · 375 × 812 pt</span></div>
<div class="demo-row">
  <div class="phone"><div class="phone-in">
    <div class="island"></div>
    <div class="scr">
      __STATUSBAR__
      <div class="scr-scroll">
        <div class="scr-head">
          <div>
            <div class="greet">おはよう ― 秋分の日まで 5 日</div>
            <div class="date-big">9月17日（木）</div>
          </div>
          <div class="avatar">{USER}</div>
        </div>
        <div class="week">
          <div class="wk"><span>火</span><b>15</b></div>
          <div class="wk"><span>水</span><b>16</b></div>
          <div class="wk sel"><span>木</span><b>17</b></div>
          <div class="wk"><span>金</span><b>18</b></div>
          <div class="wk sat"><span>土</span><b>19</b></div>
          <div class="wk sun"><span>日</span><b>20</b></div>
          <div class="wk"><span>月</span><b>21</b></div>
        </div>
        <div class="scr-sec"><h3>予定 <i>· 3件</i></h3><a>すべて見る</a></div>
        <div class="stack">
          <div class="sched"><span class="bar"></span><div class="tm"><b>09:30</b>45分</div><div class="bd"><h5>朝会 · チーム共有</h5><p>会議室 A</p><span class="chip">会議</span></div></div>
          <div class="sched t2"><span class="bar"></span><div class="tm"><b>12:30</b>60分</div><div class="bd"><h5>ランチ · 佐藤さん</h5><p>駅前カフェ</p><span class="chip">予定</span></div></div>
          <div class="sched t3"><span class="bar"></span><div class="tm"><b>15:00</b>90分</div><div class="bd"><h5>デザインレビュー</h5><p>オンライン</p><span class="chip">ワーク</span></div></div>
        </div>
        <div class="quote">
          <div>
            <div class="q-title">今日の一句</div>
            <div class="q-text">名月を 取ってくれろと<br>泣く子かな</div>
            <div class="q-by">— 小林一茶</div>
          </div>
          <div class="tate-sm">めいげつ</div>
        </div>
      </div>
      <div class="tabbar">
        <div class="tab on">{HOME}<span>ホーム</span></div>
        <div class="tab">{CAL}<span>カレンダー</span></div>

        <div class="tab">{NOTE}<span>メモ</span></div>
        <div class="tab">{SLIDERS}<span>設定</span></div>
      </div>
    </div>
    <div class="home-bar"></div>
  </div></div>

  __DESIGN_NOTES__
</div>
"""


def design_notes(theme):
    """Describe emitted roles and available samples from the current theme."""
    roles=theme.get('palette_roles', {})
    if roles.get('auxiliary') and roles.get('tertiary'):
        color_story=(f'主色 {escape(roles["accent"])} 用于主要操作；辅助色 '
                     f'{escape(roles["auxiliary"])} 与第三色 {escape(roles["tertiary"])} '
                     '用于分类、图表及轻量点缀。错误、成功和警告保持独立语义，不借用品牌辅色。')
    else:
        color_story='主色用于主要操作；第二、第三色用于分类与图表。错误、成功和警告使用独立语义。'
    ext=escape(theme['file'].replace('.html','-ext.html'), quote=True)
    return f'''<div class="notes"><h3>设计说明 <span class="en">Design Notes</span></h3>
    <h4>美学原则</h4><ul>
      <li><b>间（Ma）</b>：留白与清晰层级共同组织内容，间距按组件和屏幕调整。</li>
      <li><b>线条与角色</b>：克制的描边、胶囊按钮与多色分类各有用途；{color_story}</li>
      <li><b>和式日历</b>：周日与周六的装饰色保留日历语境，不代替状态文字。</li>
      <li><b>双语版式</b>：功能文字随语言和字号调整，罗马音用于辅助识别。</li>
    </ul><h4>已有样张与原生接入</h4><ul>
      <li><a href="{ext}">查看本主题的深色、Sheet、空态、引导和图表等扩展样张</a>；基础页还包含可操作 HTML 演示。</li>
      <li>四模式语义颜色见 <a href="design-tokens.json">Token 导出</a>；原生工程映射系统动态颜色和安全区。</li>
      <li>HTML 样张与本地交互不代替 SwiftUI / WidgetKit 实现、VoiceOver 或真机验收；目标 iOS 版本由具体 App 确认。</li>
    </ul></div>'''

HEADER_TPL = Template("""
<div class="bh">
  <div class="bh-left">
    <div class="appicon"><span class="kanji">$KANJI</span></div>
    <div class="bh-title">
      <div class="kicker">JP MINIMAL UI KIT — DIRECTION $LETTER — iOS / SwiftUI</div>
      <h1>$JP<span class="romaji">$ROMAJI</span></h1>
      <div class="cn">$TAGLINE · $CN_SHORT</div>
      <p class="desc">$DESC</p>
      <div class="kw">$KW</div>
    </div>
  </div>
  <div class="tate">間を活かす・日本のミニマリズム</div>
  <div class="swatches">$SW</div>
</div>
<div class="tokens">
  <span class="tk"><b>字体</b>Hiragino Sans · SF Pro</span>
  <span class="tk"><b>字号</b>27 / 17 / 15 / 13 / 11</span>
  <span class="tk"><b>圆角</b>$RADII</span>
  <span class="tk"><b>间距</b>4 · 8 · 12 · 16 · 24 · 32</span>
  <span class="tk"><b>边框</b>1px 发丝线（低对比）</span>
  <span class="tk"><b>强调色使用</b>主要操作与必要高亮</span>
</div>
""")

# ------------------------------------------------ a11y: HC + Dynamic Type ----
# 色值唯一数据源 = contrast_patch.json（已求解好的 HC 值），严禁在此硬编码。
# Dynamic Type 机制：:root 定义 --dt-scale:1，所有 font-size 写成
#   calc(Npx * var(--dt-scale,1))
# 屏幕内可通过 .screen{--dt-scale:1.176} 之类局部覆盖实现放大；
# 屏幕外的文档装饰继承 root 的 1，故默认渲染与改造前逐像素一致。
CONTRAST_PATCH = os.path.join(OUT, "contrast_patch.json")


def hc_vars(letter, mode="light"):
    if mode not in ("light", "dark"):
        raise ValueError("Unknown color mode")
    if letter == "D":
        from build_d import L, D
        return semantic_hc_css(L if mode == "light" else D, mode == "light")
    theme = next(t for t in THEMES if t["letter"] == letter)
    if mode == "light":
        return semantic_hc_css(derive(theme["vars"], True), True)
    from build_ext import DARK
    return semantic_hc_css(DARK[letter], False)


def a11y_css(letter):
    """基础篇无障碍层：仅浅色（深色样例只存在于扩展篇）"""
    v = hc_vars(letter, "light")
    return (
        "\n/* ===== 无障碍层 · Increased Contrast + Dynamic Type ===== */\n"
        ":root{--dt-scale:1}\n"
        ".hc{" + v + "}\n"
        "@media (prefers-contrast: more){:root{" + v + "}}\n"
    )


PAGE_TPL = Template("""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>$TITLE</title>
<style>$CSS</style>
<style>:root{$VARS}</style>
<style>$A11Y</style>
</head>
<body>
<div class="board">
$HEADER
$BODY
<div class="foot">DIRECTION $LETTER · $JP — $ROMAJI · JP MINIMAL UI KIT 2026</div>
</div>
</body>
</html>
""")

# ------------------------------------------------------------------ build ----
def main():
    body_html = BODY.replace("__STATUSBAR__", STATUSBAR)
    body_html = body_html.replace("__CALGRID__", cal_grid())
    body_html = body_html.format(**ICONS)

    for t in THEMES:
        # 统一架构：vars 由 derive() 推导 sub/faint/on_*/hc_*（不再硬编码）
        tv = derive(t["vars"], True)
        vars_css = ";".join(
            f"--{k.replace('_', '-')}:{v}" for k, v in tv.items()
        )
        sw = "".join(
            f'<div class="sw"><div class="dot" style="background:{c}"></div>'
            f'<div class="nm">{n}</div><div class="hx">{c}</div></div>'
            for n, c in t["swatches"]
        )
        kw = "".join(f"<span>{k}</span>" for k in t["keywords"])
        header = HEADER_TPL.substitute(
            KANJI=t["kanji"], LETTER=t["letter"], JP=t["jp"], ROMAJI=t["romaji"],
            TAGLINE=t["tagline"], CN_SHORT=t["cn_short"], DESC=t["desc"],
            KW=kw, SW=sw, RADII=t["radii"],
        )
        page = PAGE_TPL.substitute(
            TITLE=f"{t['jp']} {t['romaji']} — 日式简约 iOS UI 方向 {t['letter']}",
            CSS=CSS, A11Y=a11y_css(t["letter"]),
            VARS=vars_css, HEADER=header, BODY=body_html.replace('__DESIGN_NOTES__', design_notes(t)),
            LETTER=t["letter"], JP=t["jp"], ROMAJI=t["romaji"],
        )
        page = prepare_page(page, t["file"], t)
        path = os.path.join(OUT, t["file"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        log.info("written %s (%.1f KB)", t["file"], os.path.getsize(path) / 1024)

    # ⚠ index.html 的归属权在 build_ext.py 的 build_index_v2()（v4 四方向卡片）。
    # 此处曾写入三方向旧版 index，一旦运行就会把 v4 索引打回旧版、D 卡消失。
    # 已于 2026-09-17 移除；build_index()/INDEX_CSS 保留仅作历史参考，不得再被调用。
    log.info("index.html 由 build_ext.py 生成")
    log.info("BUILD OK -> %s", OUT)

if __name__ == "__main__":
    main()
