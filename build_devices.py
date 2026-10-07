# -*- coding: utf-8 -*-
"""
日式简约 UI Kit · 全部主题设备尺寸样张

覆盖：注册的全部主题 × 四组 iPhone 16 系列预设样张。
尺寸仅用于 HTML 排版示意，不表示真机测试：
  iPhone 16          393 x 852  @3x
  iPhone 16 Pro      402 x 874  @3x
  iPhone 16 Plus     430 x 932  @3x
  iPhone 16 Pro Max  440 x 956  @3x

安全区 62pt / 34pt 是样张预设；原生运行时须读取系统安全区。

统一架构：全部主题 Token 来自权威主题源与 derive()，不复制色值。
Run: python build_devices.py
"""
import logging
import math
import os
import re
from design_tokens import css_vars
from site_support import prepare_page, all_themes

from build import THEMES, ICONS, cal_grid, derive, LAT_LANG_SEL, FF_LAT, LAT_LANGS   # 统一 Token 源 + 统一语种列表
from build_ext import ALL_ICONS                            # 共用线性图标库

OUT = os.path.dirname(os.path.abspath(__file__))
log = logging.getLogger("devices")
if not log.handlers:                      # 显式绑定，避免被上层 basicConfig 劫持
    log.setLevel(logging.INFO)
    log.propagate = False
    _fh = logging.FileHandler(os.path.join(OUT, "build_devices.log"), encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _sh = logging.StreamHandler()
    _sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(_fh)
    log.addHandler(_sh)

DEVICES = [
    ("iPhone 16", 393, 852, "1179 × 2556"),
    ("iPhone 16 Pro", 402, 874, "1206 × 2622"),
    ("iPhone 16 Plus", 430, 932, "1290 × 2796"),
    ("iPhone 16 Pro Max", 440, 956, "1320 × 2868"),
]
SAFE_TOP, SAFE_BOTTOM = 62, 34      # Dynamic Island 机型
TAB_H = 54                          # Tab 栏高
MARGIN = 16                         # 内容外边距（四套统一）
NAV_H = SAFE_TOP + 64               # 状态栏 62pt + 导航行 64pt（实测）

# 页面语言：唯一事实源，须与下方 HTML 模板中的 <html lang> 一致（写盘后有断言复核，
# 漂移会被捕获而非静默出错）。
LANG = "zh-CN"
SCRIPT = "lat" if LANG.split("-")[0].lower() in LAT_LANGS else "cjk"

# 日程池：屏越高需要的条数越多，按 sched_count() 截取
SCHEDULE_POOL = [
    ("09:30", "30分", "朝の打ち合わせ", "会議室 A · 3名", ""),
    ("11:00", "1時間", "デザインレビュー", "オンライン", "t2"),
    ("14:20", "45分", "資料の整理", "自席 · 集中", "t3"),
    ("16:00", "20分", "夕方の散歩", "近所 · ひとり", "t2"),
    ("19:30", "1時間", "読書", "居間 · 静かに", "t3"),
    ("21:00", "30分", "日記を書く", "自室", "t2"),
    ("22:30", "15分", "明日の支度", "自室 · 静かに", "t3"),
    ("06:30", "40分", "朝のジョギング", "公園 · ひとり", ""),
    ("10:15", "45分", "コードレビュー", "オンライン · 4名", "t2"),
    ("13:00", "30分", "昼休み", "カフェ · 静かに", "t3"),
    ("17:45", "1時間", "夕食の準備", "家 · 台所", ""),
    ("23:00", "20分", "ストレッチ", "自室", "t3"),
]


def sched_count(h):
    # A fixed example dataset: short content is valid; scrolling, not invented rows,
    # keeps the last real item reachable beneath the navigation layer.
    return 8

# 六个方向：letter / 中文 / 罗马字 / 玻璃化（仅 D）
DIRECTIONS = [(t['letter'], t['jp'], t['romaji'], t.get('material') == 'glass') for t in all_themes()]



def theme_of(letter):
    """取某方向的 vars（已过 derive），返回 (t, v)

    A/B/C 来自 build.py 的 THEMES；D 由 build_d.py 独立定义（L = derive(L_BASE, True)）。
    """
    if letter == "D":
        from build_d import L, L_BASE
        t = dict(letter="D", jp="紫硝子", romaji="MURASAKI",
                 vars=L_BASE, file="d-murasaki.html")
        return t, L
    t = next(x for x in THEMES if x["letter"] == letter)
    return t, derive(t["vars"], True)


def statusbar():
    return ('<div class="sb"><span>9:41</span>'
            '<span class="isl"></span>'
            '<span class="r"><svg width="17" height="11" viewBox="0 0 15 11" fill="currentColor">'
            '<rect x="0" y="7" width="2.6" height="4" rx="1"/><rect x="4" y="5" width="2.6" height="6" rx="1"/>'
            '<rect x="8" y="2.6" width="2.6" height="8.4" rx="1"/><rect x="12" y="0" width="2.6" height="11" rx="1"/></svg>'
            '<svg width="16" height="11" viewBox="0 0 16 12" fill="currentColor">'
            '<path d="M8 9.6a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3zM4.4 7.2a5.1 5.1 0 0 1 7.2 0l-1.2 1.2a3.4 3.4 0 0 0-4.8 0zM1.8 4.6a8.8 8.8 0 0 1 12.4 0L13 5.8a7 7 0 0 0-10 0z"/></svg>'
            '<span class="bat"></span></span></div>')


def screen(glass, h):
    """单套方向的真机屏（同一套「朝」布局，换主题即换风格）

    日程卡条数按屏高自动适配，保证内容穿过 Tab 栏 → edge-to-edge 成立。
    """
    scheds = "".join(
        '<div class="sched %s"><div class="bar"></div>'
        '<div class="tm"><b>%s</b>%s</div>'
        '<div><h5>%s</h5><p>%s</p></div></div>' % (c, t, d, ttl, p)
        for t, d, ttl, p, c in SCHEDULE_POOL[:sched_count(h)])
    nav_cls = "nav glass" if glass else "nav"
    tab_cls = "tabbar glass" if glass else "tabbar"
    return (
        statusbar()
        + '<div class="%s"><div class="big">朝</div>'
          '<div class="sub">9月17日 木曜</div>'
          '<div class="act">%s</div></div>' % (nav_cls, ALL_ICONS["PLUS"])
        + '<div class="scroll">'
          '<div class="hero"><div class="sun"></div>'
          '<div class="tx"><b>晴れ · 24°</b><span>東京 · 紫外線 やや強い</span></div></div>'
        + scheds
        + '<div class="cta-wrap"><div class="btn cap primary">'
        + ALL_ICONS["PLUS"] + '新しい予定</div></div>'
        + "</div>"
        + '<div class="%s">%s</div>' % (tab_cls, tabbar())
    )


def tabbar():
    items = [("HOME", "ホーム", True), ("CAL", "予定", False),
             ("NOTE", "記録", False), ("USER", "設定", False)]
    return "".join(
        '<div class="tab%s"><span class="ic">%s</span><span class="lb">%s</span></div>'
        % (" on" if on else "", ALL_ICONS[k], jp)
        for k, jp, on in items)


def frame(name, w, h, px, letter, jp, romaji, glass):
    t, v = theme_of(letter)
    return (f'<div class="dev" data-dir="{letter}" data-w="{w}" data-h="{h}" style="{css_vars(v)}">'
            f'<div class="dev-hd"><b>{name}</b><span>{w} × {h} pt</span><em>{px}</em><i>{jp}</i></div>'
            f'<div class="screen" style="width:{w}px;height:{h}px">{screen(glass,h)}</div></div>')


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F1EEE8;color:#2A2723;
  font-family:"Hiragino Sans","Yu Gothic","Noto Sans JP","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased}
.board{padding:52px 26px 60px}
.mast{display:flex;justify-content:space-between;align-items:flex-end;
  border-bottom:1px solid #CFC8BA;padding-bottom:20px;margin-bottom:34px}
.k{font-size:10.5px;letter-spacing:.32em;color:#A29A8C;text-transform:uppercase}
.mast h1{font-size:30px;font-weight:700;letter-spacing:.06em;margin:9px 0 8px}
.mast h1 em{font-style:normal;font-size:13px;font-weight:600;color:#8A8375;letter-spacing:.1em}
.mast .s{font-size:12.5px;line-height:1.85;color:#6E695E;max-width:760px}
.badge{border:1px solid #CFC8BA;border-radius:999px;padding:7px 15px;
  font-size:10.5px;letter-spacing:.18em;color:#6E695E;white-space:nowrap}

/* 方向分组 */
.dir-grp{margin-bottom:46px}
.dir-hd{display:flex;align-items:baseline;gap:12px;margin-bottom:16px;
  border-left:3px solid #2A2723;padding-left:12px}
.dir-hd b{font-size:17px;font-weight:700;letter-spacing:.08em}
.dir-hd span{font-size:10px;letter-spacing:.22em;color:#8A8375}
.dir-hd em{font-style:normal;font-size:11px;color:#6E695E;margin-left:auto}

/* 机型行 */
.row{display:flex;gap:18px;flex-wrap:wrap}
.dev{background:#FDFCFA;border:1px solid #D8D2C6;border-radius:14px;padding:12px}
.dev-hd{font-size:10px;letter-spacing:.1em;color:#6E695E;margin-bottom:9px;
  display:flex;gap:7px;align-items:baseline;flex-wrap:wrap}
.dev-hd b{font-size:11px;color:#2A2723;font-weight:700}
.dev-hd em{font-style:normal;color:#8A8375}
.dev-hd i{font-style:normal;margin-left:auto;font-weight:700}
.dev-hd i[data-l="A"],.dev-hd i[data-l="A"]{color:#8A6248}
.screen{position:relative;overflow:hidden;border-radius:9px;
  background:var(--bg);color:var(--ink);font-size:11px}

/* 状态栏（62pt 上安全区） */
.sb{height:62px;display:flex;align-items:flex-end;justify-content:space-between;
  padding:0 22px 7px;font-size:12px;font-weight:600;position:relative;z-index:3}
.sb .isl{position:absolute;left:50%;top:12px;transform:translateX(-50%);
  width:88px;height:25px;border-radius:999px;background:#0D0C0F}
.sb .r{display:flex;align-items:center;gap:5px;color:var(--ink)}
.sb .bat{width:22px;height:11px;border:1px solid currentColor;border-radius:3px;
  position:relative;opacity:.9}
.sb .bat::after{content:"";position:absolute;inset:1.5px;right:5px;background:currentColor;border-radius:1px}

/* 导航（玻璃 / 实体） */
.nav{position:relative;z-index:2;display:flex;align-items:center;gap:10px;
  padding:6px 16px 14px}
.nav.glass{background:color-mix(in srgb,var(--bg) 72%,transparent);
  backdrop-filter:blur(22px) saturate(1.7);-webkit-backdrop-filter:blur(22px) saturate(1.7)}
.nav .big{font-size:27px;font-weight:700;letter-spacing:.1em}
.nav .sub{font-size:10px;color:var(--faint);letter-spacing:.12em;align-self:flex-end;
  padding-bottom:4px}
.nav .act{margin-left:auto;width:44px;height:44px;border-radius:999px;
  display:flex;align-items:center;justify-content:center;color:var(--accent-text)}
.nav .act svg{width:19px;height:19px}

/* 内容区（edge-to-edge：内容穿到 Tab 栏下方） */
.scroll{padding:0 16px 40px;position:relative}
.hero{border-radius:12px;padding:14px 15px;margin-bottom:11px;
  background:linear-gradient(135deg,var(--accent-soft),var(--surface));
  display:flex;align-items:center;gap:11px;border:1px solid var(--line)}
.hero .sun{width:26px;height:26px;border-radius:999px;background:var(--tone2);flex:none}
.hero .tx b{display:block;font-size:13px;font-weight:700}
.hero .tx span{font-size:10px;color:var(--sub)}
.sched{display:flex;gap:9px;align-items:flex-start;background:var(--surface);
  border:1px solid var(--line);border-radius:10px;padding:11px 13px;margin-bottom:8px}
.sched .bar{width:3px;border-radius:999px;background:var(--accent);align-self:stretch;flex:none}
.sched.t2 .bar{background:var(--tone2)}
.sched.t3 .bar{background:var(--tone3)}
/* i18n: 本地化时间格式（"14:30 Uhr"=50px / "7:00 a. m."=49px）超固定宽；
   改 min-width + auto。现内容 "15:00" 远窄于 56px，min-width 仍主导 => 渲染等价。 */
.sched .tm{min-width:56px;width:auto;flex:none;font-size:10px}
.sched .tm b{display:block;font-size:12px;font-weight:700}
.sched .tm span{color:var(--faint)}
.sched h5{font-size:12.5px;font-weight:700;margin-bottom:2px}
.sched p{font-size:10.5px;color:var(--sub)}

/* CTA */
.cta-wrap{padding-top:4px}
.btn{display:inline-flex;align-items:center;gap:8px;height:50px;padding:0 22px;
  background:var(--accent);color:var(--on-accent);font-size:13.5px;font-weight:600;
  border-radius:999px}
.btn svg{width:15px;height:15px}

/* Tab 栏（D 玻璃 / A-C 实体），底边贴下安全区上沿 34pt */
.tabbar{position:absolute;left:14px;right:14px;bottom:34px;height:54px;
  border-radius:999px;display:flex;align-items:center;justify-content:space-around;
  background:var(--surface);border:1px solid var(--line);z-index:4}
.tabbar.glass{background:color-mix(in srgb,var(--surface) 68%,transparent);
  backdrop-filter:blur(26px) saturate(1.8);-webkit-backdrop-filter:blur(26px) saturate(1.8);
  border-color:color-mix(in srgb,var(--line) 60%,transparent);
  box-shadow:0 6px 22px color-mix(in srgb,var(--ink) 12%,transparent)}
.tab{display:flex;flex-direction:column;align-items:center;gap:3px;min-height:44px;
  justify-content:center;color:var(--faint);flex:1;min-width:0}
.tab.on{color:var(--accent-text)}
.tab .ic svg{width:22px;height:22px;display:block}
/* i18n: min-width:0 让 flex 子项可收缩；标签单行截断。
   德语 Einstellungen=66px / 可用 73px（实测余量仅 7px），DT 放大或窄屏（393pt）即溢出。 */
.tab .lb{font-size:9px;letter-spacing:.06em;display:block;max-width:100%;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gtab-hint{position:absolute;left:14px;right:14px;bottom:8px;text-align:center;
  font-size:8.5px;color:var(--faint);z-index:5}

/* 汇总表 */
.sec-tag{display:flex;align-items:baseline;gap:11px;margin:8px 0 18px}
.sec-tag h2{font-size:19px;font-weight:700;letter-spacing:.07em}
.sec-tag .en{font-size:10px;letter-spacing:.2em;color:#8A8375}
.sec-tag::after{content:"";flex:1;height:1px;background:#CFC8BA}
table{width:100%;border-collapse:collapse;background:#FDFCFA;
  border:1px solid #D8D2C6;border-radius:12px;overflow:hidden;font-size:12px}
th,td{padding:11px 13px;text-align:left;border-bottom:1px solid #E8E3D8}
th{background:#F4F1EA;font-size:10.5px;letter-spacing:.14em;color:#6E695E;
  font-weight:700;text-transform:uppercase}
tr:last-child td{border-bottom:none}
td.ok{color:#4E7A55;font-weight:700}
td.num{font-family:ui-monospace,Consolas,monospace;font-size:11.5px}
.dot{display:inline-block;width:9px;height:9px;border-radius:999px;margin-right:7px;
  vertical-align:middle}
.notes{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:26px}
.box{background:#FBFAF7;border:1px solid #D8D2C6;border-radius:12px;padding:15px 17px}
.box h4{font-size:13px;font-weight:700;letter-spacing:.04em;margin-bottom:8px}
.box h4 span{font-size:9.5px;letter-spacing:.16em;color:#8A8375;font-weight:600;margin-left:7px}
.box p{font-size:11.5px;line-height:1.85;color:#55514A}
.box p b{color:#211F1A}
.box code{font-family:ui-monospace,Consolas,monospace;font-size:11px;background:#EDE8DD;
  padding:1px 5px;border-radius:4px}
.ok{color:#4E7A55;font-weight:700}
.warn{color:#B4493A;font-weight:700}
.foot{margin-top:42px;text-align:center;font-size:9.5px;letter-spacing:.26em;color:#9C958A}
"""

# --- i18n：devices CSS 所辖选择器的拉丁降档（语种列表复用 build.LAT_LANG_SEL）---
# devices.html 有独立 CSS（不含 build.CSS），故 --ff-lat 变量不可用，字体栈写字面值。
# 未列入的选择器（.dir-hd b .08 / .tab .lb .06 / .sec-tag h2 .07 / .box h4 .04 / .mast h1 .06）
# 属 UI 组件层字距，拉丁语系可原样保留。
DEV_I18N_CSS = """
%(S)s body{font-family:%(LAT)s}
/* devices 行高：CJK 1.85 → 拉丁 1.5 */
%(S)s :is(.mast .s,.box p){line-height:1.5}
/* devices 字距 3a 长文本/标题 → .02em */
%(S)s :is(.dev-hd,.nav .big,.mast h1 em){letter-spacing:.02em}
/* devices 字距 3b 全大写短标签 → .06em */
%(S)s :is(.k,.badge,.dir-hd span,.nav .sub,.sec-tag .en,th,
          .box h4 span,.foot){letter-spacing:.06em}
""".replace("%(S)s", LAT_LANG_SEL).replace("%(LAT)s", FF_LAT)

CSS = CSS + "\n" + DEV_I18N_CSS


def summary_table():
    rows = []
    for letter, jp, _, _ in DIRECTIONS:
        for name, w, h, _ in DEVICES:
            rows.append(f'<tr><td>{jp}</td><td>{name}</td><td>{w} × {h}</td><td>{w - 32}</td><td>62 / 34（样张预设）</td><td>待浏览器与原生验证</td></tr>')
    return ('<div class="sec-tag"><h2>尺寸配置矩阵</h2></div><div class="kit-table-wrap"><table><thead><tr><th>主题</th><th>设备</th><th>逻辑尺寸</th><th>预设内容宽</th><th>安全区</th><th>验证状态</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


BODY_NOTE = """<div class="kit-note"><b>样张使用范围</b><p>本页展示各主题在四组预设 iPhone 尺寸下的布局。尺寸表是设计输入，不是通过测试的记录。原生安全区须由系统读取；实际字体、触控、横屏、键盘和 VoiceOver 需在支持的设备与系统版本上验证。</p><p>图标按矢量使用；1pt 线条与 1 物理像素发丝线不同。内容允许滚动，末项与操作应能完整移出悬浮栏遮挡区域。内容较少时不补造数据来制造玻璃效果。</p></div>"""


def main():
    groups = []
    for letter, jp, romaji, glass in DIRECTIONS:
        t, v = theme_of(letter)
        mat = "玻璃材质" if glass else "实体表面"
        frames = "".join(frame(n, w, h, px, letter, jp, romaji, glass)
                         for n, w, h, px in DEVICES)
        groups.append(
            '<div class="dir-grp">'
            '<div class="dir-hd" style="border-left-color:%s">'
            '<b>方向 %s · %s</b><span>%s</span><em>%s · %s</em></div>'
            '<div class="row">%s</div></div>' % (
                v["accent"], letter, jp, romaji, mat, v["accent"], frames))

    page = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>日式简约 UI Kit · iPhone 设备尺寸样张</title>
<style>%s</style></head><body><div class="board">
<div class="mast"><div>
  <div class="k">JP MINIMAL UI KIT — DEVICE LAYOUT SAMPLES</div>
  <h1>iPhone 16 尺寸样张 <em>全部主题 · 预设逻辑尺寸</em></h1>
  <div class="s">每套主题共用四组设备尺寸。样张安全区上 62pt / 下 34pt，供设计比较；实际运行时读取系统安全区。当前展示为竖屏 HTML，不代表真机验收通过。</div>
</div><div class="badge">HTML · PT 参考</div></div>
%s
%s
%s
<div class="foot">JP MINIMAL UI KIT · 全部注册主题 · IPHONE 16 系列 HTML 样张 · GENERATED BY build_devices.py</div>
</div></body></html>""" % (CSS, "".join(groups), summary_table(), BODY_NOTE)

    # <html lang> 的唯一事实源是模块级 LANG。模板内写的是字面值，此处按 LANG 覆盖，
    # 使二者不可能漂移：改 LANG 会同时改变 _BLOCK_H 取值与本行输出，且失配会被下面挡住。
    page, _nsub = re.subn(r'<html lang="[^"]*">', '<html lang="%s">' % LANG, page, count=1)
    if _nsub != 1:
        raise SystemExit("[build_devices] 模板中 <html lang> 未被替换（n=%d），请检查模板。" % _nsub)

    page = prepare_page(page, "devices.html")
    page = page.replace("</head>", "<style>.screen .scroll{position:absolute;inset:126px 0 0;overflow-y:auto;padding:0 16px 120px}.dev{max-width:100%;overflow-x:auto}.screen .sched h5{font-size:15px}.screen .sched p{font-size:13px}.mast{flex-wrap:wrap;gap:16px}.k,.dir-hd span,.mast h1 em,.dev-hd em{color:#675D51}</style></head>")
    path = os.path.join(OUT, "devices.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    # 写盘复核：以磁盘内容为准，不信任内存变量
    want = '<html lang="%s">' % LANG
    if want not in open(path, encoding="utf-8").read():
        raise SystemExit("[build_devices] 写盘复核失败：%s 未出现在 %s" % (want, path))
    log.info("written %s (%.1f KB)", os.path.basename(path), os.path.getsize(path) / 1024)
    for letter, jp, romaji, glass in DIRECTIONS:
        for n, w, h, px in DEVICES:
            log.info("  %s %-6s %-18s %3d x %3d pt", letter, jp, n, w, h)


if __name__ == "__main__":
    main()
