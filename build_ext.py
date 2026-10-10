# -*- coding: utf-8 -*-
"""
JP Minimal UI Kit - Extension pages generator
Generates per theme: {x}-ext.html (dark mode / sheet / empty / onboarding / charts)
Shared: icons.html (icon design rules + library), rewrites index.html
Run: python build_ext.py
"""
import logging
import os
from string import Template
from design_tokens import finish_palette
from site_support import prepare_page, index_page, standards_page
from build import (THEMES, ICONS, CSS, hc_vars, derive, a11y_css,
                   LAT_LANG_SEL, FF_LAT)

OUT = os.path.dirname(os.path.abspath(__file__))
log = logging.getLogger("build_ext")
if not log.handlers:                      # 显式绑定，避免被上层 basicConfig 劫持
    log.setLevel(logging.INFO)
    log.propagate = False
    _fh = logging.FileHandler(os.path.join(OUT, "build_ext.log"), encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _sh = logging.StreamHandler()
    _sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(_fh)
    log.addHandler(_sh)


# ------------------------------------------------------- dark token sets ----
DARK = {
    "A": dict(
        bg="#1B1A16", surface="#242320", fill="#2E2C27", fill_strong="#3B3831", elev="#3E3B33",
        ink="#EDE9DF", sub="#B3ADA0", faint="#928B7C",
        line="#322F29", line_strong="#45423A",
        accent="#B08A6C", accent_deep="#CBA788", accent_soft="#2E2823",
        danger="#D0705F", danger_soft="#2F1F1C",
        tone2="#C2A878", soft2="#35301F", tone3="#93A5B3", soft3="#2A313A",
        stamp="#D56055", sun="#E08573", sat="#8CA8C9",
        toast_bg="#3E3B33", toast_fg="#EDE9DF",
        on_accent="#1B1A16", on_danger="#1B1A16", on_stamp="#1B1A16",
    ),
    "B": dict(
        bg="#171C24", surface="#1F252F", fill="#262D38", fill_strong="#333B48", elev="#414A58",
        ink="#E9EDF3", sub="#A6B0BC", faint="#848E9B",
        line="#2B323D", line_strong="#3A4350",
        accent="#7FA3CC", accent_deep="#A8C3E2", accent_soft="#2A3646",
        danger="#DB8A7E", danger_soft="#3B2A28",
        tone2="#86BFA9", soft2="#22352F", tone3="#AE9FD1", soft3="#2C2940",
        stamp="#E0685C", sun="#E08A7E", sat="#93AED1",
        toast_bg="#39414E", toast_fg="#E9EDF3",
        on_accent="#171C24", on_danger="#171C24", on_stamp="#171C24",
    ),
    "C": dict(
        bg="#181C16", surface="#20251E", fill="#272D24", fill_strong="#343B2F", elev="#414A3C",
        ink="#E9EFE4", sub="#A5B29D", faint="#829079",
        line="#2C3328", line_strong="#3B4436",
        accent="#93B07F", accent_deep="#AEC89C", accent_soft="#2C3527",
        danger="#D48A6F", danger_soft="#38291F",
        tone2="#C7AE7E", soft2="#35301F", tone3="#95AACA", soft3="#252E3B",
        stamp="#D9604F", sun="#DE8573", sat="#8FAAC6",
        toast_bg="#3A4235", toast_fg="#E9EFE4",
        on_accent="#181C16", on_danger="#181C16", on_stamp="#181C16",
    ),
    # E 青磁：深色不是反相，是按 4.2 从 A/B/C 实测 HSL 规律重新推导
    # （同族 token 跟随 E 色相 H158；语义色 danger/stamp/sun/sat 保持绝对色相，四套一致）
    "E": dict(
        bg="#161C1A", surface="#1E2524", fill="#262F2D", fill_strong="#303C39", elev="#3C4A46",
        ink="#E4F0ED", sub="#9FB4AE", faint="#7C928B",
        line="#283330", line_strong="#384743",
        accent="#78B7A3", accent_deep="#94D0BE", accent_soft="#273531",
        danger="#D57E6E", danger_soft="#372421",
        tone2="#C5B580", soft2="#35301F", tone3="#95AACA", soft3="#27303D",
        stamp="#D95D50", sun="#DE8675", sat="#8CA8C9",
        toast_bg="#35423F", toast_fg="#E4F0ED",
        on_accent="#161C1A", on_danger="#161C1A", on_stamp="#161C1A",
    ),
    # F 桜色：深色重新推导。桜粉在深底上需提亮并略增饱和，
    # 否则会发灰成「脏粉」；底色保持极淡的暖墨，不用纯黑。
    "F": dict(
        bg="#1E1918", surface="#272120", fill="#302827", fill_strong="#3C3230", elev="#4A3E3B",
        ink="#F3E7E4", sub="#C4A9A4", faint="#9C837E",
        line="#332B29", line_strong="#463B38",
        accent="#F0BDB4", accent_deep="#F8D3CB", accent_soft="#3A2A27",
        danger="#E08A7B", danger_soft="#3D2724",
        tone2="#C9B694", soft2="#38301F", tone3="#9BB0C4", soft3="#28303B",
        stamp="#E06758", sun="#E89080", sat="#A2B8CE",
        toast_bg="#4A3E3B", toast_fg="#F3E7E4",
        on_accent="#1E1918", on_danger="#1E1918", on_stamp="#1E1918",
    ),
}
DARK.update({t["letter"]: t["dark_vars"] for t in THEMES if "dark_vars" in t})
DARK = {key: finish_palette(value, False) for key, value in DARK.items()}

DARK_SWATCH = {key: [(label, p[token]) for label, token in
    (("墨底","bg"),("面","surface"),("浮","elev"),("字","ink"),("主色","accent"),("线","line_strong"))]
    for key,p in DARK.items()}

# ------------------------------------------------------------- new icons ----
def _svg(inner, sw=1.6):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')

NEW_ICONS = dict(
    # --- 通用 UI ---
    BOOKMARK=_svg('<path d="M6.6 3.8h10.8a1.2 1.2 0 0 1 1.2 1.2v15.6L12 16.2l-6.6 4.4V5a1.2 1.2 0 0 1 1.2-1.2z"/>'),
    CLOCK=_svg('<circle cx="12" cy="12" r="9"/><polyline points="12 6.8 12 12 15.6 14.4"/>'),
    STAR=_svg('<path d="M12 3.2l2.7 5.5 6 .9-4.35 4.2 1.03 6L12 16.98 6.62 19.8l1.03-6L3.3 9.6l6-.9z"/>'),
    X=_svg('<line x1="6.2" y1="6.2" x2="17.8" y2="17.8"/><line x1="17.8" y1="6.2" x2="6.2" y2="17.8"/>', 1.8),
    EDIT=_svg('<path d="M16.9 3.6a2.12 2.12 0 0 1 3 3L8.4 18.1l-4.4 1.3 1.3-4.4z"/><line x1="14.5" y1="6" x2="17.4" y2="8.9"/>'),
    TRASH=_svg('<path d="M4.2 6.8h15.6"/><path d="M9.2 6.8V5a1.6 1.6 0 0 1 1.6-1.6h2.4A1.6 1.6 0 0 1 14.8 5v1.8"/><path d="M6.4 6.8l1 12.9a1.8 1.8 0 0 0 1.8 1.7h5.6a1.8 1.8 0 0 0 1.8-1.7l1-12.9"/><line x1="10.2" y1="10.6" x2="10.2" y2="17.2"/><line x1="13.8" y1="10.6" x2="13.8" y2="17.2"/>'),
    DOWNLOAD=_svg('<path d="M12 3.6v11.6"/><polyline points="7.4 10.8 12 15.4 16.6 10.8"/><line x1="4.4" y1="20" x2="19.6" y2="20"/>'),
    UPLOAD=_svg('<path d="M12 15.6V4"/><polyline points="7.4 8.4 12 3.8 16.6 8.4"/><line x1="4.4" y1="20" x2="19.6" y2="20"/>'),
    EYE=_svg('<path d="M2.6 12S6.2 5.9 12 5.9 21.4 12 21.4 12 17.8 18.1 12 18.1 2.6 12 2.6 12z"/><circle cx="12" cy="12" r="3"/>'),
    FILTER=_svg('<path d="M3.6 5.4h16.8l-6.6 7.7v5.7l-3.6 2v-7.7z"/>'),
    CHEV_U=_svg('<polyline points="5.6 14.8 12 8.4 18.4 14.8"/>'),
    CHEV_D=_svg('<polyline points="5.6 9.2 12 15.6 18.4 9.2"/>'),
    # --- 衣 · 穿搭购物 ---
    TSHIRT=_svg('<path d="M8.4 3.6L3.8 6l1.8 3.8 1.8-.6v11.2h9.2V9.2l1.8.6L20.2 6l-4.6-2.4a3.6 3.6 0 0 1-7.2 0z"/>'),
    SHIRT=_svg('<path d="M9 3.4L5 5.4l1.6 3.6 1.4-.5v12.1h8V8.5l1.4.5L19 5.4l-4-2-1.6 1.8h-2.8z"/><path d="M9 3.4L12 6l3-2.6"/><path d="M12 11v.01M12 15v.01"/>'),
    PANTS=_svg('<path d="M6.4 3.4h11.2l-.9 17.2h-3.9L12 12.4l-.8 8.2H7.3z"/><line x1="6.6" y1="6.8" x2="17.4" y2="6.8"/>'),
    COAT=_svg('<path d="M8.8 3.4L4.4 5.8v14.8h6.2V7zM15.2 3.4l4.4 2.4v14.8h-6.2V7z"/><path d="M8.8 3.4L12 7l3.2-3.6"/>'),
    DRESS=_svg('<path d="M9.6 3.6L12 6.4l2.4-2.8"/><path d="M9.6 6.6L8 8.8l4 1.4 4-1.4-1.6-2.2"/><path d="M8 8.8L5.6 20.6h12.8L16 8.8"/>'),
    SHOE=_svg('<path d="M3 17.6v-3.4l5.4-.6 3.6-3 1.9 1.3 2.5.5c2.6.5 4.6 1.7 4.6 3.3v1.9z"/><path d="M3 20.2h18"/>'),
    BAG=_svg('<path d="M4.6 8.4h14.8l1 12H3.6z"/><path d="M8.8 8.4V6a3.2 3.2 0 0 1 6.4 0v2.4"/>'),
    BACKPACK=_svg('<path d="M5.6 9.8a6.4 6.4 0 0 1 12.8 0v10.6H5.6z"/><path d="M9.4 7.2V6a2.6 2.6 0 0 1 5.2 0v1.2"/><rect x="9" y="13" width="6" height="4" rx="1.2"/>'),
    UMBRELLA=_svg('<path d="M12 3.4a8.8 8.8 0 0 1 8.8 8.8H3.2A8.8 8.8 0 0 1 12 3.4z"/><path d="M12 12.2v5.6a2.4 2.4 0 0 1-4.8 0"/><line x1="12" y1="1.8" x2="12" y2="3.4"/>'),
    GLASSES=_svg('<circle cx="6.4" cy="13.4" r="3.4"/><circle cx="17.6" cy="13.4" r="3.4"/><path d="M9.8 13.4c1.4-1 3-1 4.4 0"/><path d="M3 13.4l1.8-4.2M21 13.4l-1.8-4.2"/>'),
    WATCH=_svg('<circle cx="12" cy="12" r="5.6"/><polyline points="12 8.8 12 12 14.2 13.4"/><path d="M9 7.2l.4-3.8h5.2l.4 3.8M9 16.8l.4 3.8h5.2l.4-3.8"/>'),
    CART=_svg('<circle cx="9.4" cy="20.2" r="1.5"/><circle cx="17.4" cy="20.2" r="1.5"/><path d="M2.8 3.8h2.4l2.6 11.6h9.8l2-8.4H6.2"/>'),
    GIFT=_svg('<rect x="3.6" y="8.4" width="16.8" height="4" rx="1"/><path d="M5.2 12.4v8h13.6v-8"/><line x1="12" y1="8.4" x2="12" y2="20.4"/><path d="M12 8.4S11 3.8 8.4 3.8a2.3 2.3 0 0 0 0 4.6zM12 8.4s1-4.6 3.6-4.6a2.3 2.3 0 0 1 0 4.6z"/>'),
    # --- 食 · 餐饮厨房 ---
    RICE=_svg('<path d="M3.8 11h16.4a8.2 8.2 0 0 1-8.2 7.8A8.2 8.2 0 0 1 3.8 11z"/><path d="M8.6 20.8h6.8"/><path d="M9 7.6c-.8-1 0-2 .8-2.6M12.4 7c-.9-1.2 0-2.3.9-3M15.8 7.6c-.8-1 0-2 .8-2.6"/>'),
    BOWL=_svg('<path d="M3.4 10.6h17.2a8.6 8.6 0 0 1-8.6 8.2 8.6 8.6 0 0 1-8.6-8.2z"/><path d="M8.8 20.8h6.4"/><line x1="9.6" y1="9.4" x2="20.4" y2="4.2"/><line x1="11.8" y1="9.8" x2="21.4" y2="6.6"/>'),
    BREAD=_svg('<path d="M5 9.6c0-3 3.1-5.2 7-5.2s7 2.2 7 5.2c0 1.5-1 2.2-1 3.2v7.2H6v-7.2c0-1-1-1.7-1-3.2z"/>'),
    MEAT=_svg('<path d="M13.6 3.8c4.8.6 7.2 3.8 6.8 8-.4 4.4-4 7.8-8.6 7.6-4.4-.2-7.8-3.2-7.8-7.4 0-2.2 1-3.4 2.2-4.8 1.2-1.4 2.6-3.9 7.4-3.4z"/><path d="M9.4 8.6c2-1.4 4.6-1.4 6.4 0"/>'),
    FISH=_svg('<path d="M16.4 12c-1.8 3-4.6 4.6-7.8 4.6-2.4 0-4.2-.9-5.2-2l2.2-2.6-2.2-2.6c1-1.1 2.8-2 5.2-2 3.2 0 6 1.6 7.8 4.6z"/><path d="M16.4 8.4l3.8-2.6v12.4l-3.8-2.6"/><path d="M6.6 10.6v.01"/>'),
    EGG=_svg('<path d="M12 3.4c4.8 0 8.4 3.6 8.4 8s-3.6 8.4-8.4 8.4-8.4-3.6-8.4-8c0-2.4 1.2-3.8 2.4-5.2C7.2 5.2 8.4 3.4 12 3.4z"/><circle cx="12" cy="11.6" r="3"/>'),
    VEGETABLE=_svg('<path d="M15.2 6.8l2.4 2.4L5.4 21.4z"/><path d="M16.4 6.2l1.4-2.4M15 5.6l-.4-2.8M17.8 7l2.6-1"/>'),
    APPLE=_svg('<path d="M12 7.4c-1.4-1-3-1.4-4.4-.8-2.2.9-3.4 3.4-3 6.2.4 3.2 2.6 6.6 4.8 7.2 1 .3 1.8-.2 2.6-.2s1.6.5 2.6.2c2.2-.6 4.4-4 4.8-7.2.4-2.8-.8-5.3-3-6.2-1.4-.6-3-.2-4.4.8z"/><path d="M12 7V4.4M12 5c1.8-2.2 4-2.4 5.4-1.8-.4 2-2 3.4-4.2 3.4"/>'),
    BANANA=_svg('<path d="M4.8 6.2c.8 7 5.6 12 12.4 12.4 1.6.1 2.6-.6 2.4-1.8-.8-4.6-4.4-8.4-9.6-9.8-1.8-.5-3.4-.9-4-1.8-.4-.6-1.4-.4-1.2 1z"/>'),
    CAKE=_svg('<path d="M3.8 13.4l8.2-4.4 8.2 4.4v6.8H3.8z"/><path d="M3.8 17h16.4"/><line x1="12" y1="9" x2="12" y2="5.6"/><path d="M12 5.6c-.8-.8-.8-1.8 0-2.6.8.8.8 1.8 0 2.6"/>'),
    ICE=_svg('<path d="M7.8 10.6a4.2 4.2 0 1 1 8.4 0z"/><path d="M8.6 10.6h6.8L12 21z"/><path d="M9.4 6.8c1.6-1 3.6-1 5.2 0"/>'),
    COFFEE=_svg('<path d="M4.8 8.8h11.4v6a4.7 4.7 0 0 1-4.7 4.7H9.5a4.7 4.7 0 0 1-4.7-4.7z"/><path d="M16.2 10.4h1.9a2.7 2.7 0 0 1 0 5.4h-1.9"/><path d="M8.2 4.6v2M11.4 3.9v2.7"/>'),
    TEA=_svg('<path d="M5 8.8h11v5.6a5.5 5.5 0 0 1-11 0z"/><path d="M16 10h1.6a2.4 2.4 0 0 1 0 4.8H16"/><line x1="3.4" y1="20.4" x2="17.6" y2="20.4"/><path d="M8.4 5.8c-.6-.8 0-1.6.6-2.2M11.8 5.8c-.6-.8 0-1.6.6-2.2"/>'),
    CUP=_svg('<path d="M6.4 3.8h11.2l-1.4 16.4H7.8z"/><line x1="7.2" y1="10.6" x2="16.8" y2="10.6"/>'),
    FORK=_svg('<path d="M7 3.4v6a2.4 2.4 0 0 0 4.8 0v-6M9.4 9.4V21"/><path d="M17.4 3.4c-1.6 1.4-2.4 3.4-2.4 5.6 0 1.6.8 2.4 2.4 2.6V21"/>'),
    CHOPSTICKS=_svg('<line x1="4.6" y1="8.6" x2="19.4" y2="5.4"/><line x1="4.6" y1="12.6" x2="19.4" y2="9.4"/><path d="M4 17.8c3 1.4 6.6 1.8 10 1.2"/>'),
    POT=_svg('<path d="M4.8 10.4h14.4v6a4 4 0 0 1-4 4H8.8a4 4 0 0 1-4-4z"/><path d="M3 10.4h18"/><line x1="10.6" y1="7.6" x2="13.4" y2="7.6"/><path d="M12 7.6V5.2"/><path d="M4.8 13H3.2M20.8 13h-1.6"/>'),
    FRIDGE=_svg('<rect x="6" y="2.8" width="12" height="18.4" rx="2.4"/><line x1="6" y1="9.6" x2="18" y2="9.6"/><line x1="8.8" y1="5.6" x2="8.8" y2="7.6"/><line x1="8.8" y1="12" x2="8.8" y2="15"/>'),
    # --- 住 · 家居天气 ---
    SOFA=_svg('<path d="M5.6 12.2V7.8a2 2 0 0 1 2-2h8.8a2 2 0 0 1 2 2v4.4"/><path d="M3.2 12.8a1.8 1.8 0 0 1 2.4 1.7v1.3h12.8v-1.3a1.8 1.8 0 1 1 3.6 0v5a1.8 1.8 0 0 1-1.8 1.8H3.8A1.8 1.8 0 0 1 2 19.5v-5c0-.8.5-1.5 1.2-1.7z"/>'),
    BED=_svg('<path d="M2.8 19.6v-8.4M2.8 15.4h18.4v4.2M21.2 15.4v-2a2 2 0 0 0-2-2H10v4"/><rect x="5" y="12.2" width="3.6" height="2.4" rx=".8"/>'),
    LAMP=_svg('<path d="M8.6 3.6h6.8l3 7.2H5.6z"/><line x1="12" y1="10.8" x2="12" y2="18.4"/><path d="M8.4 20.6h7.2l-.8-2.2H9.2z"/>'),
    BATH=_svg('<path d="M3.4 12h17.2v3.4a4.6 4.6 0 0 1-4.6 4.6H8a4.6 4.6 0 0 1-4.6-4.6z"/><path d="M6.2 12V5.6a2.2 2.2 0 0 1 4.4 0v1"/><path d="M6.4 20v1.4M17.6 20v1.4"/>'),
    WASHER=_svg('<rect x="4.4" y="2.8" width="15.2" height="18.4" rx="2.4"/><circle cx="12" cy="14" r="4.6"/><line x1="7" y1="6.6" x2="11" y2="6.6"/><path d="M16.6 6.6h.01"/>'),
    TV=_svg('<rect x="2.8" y="6.4" width="18.4" height="12" rx="2.2"/><path d="M8.4 2.8L12 6.4l3.6-3.6"/><line x1="8" y1="21.2" x2="16" y2="21.2"/>'),
    PLUG=_svg('<path d="M9 3.4v5M15 3.4v5"/><path d="M7 8.4h10v3a5 5 0 0 1-10 0z"/><path d="M12 16.4v4.2"/>'),
    BULB=_svg('<path d="M9.4 16.6a6.4 6.4 0 1 1 5.2 0v2.6H9.4z"/><path d="M10.4 14.2c1-1 2.2-1 3.2 0"/>'),
    DOOR=_svg('<path d="M5.4 21V4.6a1.6 1.6 0 0 1 1.6-1.6h8a1.6 1.6 0 0 1 1.6 1.6V21"/><line x1="3.4" y1="21" x2="20.6" y2="21"/><path d="M14.4 12.4h.01"/>'),
    KEY=_svg('<circle cx="7.8" cy="15.8" r="4.2"/><path d="M10.8 12.8L20.4 3.2M17.4 6.2l2.2 2.2M14.8 8.8l1.8 1.8"/>'),
    BOX=_svg('<path d="M3.4 7.8L12 3.4l8.6 4.4v8.4L12 20.6l-8.6-4.4z"/><path d="M3.4 7.8L12 12.2l8.6-4.4M12 12.2v8.4"/>'),
    SUN=_svg('<circle cx="12" cy="12" r="4.4"/><path d="M12 1.9v2.3M12 19.8v2.3M4.3 4.3l1.6 1.6M18.1 18.1l1.6 1.6M1.9 12h2.3M19.8 12h2.3M4.3 19.7l1.6-1.6M18.1 5.9l1.6-1.6"/>'),
    MOON=_svg('<path d="M20.9 14.7A8.9 8.9 0 0 1 9.3 3.1a8.9 8.9 0 1 0 11.6 11.6z"/>'),
    CLOUD=_svg('<path d="M7.4 18.9h9.9a4.4 4.4 0 0 0 .5-8.8 6.2 6.2 0 0 0-12 1.4 4 4 0 0 0 1.6 7.4z"/>'),
    RAIN=_svg('<path d="M7.4 15.6h9.6a4.2 4.2 0 0 0 .4-8.4 6 6 0 0 0-11.6 1.4 3.8 3.8 0 0 0 1.6 7z"/><path d="M8.6 18.4l-1 2.8M12.4 18.4l-1 2.8M16.2 18.4l-1 2.8"/>'),
    # --- 行 · 出行导航 ---
    CAR=_svg('<path d="M3.6 14.4l1.8-5.4a2.4 2.4 0 0 1 2.2-1.6h8.8a2.4 2.4 0 0 1 2.2 1.6l1.8 5.4v3.4a.8.8 0 0 1-.8.8h-2a.8.8 0 0 1-.8-.8v-1H8v1a.8.8 0 0 1-.8.8h-2a.8.8 0 0 1-.8-.8z"/><line x1="3.6" y1="14.4" x2="20.4" y2="14.4"/><path d="M6.8 16.6h1.4M15.8 16.6h1.4"/>'),
    BUS=_svg('<rect x="4.2" y="3.4" width="15.6" height="14.4" rx="2.6"/><line x1="4.2" y1="9.4" x2="19.8" y2="9.4"/><path d="M7.2 17.8v2M16.8 17.8v2"/><line x1="7" y1="14.4" x2="8.8" y2="14.4"/><line x1="15.2" y1="14.4" x2="17" y2="14.4"/>'),
    TRAIN=_svg('<rect x="5.4" y="3.4" width="13.2" height="13.6" rx="3.4"/><path d="M5.4 10.6h13.2"/><line x1="8.4" y1="13.8" x2="9.6" y2="13.8"/><line x1="14.4" y1="13.8" x2="15.6" y2="13.8"/><path d="M8 17.4l-2.2 3.2M16 17.4l2.2 3.2"/><line x1="5" y1="20.6" x2="19" y2="20.6"/>'),
    SUBWAY=_svg('<path d="M3.4 20.6v-8.6a8.6 8.6 0 0 1 17.2 0v8.6"/><rect x="8.4" y="11" width="7.2" height="6.4" rx="1.8"/><line x1="8.4" y1="14.2" x2="15.6" y2="14.2"/><path d="M9.8 17.4v1.6M14.2 17.4v1.6"/>'),
    PLANE=_svg('<path d="M10.2 3.2a1.7 1.7 0 0 1 3.3 0l1.3 6.6 6 3.4v2.4l-6.4-2-.8 4 2.4 1.8v1.8l-4.1-1.2-4.1 1.2v-1.8l2.4-1.8-.8-4-6.4 2v-2.4l6-3.4z"/>'),
    SHIP=_svg('<path d="M3.8 14.4l1.6 5a2.4 2.4 0 0 0 2.3 1.8h8.6a2.4 2.4 0 0 0 2.3-1.8l1.6-5z"/><path d="M8.4 14.4V7.4h7.2v7"/><line x1="12" y1="7.4" x2="12" y2="3.4"/><path d="M12 3.8l4.6 2-4.6 1.8"/>'),
    BIKE=_svg('<circle cx="5.8" cy="17" r="3.6"/><circle cx="18.2" cy="17" r="3.6"/><path d="M5.8 17l4-7.6h5.2M9.8 9.4l4 7.6 4.4-7.6M13.8 9.4l1.6-3h3M7.6 9.4h4"/>'),
    WALK=_svg('<circle cx="13" cy="4.6" r="2"/><path d="M10 21.4l2.2-6-2.4-2.4.8-4.4 3.4 1.4 1.6 2.8 2.8 1M12.2 15.4l3 2 1.2 3.6M9.2 8.8L5.6 10.2"/>'),
    NAVI=_svg('<path d="M20.8 3.6L3.8 10.8l6.8 2.6 2 7.4z"/><path d="M10.6 13.4l5.4-5.2"/>'),
    PIN=_svg('<path d="M12 21.4s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10.3" r="2.6"/>'),
    MAP=_svg('<path d="M9.4 5.8L3.4 3.4v14.8l6 2.4 5.2-2.4 6 2.4V5.8l-6-2.4z"/><line x1="9.4" y1="5.8" x2="9.4" y2="20.6"/><line x1="14.6" y1="3.4" x2="14.6" y2="18.2"/>'),
    COMPASS=_svg('<circle cx="12" cy="12" r="9"/><path d="M15.8 8.2l-2 5.6-5.6 2 2-5.6z"/>'),
    SIGNAL=_svg('<rect x="8.4" y="2.8" width="7.2" height="14.4" rx="2.6"/><circle cx="12" cy="6.4" r="1.2"/><circle cx="12" cy="10" r="1.2"/><circle cx="12" cy="13.6" r="1.2"/><path d="M12 17.2v4"/>'),
    GAS=_svg('<path d="M4.4 21V4.8a1.8 1.8 0 0 1 1.8-1.8h5.6a1.8 1.8 0 0 1 1.8 1.8V21"/><line x1="3" y1="21" x2="15" y2="21"/><rect x="6.2" y="6" width="5.2" height="4" rx=".8"/><path d="M13.6 8.4h2.2a2 2 0 0 1 2 2v6.4a1.6 1.6 0 0 0 3.2 0V9.6l-2-2.4"/>'),
    PARKING=_svg('<rect x="3.6" y="3.6" width="16.8" height="16.8" rx="3.2"/><path d="M9.4 17.2V7.4h3.4a3 3 0 0 1 0 6H9.4"/>'),
    LUGGAGE=_svg('<rect x="5.6" y="7.4" width="12.8" height="12.4" rx="2.4"/><path d="M9.4 7.4V4.8a1.6 1.6 0 0 1 1.6-1.6h2a1.6 1.6 0 0 1 1.6 1.6v2.6"/><line x1="12" y1="10.4" x2="12" y2="16.8"/><path d="M7.6 19.8v1.4M16.4 19.8v1.4"/>'),
    # --- 娱 · 兴趣健康 ---
    MUSIC=_svg('<path d="M9 18.2V6.4l10.4-2.2v11.4"/><ellipse cx="6.4" cy="18.2" rx="2.6" ry="2.2"/><ellipse cx="16.8" cy="15.6" rx="2.6" ry="2.2"/>'),
    HEADPHONE=_svg('<path d="M4 14v-2.6a8 8 0 0 1 16 0V14"/><rect x="2.8" y="13.4" width="4.4" height="6.8" rx="2"/><rect x="16.8" y="13.4" width="4.4" height="6.8" rx="2"/>'),
    MIC=_svg('<rect x="9" y="2.8" width="6" height="11" rx="3"/><path d="M5.6 11.4a6.4 6.4 0 0 0 12.8 0"/><line x1="12" y1="17.8" x2="12" y2="21.2"/><line x1="8.8" y1="21.2" x2="15.2" y2="21.2"/>'),
    FILM=_svg('<path d="M3.6 9.2L5.4 4l14.8 2.8-.8 2.4"/><line x1="3.4" y1="9.2" x2="20.6" y2="9.2"/><path d="M4 9.2h16v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/>'),
    GAME=_svg('<path d="M7.4 7.6h9.2a5 5 0 0 1 4.9 4l.9 5.2a2.6 2.6 0 0 1-4.9 1.4l-1.3-2.2H8.8l-1.3 2.2a2.6 2.6 0 0 1-4.9-1.4l.9-5.2a5 5 0 0 1 4.9-4z"/><path d="M7 11v3M5.5 12.5h3"/><path d="M15.8 11.6h.01M17.8 13.6h.01"/>'),
    CAMERA=_svg('<path d="M4 8h3l1.5-2.2h7L17 8h3a1.6 1.6 0 0 1 1.6 1.6v8.8A1.6 1.6 0 0 1 20 20H4a1.6 1.6 0 0 1-1.6-1.6V9.6A1.6 1.6 0 0 1 4 8z"/><circle cx="12" cy="13.6" r="3.4"/>'),
    IMAGE=_svg('<rect x="3" y="4.6" width="18" height="14.8" rx="2.2"/><circle cx="8.6" cy="10" r="1.5"/><polyline points="3.8 17.4 9 12.6 13 16 16 13.4 20.4 17.2"/>'),
    BOOK=_svg('<path d="M12 6.6C10.8 5.4 9.2 4.7 7 4.7c-1.4 0-2.6.3-3.6.8v13c1-.5 2.2-.8 3.6-.8 2.2 0 3.8.7 5 1.9 1.2-1.2 2.8-1.9 5-1.9 1.4 0 2.6.3 3.6.8v-13c-1-.5-2.2-.8-3.6-.8-2.2 0-3.8.7-5 1.9z"/><line x1="12" y1="6.6" x2="12" y2="19.6"/>'),
    PALETTE=_svg('<path d="M12 3.2a8.8 8.8 0 0 0 0 17.6c1.4 0 2-.8 2-1.8 0-1.4-1-1.8-1-3 0-.8.6-1.4 1.6-1.4h1.8a4.4 4.4 0 0 0 4.4-4.4c0-3.9-3.9-7-8.8-7z"/><circle cx="7.8" cy="11.4" r="1.1"/><circle cx="11" cy="7.6" r="1.1"/><circle cx="15.6" cy="8.6" r="1.1"/>'),
    RUN=_svg('<circle cx="14.6" cy="4.4" r="2"/><path d="M7 21.4l3.4-5.2-2-3 .8-4.6 4 1.6 1 3 3.4 1.2M10.4 16.2l3.6 1.6 1.4 3.6M9.2 8.8L5.4 10"/>'),
    DUMBBELL=_svg('<path d="M6.4 8v8M4 9.8v4.4M17.6 8v8M20 9.8v4.4M6.4 12h11.2"/>'),
    YOGA=_svg('<circle cx="12" cy="5" r="2.2"/><path d="M12 8v5.4M5.6 19.8c2-1.4 4.2-2 6.4-2s4.4.6 6.4 2M12 10.4L7.4 12M12 10.4l4.6 1.6"/>'),
    BALL=_svg('<circle cx="12" cy="12" r="9"/><path d="M12 7.6l4 3-1.6 4.6h-4.8L8 10.6z"/><path d="M12 3v4.6M4.2 9.4L8 10.6M19.8 9.4L16 10.6M7 20l2.6-4.8M17 20l-2.6-4.8"/>'),
    SWIM=_svg('<path d="M2.8 17.4c1.4-1.2 2.8-1.2 4.2 0s2.8 1.2 4.2 0 2.8-1.2 4.2 0 2.8 1.2 4.2 0"/><path d="M2.8 21c1.4-1.2 2.8-1.2 4.2 0s2.8 1.2 4.2 0"/><circle cx="16.6" cy="7.4" r="1.8"/><path d="M4.6 13.8l4-2.6 4.4 1.4 2.8-1.6"/>'),
    HEARTPULSE=_svg('<path d="M20.6 8c0 5.2-8.6 11-8.6 11S3.4 13.2 3.4 8a4.6 4.6 0 0 1 8.6-2.6A4.6 4.6 0 0 1 20.6 8z"/><path d="M6.4 11.4h2.8l1.6-2.6 2.2 4.6 1.4-2h3.2"/>'),
    FIRSTAID=_svg('<rect x="3" y="6.4" width="18" height="13.2" rx="2.6"/><path d="M9 6.4V5a1.8 1.8 0 0 1 1.8-1.8h2.4A1.8 1.8 0 0 1 15 5v1.4"/><path d="M12 10.4v5.2M9.4 13h5.2"/>'),
    # --- 办 · 沟通办公 ---
    MAIL=_svg('<rect x="3" y="5.4" width="18" height="13.2" rx="2.2"/><polyline points="4 7 12 12.8 20 7"/>'),
    CHAT=_svg('<path d="M21 11.8c0 4.3-4 7.8-9 7.8-1.2 0-2.3-.2-3.4-.6L3.4 20.8l1.7-4.4C3.8 15.2 3 13.6 3 11.8c0-4.3 4-7.8 9-7.8s9 3.5 9 7.8z"/>'),
    PHONE=_svg('<path d="M6.4 3.4h3.2l1.6 4-2.1 1.5a12.6 12.6 0 0 0 5.9 5.9l1.5-2.1 4 1.6v3.2a2 2 0 0 1-2.2 2A17.6 17.6 0 0 1 4.4 5.6a2 2 0 0 1 2-2.2z"/>'),
    VIDEO=_svg('<rect x="2.8" y="6" width="13" height="12" rx="2.6"/><path d="M15.8 13.4l5.4 3.4V7.2l-5.4 3.4z"/>'),
    FOLDER=_svg('<path d="M3.4 6.6a2 2 0 0 1 2-2h3.7a2 2 0 0 1 1.5.7l1.2 1.5h6.8a2 2 0 0 1 2 2v8.7a2 2 0 0 1-2 2H5.4a2 2 0 0 1-2-2z"/>'),
    DOC=_svg('<path d="M6.4 2.8h7l4.6 4.6v13.8H6.4z"/><path d="M13.4 2.8v4.6h4.6"/><line x1="9" y1="12.4" x2="15" y2="12.4"/><line x1="9" y1="16" x2="13.6" y2="16"/>'),
    CLIP=_svg('<path d="M20 11.2l-8 8a5 5 0 0 1-7-7l8.4-8.4a3.4 3.4 0 0 1 4.8 4.8L9.6 17a1.8 1.8 0 0 1-2.5-2.5l7.8-7.8"/>'),
    PENCIL=_svg('<path d="M4 20.4l1-4.2L16.4 4.8a2.1 2.1 0 0 1 3 3L8 19.2z"/><path d="M14.4 6.8l2.8 2.8"/>'),
    WALLET=_svg('<rect x="3" y="6" width="18" height="13" rx="2.6"/><circle cx="16.8" cy="12.5" r="1.25"/>'),
    CARD=_svg('<rect x="2.8" y="5" width="18.4" height="14" rx="2.6"/><line x1="2.8" y1="9.8" x2="21.2" y2="9.8"/><line x1="6.4" y1="14.4" x2="10.4" y2="14.4"/>'),
    CHART=_svg('<line x1="4.6" y1="20" x2="4.6" y2="11"/><line x1="12" y1="20" x2="12" y2="4.4"/><line x1="19.4" y1="20" x2="19.4" y2="13.8"/><line x1="2.8" y1="20.6" x2="21.2" y2="20.6"/>'),
    CHECKLIST=_svg('<line x1="8.4" y1="5.4" x2="20.6" y2="5.4"/><line x1="8.4" y1="12" x2="20.6" y2="12"/><line x1="8.4" y1="18.6" x2="20.6" y2="18.6"/><polyline points="3.4 5.8 4.4 6.8 6.2 4.4"/><polyline points="3.4 12.4 4.4 13.4 6.2 11"/><polyline points="3.4 19 4.4 20 6.2 17.6"/>'),
    UNLOCK=_svg('<rect x="4" y="10.6" width="16" height="10.6" rx="2.2"/><path d="M7.8 10.6V7a4.2 4.2 0 0 1 8.2-1.2"/>'),
    # --- 批次新增（第一批 18 枚）---
    HAT=_svg('<path d="M6.8 13.4V9.6a5.2 5.2 0 0 1 10.4 0v3.8"/><path d="M3.6 13.4h16.8a1.9 1.9 0 0 1 0 3.8H3.6a1.9 1.9 0 0 1 0-3.8z"/><path d="M6.9 12.2h10.2"/>'),
    SCARF=_svg('<path d="M7.6 3.6h8.8v5.2a4.4 4.4 0 0 1-8.8 0z"/><path d="M9.2 13.2v6.4l-1.4 1.6 1.4 1.2"/><path d="M14.8 13.2v6.4l1.4 1.6-1.4 1.2"/><path d="M9.6 6.4h4.8"/>'),
    GLOVE=_svg('<path d="M8.4 11.4V5.6a1.7 1.7 0 0 1 3.4 0v4.4"/><path d="M11.8 10V4.8a1.7 1.7 0 0 1 3.4 0v5.4"/><path d="M15.2 10.6V7.4a1.7 1.7 0 0 1 3.4 0v7.4a6 6 0 0 1-6 6h-1.4a5.6 5.6 0 0 1-5.6-5.6v-3.4a1.7 1.7 0 0 1 3-1.1"/>'),
    SUSHI=_svg('<rect x="4.4" y="11.6" width="15.2" height="8.4" rx="3.6"/><path d="M4.4 15.8h15.2"/><path d="M6 8.8c1.7-1.4 3.7-2 6-2s4.3.6 6 2"/><path d="M9 7V4.6M12 6.7V4.2M15 7V4.6"/>'),
    ONIGIRI=_svg('<path d="M12 3.4a2 2 0 0 1 1.7 1l6.1 10.6a2 2 0 0 1-1.7 3H5.9a2 2 0 0 1-1.7-3L10.3 4.4a2 2 0 0 1 1.7-1z"/><path d="M6.4 14.2h11.2v3.8H6.4z"/>'),
    BENTO=_svg('<rect x="3.4" y="7.6" width="17.2" height="11.6" rx="2.4"/><path d="M3.4 12h17.2"/><path d="M8.6 7.6V5.4a1.8 1.8 0 0 1 1.8-1.8h3.2a1.8 1.8 0 0 1 1.8 1.8v2.2"/><circle cx="8.4" cy="15.2" r="1.3"/><circle cx="15.6" cy="15.2" r="1.3"/>'),
    CHAIR=_svg('<path d="M7 3.6h10v11.8H7z"/><path d="M7 15.4h10"/><path d="M8.4 15.4v5M15.6 15.4v5"/><path d="M8.4 10.4h7.2"/>'),
    TABLE=_svg('<path d="M3.4 10.6h17.2"/><path d="M5.2 10.6v9.8M18.8 10.6v9.8"/><path d="M5.2 15.4h13.6"/>'),
    MIRROR=_svg('<ellipse cx="12" cy="10" rx="6.4" ry="7.6"/><path d="M9 7.6a3.6 3.6 0 0 1 4.4-1.2"/><path d="M12 17.6v2.8M9.6 20.4h4.8"/>'),
    TAXI=_svg('<path d="M4.6 17.4v-5.2l1.8-4.2h11.2l1.8 4.2v5.2"/><path d="M4.6 12.2h14.8"/><circle cx="7.8" cy="17.4" r="1.7"/><circle cx="16.2" cy="17.4" r="1.7"/><path d="M9.8 8v-2h4.4v2"/>'),
    TICKET=_svg('<path d="M3.4 7.6a1.8 1.8 0 0 1 1.8-1.8h13.6a1.8 1.8 0 0 1 1.8 1.8v2.2a2.2 2.2 0 0 0 0 4.4v2.2a1.8 1.8 0 0 1-1.8 1.8H5.2a1.8 1.8 0 0 1-1.8-1.8z"/><path d="M8.6 5.8v12.4" stroke-dasharray="2 2.2"/>'),
    PASSPORT=_svg('<rect x="5.4" y="3.4" width="13.2" height="17.2" rx="2"/><circle cx="12" cy="10.2" r="3.2"/><path d="M8.8 16.6h6.4"/><path d="M9.4 10.2h5.2"/>'),
    DICE=_svg('<rect x="4.4" y="4.4" width="15.2" height="15.2" rx="3"/><circle cx="9" cy="9" r="1.1" fill="currentColor" stroke="none"/><circle cx="15" cy="15" r="1.1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.1" fill="currentColor" stroke="none"/>'),
    PAD=_svg('<path d="M8.2 8.4h7.6a5.6 5.6 0 0 1 5.4 6.9l-.5 2.1a1.9 1.9 0 0 1-3.4.7l-1.4-2.1H8.1l-1.4 2.1a1.9 1.9 0 0 1-3.4-.7l-.5-2.1a5.6 5.6 0 0 1 5.4-6.9z"/><path d="M8 11.4v2.4M6.8 12.6h2.4"/><circle cx="15.6" cy="11.8" r=".9" fill="currentColor" stroke="none"/><circle cx="17.6" cy="13.8" r=".9" fill="currentColor" stroke="none"/>'),
    BOOK2=_svg('<path d="M4.4 4.6a1.6 1.6 0 0 1 1.6-1.6h4.4a2.4 2.4 0 0 1 1.6.6v15.8a2.4 2.4 0 0 0-1.6-.6H6a1.6 1.6 0 0 0-1.6 1.6z"/><path d="M19.6 4.6a1.6 1.6 0 0 0-1.6-1.6h-4.4a2.4 2.4 0 0 0-1.6.6v15.8a2.4 2.4 0 0 1 1.6-.6h4.4a1.6 1.6 0 0 1 1.6 1.6z"/>'),
    PRINTER=_svg('<path d="M7.2 9.2V4.4h9.6v4.8"/><rect x="3.6" y="9.2" width="16.8" height="7.6" rx="2"/><path d="M7.2 14.2h9.6v5.4H7.2z"/><circle cx="17.2" cy="11.8" r=".8" fill="currentColor" stroke="none"/>'),
    STAMP=_svg('<path d="M9 3.6h6a2.4 2.4 0 0 1 2.4 2.4v2A4.4 4.4 0 0 1 15 12.4h-6A4.4 4.4 0 0 1 6.6 8V6A2.4 2.4 0 0 1 9 3.6z"/><path d="M4.4 16.4h15.2v3.2a1.2 1.2 0 0 1-1.2 1.2H5.6a1.2 1.2 0 0 1-1.2-1.2z"/><path d="M8.2 15h7.6"/>'),
    CALC=_svg('<rect x="5.4" y="3.4" width="13.2" height="17.2" rx="2"/><rect x="8" y="6.4" width="8" height="3" rx=".8"/><circle cx="9" cy="13" r=".9" fill="currentColor" stroke="none"/><circle cx="12" cy="13" r=".9" fill="currentColor" stroke="none"/><circle cx="15" cy="13" r=".9" fill="currentColor" stroke="none"/><circle cx="9" cy="16.8" r=".9" fill="currentColor" stroke="none"/><circle cx="12" cy="16.8" r=".9" fill="currentColor" stroke="none"/><circle cx="15" cy="16.8" r=".9" fill="currentColor" stroke="none"/>'),
    # --- 批次新增（第二批 31 枚）---
    BELT=_svg('<rect x="3.4" y="9.4" width="17.2" height="5.2" rx="1.2"/><rect x="10.4" y="8.4" width="3.2" height="7.2" rx="1"/><path d="M10.4 12h3.2"/>'),
    TIE=_svg('<path d="M12 3.4l2.4 1.8-1 2.2 1.8 10.4-3.2 3.4-3.2-3.4L10.6 7.4l-1-2.2z"/>'),
    SOCK=_svg('<path d="M8.4 3.6h5.2v8.2l4 3.6a2.6 2.6 0 0 1-1.8 4.6h-1.4a3.4 3.4 0 0 1-2.4-1l-3.6-3.4z"/><path d="M8.4 7.4h5.2"/>'),
    DRESS2=_svg('<path d="M9.4 3.6h5.2v3.4l4.4 8.8a2 2 0 0 1-1.8 2.9H6.8a2 2 0 0 1-1.8-2.9L9.4 7z"/><path d="M9.4 7h5.2"/>'),
    SUNGLASSES=_svg('<path d="M3.6 7.4h16.8"/><path d="M5.6 7.4v3.4a3 3 0 0 0 6 0V7.4"/><path d="M12.4 7.4v3.4a3 3 0 0 0 6 0V7.4"/>'),
    NECKLACE=_svg('<path d="M5 4.4a8.4 8.4 0 0 0 14 0"/><circle cx="12" cy="17" r="3"/><path d="M12 14v-1.4M12 20v1"/>'),
    POUCH=_svg('<rect x="4.4" y="8.4" width="15.2" height="10.8" rx="2.4"/><path d="M4.4 12.6h15.2"/><path d="M9.4 8.4V6.6a2.6 2.6 0 0 1 5.2 0v1.8"/>'),
    FITTING=_svg('<path d="M12 4.6a2.6 2.6 0 0 1 2.6 2.6H9.4A2.6 2.6 0 0 1 12 4.6z"/><path d="M7.6 9.8h8.8l1.6 10.6H6z"/><path d="M9.4 7.2 12 9.8l2.6-2.6"/>'),
    SALAD=_svg('<path d="M3.6 11.4h16.8a8.4 8.4 0 0 1-8.4 8 8.4 8.4 0 0 1-8.4-8z"/><path d="M8.6 20.6h6.8"/><path d="M9 8.6a2.4 2.4 0 0 1 3.4-2.6"/><circle cx="14.6" cy="7.6" r="2.2"/>'),
    SOUP=_svg('<path d="M4.6 10.4h14.8a7.4 7.4 0 0 1-7.4 7.4 7.4 7.4 0 0 1-7.4-7.4z"/><path d="M8.6 19.6h6.8"/><path d="M9.4 7.4c-.8-1 0-2 .8-2.6M13 7.4c-.9-1.2 0-2.3.9-3"/>'),
    BEER=_svg('<path d="M6.2 7.4h9.6v12.2a1.6 1.6 0 0 1-1.6 1.6H7.8a1.6 1.6 0 0 1-1.6-1.6z"/><path d="M6.2 11.4h9.6"/><path d="M15.8 10.4h1.8a2.4 2.4 0 0 1 2.4 2.4v3.4a2.4 2.4 0 0 1-2.4 2.4h-1.8"/><path d="M8.6 4.6v1.4M12 4v2"/>'),
    CABINET=_svg('<rect x="4.4" y="3.4" width="15.2" height="17.2" rx="1.8"/><path d="M4.4 12h15.2"/><path d="M10.8 8h2.4M10.8 16h2.4"/>'),
    SHOWER=_svg('<path d="M12 3.4v3.4"/><path d="M12 6.8 6.4 12.4"/><path d="M4.2 14.4a3 3 0 0 1 4.4-2.6l1.6 1-1.6 1a3 3 0 0 1-4.4.6z"/><path d="M13.4 11v1M16.4 13v1M13.4 15.4v1M16.4 17.4v1M19.4 15v1"/>'),
    AIRCON=_svg('<rect x="3.4" y="5.4" width="17.2" height="6.8" rx="1.8"/><path d="M6.4 9.6h11.2"/><path d="M7.4 15v3.4M12 15.6v2.8M16.6 15v3.4"/>'),
    VACUUM=_svg('<path d="M8.4 20.4h6.2a1.8 1.8 0 0 0 1.8-1.8v-7.2a3.4 3.4 0 0 0-3.4-3.4H11"/><circle cx="7.4" cy="19.4" r="1.5"/><circle cx="15.6" cy="19.4" r="1.5"/><path d="M11 8V4.6h4.6"/>'),
    PLANT=_svg('<path d="M12 20.4v-6"/><path d="M12 14.4c-3.4 0-5.6-2-5.6-5.4 3.4 0 5.6 2 5.6 5.4z"/><path d="M12 14.4c3.4 0 5.6-2 5.6-5.4-3.4 0-5.6 2-5.6 5.4z"/><path d="M8.4 20.4h7.2"/>'),
    TRUCK=_svg('<path d="M2.6 16.4V7.6h11.2v8.8"/><path d="M13.8 10.4h3.6l3.4 3.4v2.6"/><circle cx="6.6" cy="17.6" r="1.8"/><circle cx="17.4" cy="17.6" r="1.8"/><path d="M13.8 16.4h1.8M8.4 16.4h5.4"/>'),
    MOTORBIKE=_svg('<circle cx="6.4" cy="16.6" r="3.2"/><circle cx="17.6" cy="16.6" r="3.2"/><path d="M6.4 16.6l3.2-6h4l1.6 4.6"/><path d="M13.6 10.6h3.2l.8 3"/><path d="M11 8.6h3.4"/>'),
    ROPEWAY=_svg('<path d="M3.4 5.4l17.2 3.4"/><rect x="6.6" y="9.4" width="10.8" height="7.6" rx="1.6"/><path d="M9.4 9.4V6.2M14.6 9.4V6.9"/><path d="M9.4 13.4h5.2v2.4H9.4z"/>'),
    HOTEL=_svg('<rect x="4.4" y="10.4" width="15.2" height="10.2" rx="1.6"/><path d="M4.4 14.6h15.2"/><circle cx="9" cy="17.4" r="1.2"/><circle cx="15" cy="17.4" r="1.2"/><path d="M7.4 10.4V4.6h9.2v5.8M10.6 7.6h2.8"/>'),
    FERRIS=_svg('<circle cx="12" cy="10.6" r="6.6"/><circle cx="12" cy="10.6" r="1.4"/><path d="M12 4v5.2M12 12v5.2M5.4 10.6h5.2M13.4 10.6h5.2M7.4 6l3.6 3.4M13 13.8l3.6 3.4M16.6 6 13 9.4M11 13.8l-3.6 3.4"/><path d="M8.4 20.6h7.2l-1.6-4.4h-4z"/>'),
    PALETTE2=_svg('<path d="M17.4 3.6a2.2 2.2 0 0 1 3.1 3.1L9.4 17.8l-4.6 1.5 1.5-4.6z"/><path d="M14.6 6.4 17.6 9.4"/><path d="M4.4 20.4h6"/>'),
    MUSICNOTE=_svg('<path d="M9.4 17.6V5.4l9.2-2v11.8"/><circle cx="6.8" cy="17.8" r="2.6"/><circle cx="16" cy="15.2" r="2.6"/>'),
    DANCE=_svg('<circle cx="14.4" cy="4.8" r="1.8"/><path d="M14.6 7l-3 3.4 1.6 3.6"/><path d="M13.2 14 9.6 20.4"/><path d="M11 9.6 6.6 11.8l1.6 3"/><path d="M14.8 9.4l3 1.2 2.4-1.6"/>'),
    TENNIS=_svg('<circle cx="12" cy="12" r="8.4"/><path d="M6 6.6c3 1.4 4.8 3.6 5.4 6.6M18 17.4c-3-1.4-4.8-3.6-5.4-6.6"/>'),
    WALK2=_svg('<circle cx="13.4" cy="4.6" r="1.8"/><path d="M13.8 7.2 11 10.4l1.4 3.4"/><path d="M12.4 13.8 10 20.6"/><path d="M11.4 9.6 7.4 11l-.6 3"/><path d="M14.6 8.8l2.8 1.6"/>'),
    COPY=_svg('<rect x="8.4" y="3.4" width="12.2" height="14.2" rx="1.8"/><path d="M15.6 17.6v1.4a1.8 1.8 0 0 1-1.8 1.8H5.2a1.8 1.8 0 0 1-1.8-1.8V8.2a1.8 1.8 0 0 1 1.8-1.8h1.4"/>'),
    PEN=_svg('<path d="M16.6 3.6 20.4 7.4 8.4 19.4l-4.6 1 1-4.6z"/><path d="M14.4 5.8 18.2 9.6"/><path d="M6.6 15.6l1.8 1.8"/>'),
    RULER=_svg('<rect x="2.6" y="8.4" width="18.8" height="7.2" rx="1.4"/><path d="M6.4 8.4v2.6M9.8 8.4v3.6M13.2 8.4v2.6M16.6 8.4v3.6"/>'),
    STAPLER=_svg('<path d="M3.4 14.6h17.2v2.6a1.6 1.6 0 0 1-1.6 1.6H5a1.6 1.6 0 0 1-1.6-1.6z"/><path d="M4.4 14.6V11a2 2 0 0 1 2-2h11.2"/><path d="M17.6 6.6a2 2 0 0 1 2 2v3h-4"/>'),
    WHITEBOARD=_svg('<rect x="3.4" y="4.4" width="17.2" height="12.2" rx="1.6"/><path d="M7.6 16.6v2.6M16.4 16.6v2.6"/><path d="M7.4 12.2c1.6-2 3-2 4.2-.6s2.4 1.2 3.6-.4"/>'),
)
# Library Wi-Fi uses the shared 24pt grid; the status-bar glyph stays separate.
NEW_ICONS["WIFI"] = _svg('<path d="M3 8a14 14 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 16a4 4 0 0 1 6 0"/><circle cx="12" cy="20" r=".8"/>')
ALL_ICONS = {**ICONS, **NEW_ICONS}

# 图标库目录：7 组；总数由目录计算 (KEY, jp, cn)
CATS = [
    ("通用 UI", "UI BASICS", [
        ("HOME", "ホーム", "首页"), ("SEARCH", "検索", "搜索"), ("FILTER", "フィルタ", "筛选"),
        ("BELL", "通知", "通知"), ("USER", "ユーザー", "用户"), ("SLIDERS", "設定", "设置"),
        ("CAL", "カレンダー", "日历"), ("CLOCK", "時計", "时钟"), ("HEART", "お気に入り", "收藏"),
        ("STAR", "評価", "评分"), ("BOOKMARK", "しおり", "书签"), ("EYE", "表示", "可见"),
        ("NOTE", "メモ", "笔记"), ("EDIT", "編集", "编辑"), ("TRASH", "削除", "删除"),
        ("PLUS", "追加", "添加"), ("CHECK", "完了", "完成"), ("X", "閉じる", "关闭"),
        ("SHARE", "共有", "分享"), ("DOWNLOAD", "保存", "下载"), ("UPLOAD", "アップロード", "上传"),
        ("CHEVR", "次へ", "前进"), ("CHEV_L", "戻る", "返回"), ("CHEV_U", "上へ", "向上"),
        ("CHEV_D", "下へ", "向下"),
    ]),
    ("衣 · 穿搭购物", "FASHION & SHOPPING", [
        ("TSHIRT", "Tシャツ", "T恤"), ("SHIRT", "シャツ", "衬衫"), ("PANTS", "パンツ", "裤装"),
        ("COAT", "コート", "大衣"), ("DRESS", "ワンピース", "连衣裙"), ("SHOE", "スニーカー", "鞋子"),
        ("BAG", "手さげ", "手提包"), ("BACKPACK", "リュック", "双肩包"), ("UMBRELLA", "かさ", "雨伞"),
        ("GLASSES", "メガネ", "眼镜"), ("WATCH", "腕時計", "手表"), ("CART", "カート", "购物车"),
        ("GIFT", "プレゼント", "礼物"),
        ("HAT", "ハット", "帽子"), ("SCARF", "マフラー", "围巾"), ("GLOVE", "てぶくろ", "手套"),
        ("BELT", "ベルト", "腰带"), ("TIE", "ネクタイ", "领带"), ("SOCK", "ソックス", "袜子"), ("DRESS2", "ドレス", "礼服"), ("SUNGLASSES", "サングラス", "墨镜"), ("NECKLACE", "ネックレス", "项链"), ("POUCH", "ポーチ", "小包"), ("FITTING", "試着室", "试衣间"),
    ]),
    ("食 · 餐饮厨房", "FOOD & KITCHEN", [
        ("RICE", "ごはん", "米饭"), ("BOWL", "ラーメン", "面碗"), ("BREAD", "パン", "面包"),
        ("MEAT", "お肉", "肉类"), ("FISH", "魚", "鱼"), ("EGG", "卵", "鸡蛋"),
        ("VEGETABLE", "野菜", "蔬菜"), ("APPLE", "りんご", "苹果"), ("BANANA", "バナナ", "香蕉"),
        ("CAKE", "ケーキ", "蛋糕"), ("ICE", "アイス", "冰激凌"), ("COFFEE", "コーヒー", "咖啡"),
        ("TEA", "お茶", "茶"), ("CUP", "グラス", "水杯"), ("FORK", "カトラリー", "刀叉"),
        ("CHOPSTICKS", "お箸", "筷子"), ("POT", "なべ", "锅"), ("FRIDGE", "冷蔵庫", "冰箱"),
        ("SUSHI", "すし", "寿司"), ("ONIGIRI", "おにぎり", "饭团"), ("BENTO", "おべんとう", "便当"),
        ("SALAD", "サラダ", "沙拉"), ("SOUP", "スープ", "汤"), ("BEER", "ビール", "啤酒"),
    ]),
    ("住 · 家居天气", "HOME & WEATHER", [
        ("SOFA", "ソファ", "沙发"), ("BED", "ベッド", "床"), ("LAMP", "ランプ", "台灯"),
        ("BATH", "よくそう", "浴缸"), ("WASHER", "せんたく機", "洗衣机"), ("TV", "テレビ", "电视"),
        ("WIFI", "Wi-Fi", "无线网络"), ("PLUG", "コンセント", "插座"), ("BULB", "電球", "灯泡"),
        ("DOOR", "ドア", "门"), ("KEY", "かぎ", "钥匙"), ("BOX", "宅配便", "包裹"),
        ("SUN", "はれ", "晴天"), ("MOON", "よる", "夜间"), ("CLOUD", "くもり", "多云"),
        ("RAIN", "あめ", "下雨"),
        ("CHAIR", "いす", "椅子"), ("TABLE", "テーブル", "桌子"), ("MIRROR", "かがみ", "镜子"),
        ("CABINET", "とだな", "柜子"), ("SHOWER", "シャワー", "淋浴"), ("AIRCON", "エアコン", "空调"), ("VACUUM", "そうじ機", "吸尘器"), ("PLANT", "しょくぶつ", "植物"),
    ]),
    ("行 · 出行导航", "TRAVEL & NAVIGATION", [
        ("CAR", "クルマ", "汽车"), ("BUS", "バス", "公交"), ("TRAIN", "でんしゃ", "火车"),
        ("SUBWAY", "ちかてつ", "地铁"), ("PLANE", "ひこうき", "飞机"), ("SHIP", "ふね", "轮船"),
        ("BIKE", "じてんしゃ", "自行车"), ("WALK", "ほこう", "步行"), ("NAVI", "ナビ", "导航"),
        ("PIN", "ピン", "位置"), ("MAP", "ちず", "地图"), ("COMPASS", "コンパス", "指南针"),
        ("SIGNAL", "しんごう", "红绿灯"), ("GAS", "ガソリン", "加油"), ("PARKING", "P", "停车场"),
        ("LUGGAGE", "スーツケース", "行李箱"),
        ("TAXI", "タクシー", "出租车"), ("TICKET", "きっぷ", "车票"), ("PASSPORT", "パスポート", "护照"),
        ("TRUCK", "トラック", "卡车"), ("MOTORBIKE", "バイク", "摩托"), ("ROPEWAY", "ロープウェイ", "缆车"), ("HOTEL", "ホテル", "酒店"), ("FERRIS", "かんらんしゃ", "摩天轮"),
    ]),
    ("娱 · 兴趣健康", "HOBBY & HEALTH", [
        ("MUSIC", "音楽", "音乐"), ("HEADPHONE", "ヘッドホン", "耳机"), ("MIC", "マイク", "麦克风"),
        ("FILM", "えいが", "电影"), ("GAME", "ゲーム", "游戏"), ("CAMERA", "カメラ", "相机"),
        ("IMAGE", "しゃしん", "图片"), ("BOOK", "よみもの", "阅读"), ("PALETTE", "おえかき", "绘画"),
        ("RUN", "ランニング", "跑步"), ("DUMBBELL", "ダンベル", "健身"), ("YOGA", "ヨガ", "瑜伽"),
        ("BALL", "サッカー", "球类"), ("SWIM", "すいえい", "游泳"), ("HEARTPULSE", "しんぱく", "心率"),
        ("FIRSTAID", "きゅうきゅう", "医药"),
        ("DICE", "サイコロ", "骰子"), ("PAD", "ゲームパッド", "手柄"), ("BOOK2", "ほん", "书籍"),
        ("PALETTE2", "ペンキ", "画笔"), ("MUSICNOTE", "おんがく", "乐谱"), ("DANCE", "ダンス", "舞蹈"), ("TENNIS", "テニス", "网球"), ("WALK2", "さんぽ", "散步"),
    ]),
    ("办 · 沟通办公", "WORK & SOCIAL", [
        ("MAIL", "メール", "邮件"), ("CHAT", "メッセージ", "消息"), ("PHONE", "でんわ", "电话"),
        ("VIDEO", "ビデオ", "视频"), ("FOLDER", "フォルダ", "文件夹"), ("DOC", "書類", "文档"),
        ("CLIP", "クリップ", "回形针"), ("PENCIL", "えんぴつ", "铅笔"), ("WALLET", "さいふ", "钱包"),
        ("CARD", "カード", "银行卡"), ("CHART", "とうけい", "统计"), ("CHECKLIST", "チェックリスト", "清单"),
        ("LOCK", "ロック", "锁定"), ("UNLOCK", "かいじょ", "解锁"), ("INFO", "じょうほう", "信息"),
        ("WARN", "ちゅうい", "警告"),
        ("PRINTER", "プリンタ", "打印机"), ("STAMP", "はんこ", "印章"), ("CALC", "でんたく", "计算器"),
        ("COPY", "コピー", "复印"), ("PEN", "ペン", "钢笔"), ("RULER", "定規", "尺子"), ("STAPLER", "ホッチキス", "订书机"), ("WHITEBOARD", "ホワイトボード", "白板"),
    ]),
]

def sub_icons(html):
    html = html.replace("__STATUSBAR__", STATUSBAR)
    html = html.replace("__CALGRID__", cal_grid())
    for k, v in ALL_ICONS.items():
        html = html.replace("__" + k + "__", v)
    return html

STATUSBAR = ('<div class="statusbar"><span>9:41</span><span class="sb-right">'
             '<span class="sig"><i></i><i></i><i></i><i></i></span>'
             '<span class="wifi">__WIFI__</span>'
             '<span class="bat"><i></i></span></span></div>')

# ------------------------------------------------------------------ css ----
EXT_CSS = """
/* ===== nav pills ===== */
.nav-row{display:flex;gap:10px;margin-top:26px;flex-wrap:wrap}
.nav-row a{font-size:calc(11.5px * var(--dt-scale,1));letter-spacing:.1em;color:var(--sub);text-decoration:none;
  border:1px solid var(--line-strong);border-radius:16px;padding:6px 15px;background:var(--surface);
  transition:color .15s,border-color .15s}
.nav-row a:hover{color:var(--accent-text);border-color:var(--accent-text)}
.nav-row a.cur{color:var(--on-accent);background:var(--accent);border-color:var(--accent-text)}

/* ===== dark mode additions ===== */
.toast{background:var(--accent-soft);color:var(--accent-deep)}
.dark .seg .on{background:var(--elev);box-shadow:0 1px 4px rgba(0,0,0,.5)}
.dark .stage{background:rgba(8,7,5,.6)}
.dark .alert{box-shadow:0 18px 44px rgba(0,0,0,.55)}
.dark .screen,.dark.phone-in{box-shadow:0 16px 44px rgba(0,0,0,.5)}
.dark-sw{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.dark-sw span{width:52px;text-align:center}
.dark-sw i{width:40px;height:40px;border-radius:10px;display:block;margin:0 auto 5px;
  border:1px solid rgba(0,0,0,.25)}
.dark-sw em{font-size:calc(8.5px * var(--dt-scale,1));color:var(--faint);font-style:normal;font-family:ui-monospace,Consolas,monospace}
.dark-sw b{display:block;font-size:calc(10px * var(--dt-scale,1));color:var(--sub);margin-bottom:4px;font-weight:500}

/* ===== sheet ===== */
.screen.rel{position:relative;height:648px;padding-bottom:0}
.faded{opacity:.4}
.backdrop{position:absolute;inset:0;background:rgba(18,15,10,.42)}
.sheet{position:absolute;left:0;right:0;bottom:0;background:var(--surface);
  border-radius:18px 18px 0 0;padding:12px 22px 34px;box-shadow:0 -14px 44px rgba(0,0,0,.22)}
.grab{width:36px;height:5px;border-radius:3px;background:var(--fill-strong);margin:0 auto 16px}
.sheet h4{text-align:center;font-size:calc(16px * var(--dt-scale,1));letter-spacing:.06em;margin-bottom:4px}
.sheet .s-sub{text-align:center;font-size:calc(11.5px * var(--dt-scale,1));color:var(--faint);margin-bottom:14px}
.s-opt{display:flex;align-items:center;justify-content:space-between;height:52px;
  font-size:calc(15px * var(--dt-scale,1));border-bottom:1px solid var(--line);cursor:pointer}
.s-opt:last-of-type{border-bottom:none}
.s-opt .ck{width:19px;height:19px;color:var(--accent-text);display:flex}
.s-opt .ck svg{width:19px;height:19px}
.sheet.full{top:36px;bottom:0;display:flex;flex-direction:column;padding:0 22px 34px}
.s-nav{display:flex;align-items:center;justify-content:space-between;height:52px;flex:none}
.s-nav .xi{width:30px;height:30px;border-radius:50%;background:var(--fill);color:var(--sub);
  display:flex;align-items:center;justify-content:center;cursor:pointer}
.s-nav .xi svg{width:14px;height:14px}
.s-nav .t{font-size:calc(15.5px * var(--dt-scale,1));font-weight:700;letter-spacing:.08em}
.s-nav .save{font-size:calc(14.5px * var(--dt-scale,1));font-weight:700;color:var(--accent-text);letter-spacing:.06em;cursor:pointer}
.s-body{flex:1;overflow:hidden}

/* ===== empty state ===== */
.empty{display:flex;flex-direction:column;align-items:center;text-align:center;padding:30px 34px 0}
.empty svg{width:136px;height:108px}
.empty h4{font-size:calc(16.5px * var(--dt-scale,1));margin-top:22px;letter-spacing:.08em}
.empty p{font-size:calc(12.5px * var(--dt-scale,1));color:var(--faint);line-height:2;margin-top:9px}
.empty .btn{width:auto;padding:0 36px;height:44px;margin-top:24px;font-size:calc(14.5px * var(--dt-scale,1))}
.e-head{padding:6px 2px 0}
.e-head .big{font-size:calc(24px * var(--dt-scale,1));font-weight:700;letter-spacing:.08em}

/* ===== onboarding ===== */
.screen.ob-scr{height:700px;padding-bottom:0;display:flex;flex-direction:column}
.ob-top{display:flex;justify-content:flex-end;padding:2px 24px 0;font-size:calc(11.5px * var(--dt-scale,1));
  color:var(--faint);letter-spacing:.14em;flex:none}
.ob{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;
  padding:0 32px 36px}
.ob .illus{margin-top:26px;width:236px;height:164px}
.ob h3{font-size:calc(21px * var(--dt-scale,1));letter-spacing:.14em;margin-top:34px}
.ob .en-t{font-size:calc(9.5px * var(--dt-scale,1));letter-spacing:.32em;color:var(--faint);margin-top:11px;text-transform:uppercase}
.ob p{font-size:calc(12.5px * var(--dt-scale,1));color:var(--sub);line-height:2.15;margin-top:16px;max-width:264px}
.ob .dots{display:flex;gap:7px;margin-top:28px;align-items:center}
.dots i{width:6px;height:6px;border-radius:50%;background:var(--fill-strong);display:block}
.dots i.on{width:22px;border-radius:3px;background:var(--accent)}
.ob .cta{margin-top:auto;width:100%}
.ob .step{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.24em;color:var(--faint);margin-bottom:10px}

/* ===== charts ===== */
.chart-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-card);
  padding:16px 15px 13px}
.chart-card + .chart-card{margin-top:14px}
.ch-title{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px}
.ch-title b{font-size:calc(13px * var(--dt-scale,1));letter-spacing:.1em;font-weight:700}
.ch-title span{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
.cap-row{display:flex;justify-content:space-between;font-size:calc(10px * var(--dt-scale,1));color:var(--faint);
  margin-top:9px;letter-spacing:.06em}
.stat-row{display:flex;gap:10px;margin-bottom:14px}
.stat{flex:1;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-in);
  padding:12px 13px}
.stat .v{font-size:calc(19px * var(--dt-scale,1));font-weight:700;letter-spacing:.02em}
.stat .l{font-size:calc(9.5px * var(--dt-scale,1));color:var(--faint);letter-spacing:.14em;margin-top:3px}
.stat .d{font-size:calc(10px * var(--dt-scale,1));margin-top:7px;letter-spacing:.04em}
.d.up{color:var(--tone2-text)}.d.down{color:var(--danger)}
.bar-labels{display:flex;margin-top:8px;padding:0 4px}
.bar-labels span{flex:1;text-align:center;font-size:calc(9.5px * var(--dt-scale,1));color:var(--faint);letter-spacing:.06em}
.bar-labels span.on{color:var(--accent-text);font-weight:700}
.donut-row{display:flex;align-items:center;gap:16px}
.donut-legend{flex:1}
.dl{display:flex;align-items:center;gap:8px;font-size:calc(11.5px * var(--dt-scale,1));color:var(--sub);padding:5px 0}
.dl i{width:8px;height:8px;border-radius:3px;display:block;flex:none}
.dl b{margin-left:auto;font-size:calc(11.5px * var(--dt-scale,1));color:var(--ink);font-weight:600}
.cd-big{font-size:calc(23px * var(--dt-scale,1));font-weight:700;fill:var(--ink)}
.cd-sm{font-size:calc(8px * var(--dt-scale,1));fill:var(--faint);letter-spacing:.2em}
.prog{margin-top:2px}
.prog .p-row{display:flex;justify-content:space-between;font-size:calc(12px * var(--dt-scale,1));margin-bottom:9px;letter-spacing:.04em}
.prog .p-row b{color:var(--accent-text);font-size:calc(11.5px * var(--dt-scale,1))}
.p-track{height:6px;border-radius:3px;background:var(--fill-strong);overflow:hidden}
.p-fill{height:100%;width:68%;border-radius:3px;background:var(--accent)}
.notes.full{width:100%;margin-top:26px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:0 40px}
.g2 h4{margin-top:16px}

/* ===== illustrations ===== */
.illus .muted{stroke:var(--line-strong)}
.illus .fine{stroke:var(--faint)}
.illus .acc{stroke:var(--accent-ui)}
"""

# --- i18n：EXT_CSS 所辖选择器的拉丁降档（语种列表复用 build.LAT_LANG_SEL，勿另抄）---
# 依据 tmp/ls_lh_audit.txt：EXT_CSS 内 字距>=.1em 共 9 条、行高>=1.8 共 2 条。
# 注意 EXT_CSS 含大量字面 %（color-mix / saturate），禁用 % 格式化 —— 一律 .replace()。
EXT_I18N_CSS = """
/* EXT 行高：CJK 2 / 2.15 → 拉丁 1.5 */
%(S)s :is(.empty p,.ob p){line-height:1.5}
/* EXT 字距 3a 长文本/标题 → .02em */
%(S)s :is(.nav-row a,.ob h3,.ch-title b,.stat .l){letter-spacing:.02em}
/* EXT 字距 3b 全大写短标签 → .06em */
%(S)s :is(.ob-top,.ob .en-t,.ob .step,.ch-title span,.cd-sm){letter-spacing:.06em}
""".replace("%(S)s", LAT_LANG_SEL)

EXT_CSS = EXT_CSS + "\n" + EXT_I18N_CSS

# --------------------------------------------------------------- markup ----
DARK_SCREEN = """
<div class="screen dark">
  __STATUSBAR__
  <div class="sec">
    <div class="sec-h"><span class="jp">ダーク · ボタン</span><span class="en">Dark Buttons</span></div>
    <div class="stack">
      <button class="btn btn-primary">続ける</button>
      <button class="btn btn-secondary">キャンセル</button>
      <div class="btn-row">
        <button class="btn btn-soft">下書き保存</button>
        <button class="btn btn-ghost">破棄</button>
      </div>
      <button class="btn btn-danger">削除する</button>
    </div>
    <div class="icon-btns">
      <span class="ibtn">__SEARCH__</span><span class="ibtn">__HEART__</span>
      <span class="ibtn">__SHARE__</span><span class="ibtn fill">__PLUS__</span>
    </div>
  </div>
  <div class="sec">
    <div class="sec-h"><span class="jp">入力とリスト</span><span class="en">Fields · Lists</span></div>
    <div class="field"><div class="input focus">y.taro@example.com</div></div>
    <div class="field"><div class="input error">••••••</div><div class="field-msg">8文字以上で入力してください</div></div>
    <div class="ctl"><div class="ctl-row"><div><div class="ctl-label">通知</div><div class="ctl-sub">プッシュ通知を受け取る</div></div><div class="toggle"></div></div>
    <div class="ctl-row"><div class="ctl-label">ダークモード</div><div class="toggle"></div></div></div>
    <div class="list mt16">
      <div class="li"><span class="li-ic">__USER__</span><div class="li-tx"><b>プロフィール</b><span>名前 · アイコン</span></div><span class="right">__CHEVR__</span></div>
      <div class="li"><span class="li-ic">__BELL__</span><div class="li-tx"><b>通知設定</b></div><span class="right"><span class="bdg">3</span>__CHEVR__</span></div>
    </div>
  </div>
  <div class="sec">
    <div class="sec-h"><span class="jp">フィードバック</span><span class="en">Feedback</span></div>
    <div class="toast-stage"><div class="toast"><span class="ic">__CHECK__</span>保存しました</div></div>
    <div class="banner"><span class="bi">__INFO__</span><span>新しいバージョン（2.1.0）が利用可能です。</span></div>
    <div class="badge-row"><span class="chip">タグ</span><span class="chip on">選択中</span><span class="tag-new">NEW</span></div>
    <div class="cal mt16">
      <div class="cal-h"><span class="nav">__CHEV_L__</span><span class="m">2026年 9月</span><span class="nav">__CHEVR__</span></div>
      <div class="cal-grid">__CALGRID__</div>
    </div>
  </div>
</div>
"""

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

def demo_dark():
    return """
<div class="phone"><div class="phone-in dark">
  <div class="island"></div>
  <div class="scr">
    __STATUSBAR__
    <div class="scr-scroll">
      <div class="scr-head">
        <div>
          <div class="greet">こんばんは ― 秋分の日まで 5 日</div>
          <div class="date-big">9月17日（木）</div>
        </div>
        <div class="avatar">__USER__</div>
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
      <div class="tab on">__HOME__<span>ホーム</span></div>
      <div class="tab">__CAL__<span>カレンダー</span></div>

      <div class="tab">__NOTE__<span>メモ</span></div>
      <div class="tab">__SLIDERS__<span>設定</span></div>
    </div>
  </div>
  <div class="home-bar"></div>
</div></div>
"""

def dark_notes(letter):
    sw = "".join(
        f'<span><b>{n}</b><i style="background:{c}"></i><em>{c}</em></span>'
        for n, c in DARK_SWATCH[letter]
    )
    return f"""
<div class="notes">
  <h3>深色模式规则 <span class="en">Dark Mode</span></h3>
  <h4>底色</h4>
  <ul>
    <li>基底用<b>「墨色」</b>（带主题色相的深灰），绝不用纯黑 #000</li>
    <li>三级明度层级：底 bg → 卡片 surface → 浮起 elev，替代投影分层</li>
  </ul>
  <h4>颜色</h4>
  <ul>
    <li>强调色<b>提亮一档</b>（约 +15~20% 明度）保证暗底对比度</li>
    <li>发丝线改为低透明度浅色（白 8~14%），禁止纯白描边</li>
    <li>警示 / 印章红同步提亮；正文不用纯白，用米白降刺激</li>
  </ul>
  <h4>组件</h4>
  <ul>
    <li>Toast 反转为浮起深灰底；Alert 遮罩加深至 60%</li>
    <li>图表改用低饱和亮色，禁用大面积渐变</li>
    <li>切换动效 0.25s 交叉淡化，跟随系统 appearance</li>
  </ul>
  <h4>暗色 Token</h4>
  <div class="dark-sw">{sw}</div>
</div>
"""

SHEET_HALF = """
<div class="screen rel">
  __STATUSBAR__
  <div class="sec">
    <div class="sec-h"><span class="jp">予定</span><span class="en">Schedule</span></div>
    <div class="stack">
      <div class="sched"><span class="bar"></span><div class="tm"><b>09:30</b>45分</div><div class="bd"><h5>朝会 · チーム共有</h5><p>会議室 A</p></div></div>
      <div class="sched t2"><span class="bar"></span><div class="tm"><b>12:30</b>60分</div><div class="bd"><h5>ランチ · 佐藤さん</h5><p>駅前カフェ</p></div></div>
      <div class="sched t3"><span class="bar"></span><div class="tm"><b>15:00</b>90分</div><div class="bd"><h5>デザインレビュー</h5><p>オンライン</p></div></div>
    </div>
  </div>
  <div class="backdrop"></div>
  <div class="sheet">
    <div class="grab"></div>
    <h4>並び替え</h4>
    <div class="s-sub">予定の表示順を選択</div>
    <div class="s-opt"><span>新しい順</span><span class="ck">__CHECK__</span></div>
    <div class="s-opt"><span>古い順</span></div>
    <div class="s-opt"><span>名前順</span></div>
    <button class="btn btn-primary mt16" style="margin-top:18px">完了</button>
  </div>
</div>
"""

SHEET_FULL = """
<div class="screen rel">
  __STATUSBAR__
  <div class="backdrop"></div>
  <div class="sheet full">
    <div class="grab"></div>
    <div class="s-nav">
      <span class="xi">__X__</span><span class="t">新規予定</span><span class="save">保存</span>
    </div>
    <div class="s-body">
      <div class="field">
        <div class="field-label"><span>タイトル</span><span class="req">必須</span></div>
        <div class="input focus">デザインレビュー</div>
      </div>
      <div class="row-field" style="margin-bottom:14px"><div class="rf-tx"><span class="rf-lab">日時</span><span class="rf-val">9月17日（木）15:00 – 16:30</span></div><span class="chev">__CHEVR__</span></div>
      <div class="field">
        <div class="field-label"><span>カテゴリ</span></div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <span class="chip on">ワーク</span><span class="chip">予定</span><span class="chip">会議</span><span class="chip">プライベート</span>
        </div>
      </div>
      <div class="field">
        <div class="field-label"><span>メモ</span><span class="hint">0 / 200</span></div>
        <div class="textarea" style="min-height:64px"><span class="ph">詳細を入力…</span></div>
      </div>
      <div class="ctl" style="margin-top:4px">
        <div class="ctl-row"><div class="ctl-label">通知</div><div class="toggle"></div></div>
        <div class="ctl-row"><div class="ctl-label">終日の予定</div><div class="toggle off"></div></div>
      </div>
    </div>
    <button class="btn btn-primary" style="margin-top:14px">保存する</button>
  </div>
</div>
"""

SHEET_NOTES = """
<div class="notes">
  <h3>Sheet 弹层规则 <span class="en">Sheets</span></h3>
  <h4>结构</h4>
  <ul>
    <li>抓手 Grabber：<b>36 × 5pt</b>，圆角 2.5，置于顶部居中，距顶 12</li>
    <li>半屏 Sheet 顶部圆角 <b>16~18pt</b>，底部贴安全区（Home 指示条留 34pt）</li>
    <li>遮罩：墨色 40%（深色模式 60%），下层内容保留可见但不可点</li>
  </ul>
  <h4>层级与类型</h4>
  <ul>
    <li><b>半屏</b>：轻选择（排序 / 筛选 / 分享），选项 ≤ 5 行</li>
    <li><b>全屏 Sheet</b>：创建 / 编辑表单，导航栏 = 取消(左) · 标题(中) · 保存(右，强调色)</li>
    <li><b>Action Sheet</b>：含破坏性操作时，危险项置顶标红，取消独立成块与选项隔 8pt</li>
  </ul>
  <h4>交互（HIG）</h4>
  <ul>
    <li>下拉可关闭；表单有改动时下拉弹出「放弃编辑？」确认</li>
    <li>弹出动画 0.3s spring；键盘升起时 Sheet 自动避让</li>
  </ul>
</div>
"""

ILLUS_CAL_MOON = """
<svg class="illus" viewBox="0 0 140 110" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <rect x="32" y="20" width="76" height="68" rx="10" class="muted" stroke-width="2.4"/>
  <path d="M32 40h76" class="muted" stroke-width="2.4"/>
  <path d="M52 13v10M88 13v10" class="muted" stroke-width="2.4"/>
  <path d="M78 51a11 11 0 1 0 0 21 13.5 13.5 0 0 1 0-21z" class="acc" stroke-width="2.4"/>
  <path d="M48.5 56h5M51 53.5v5" class="fine" stroke-width="2"/>
  <path d="M85 76h3.4M86.7 74.3v3.4" class="fine" stroke-width="2"/>
  <ellipse cx="70" cy="101" rx="40" ry="3.6" style="fill:var(--chart-muted)" opacity=".4" stroke="none"/>
</svg>
"""
ILLUS_SEARCH = """
<svg class="illus" viewBox="0 0 140 110" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="62" cy="47" r="26" class="muted" stroke-width="2.4"/>
  <circle cx="62" cy="47" r="17" class="fine" stroke-width="1.8" stroke-dasharray="3 5"/>
  <path d="M81 66l18 18" class="muted" stroke-width="2.4"/>
  <path d="M56.5 41.5l11 11M67.5 41.5l-11 11" class="acc" stroke-width="2.4"/>
  <ellipse cx="68" cy="101" rx="34" ry="3.6" style="fill:var(--chart-muted)" opacity=".4" stroke="none"/>
</svg>
"""
ILLUS_OFFLINE = """
<svg class="illus" viewBox="0 0 140 110" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M48 74h40a16 16 0 0 0 2-31.8A23 23 0 0 0 46.5 47 14.6 14.6 0 0 0 48 74z" class="muted" stroke-width="2.4"/>
  <path d="M36 88L104 32" class="acc" stroke-width="2.4"/>
  <path d="M50 98h40" class="fine" stroke-width="2.2" stroke-dasharray="2 6"/>
</svg>
"""

def empty_screens():
    return f"""
<div class="screen" style="height:560px">
  __STATUSBAR__
  <div class="sec e-head"><div class="big">予定</div></div>
  <div class="empty">{ILLUS_CAL_MOON}
    <h4>今日は予定がありません</h4>
    <p>ゆったり過ごせる一日です。<br>新しい予定を追加してみませんか？</p>
    <button class="btn btn-primary">予定を追加</button>
  </div>
</div>
<div class="screen" style="height:560px">
  __STATUSBAR__
  <div class="sec"><div class="search">__SEARCH__<span style="color:var(--ink)">京都</span></div></div>
  <div class="empty">{ILLUS_SEARCH}
    <h4>見つかりませんでした</h4>
    <p>「京都」に一致する結果はありません。<br>別の言葉で試してみてください。</p>
    <button class="btn btn-soft">条件を変更する</button>
  </div>
</div>
<div class="screen" style="height:560px">
  __STATUSBAR__
  <div class="sec e-head"><div class="big">メモ</div></div>
  <div class="empty">{ILLUS_OFFLINE}
    <h4>オフラインです</h4>
    <p>ネットワークに接続できません。<br>接続を確認して再度お試しください。</p>
    <button class="btn btn-secondary">再読み込み</button>
  </div>
</div>
"""

EMPTY_NOTES = """
<div class="notes full">
  <div class="g2">
    <div>
      <h4 style="margin-top:0">空状态规则</h4>
      <ul>
        <li>插画为<b>匀线线稿</b>，线宽随画幅放大（空态画幅 140 → <b>2.4pt</b> 主线 / 2pt 细节），高分屏下不发虚；主体发丝灰、仅一处强调色点睛，配淡椭圆落影</li>
        <li>文案三段式：<b>状态陈述（发生了什么）→ 安抚/解释 → 引导（下一步）</b>，日语敬体、不用感叹号</li>
        <li>CTA 分级：可行动 → 主按钮；可调整 → 柔底；不可行动（如离线）→ 次级按钮</li>
      </ul>
    </div>
    <div>
      <h4 style="margin-top:0">必备场景清单</h4>
      <ul>
        <li>首次使用空态（带引导 CTA）/ 筛选无结果 / 搜索无结果</li>
        <li>离线 / 加载失败（重试）/ 通知清空 / 收藏为空</li>
        <li>每个空态都要回答：「用户现在能做什么？」</li>
      </ul>
    </div>
  </div>
</div>
"""

ILLUS_MOUNTAIN = """
<svg class="illus" viewBox="0 0 230 160" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="168" cy="44" r="18" class="acc" stroke-width="2.2" style="fill:var(--accent-soft)"/>
  <path d="M54 38q5-5 10 0M74 30q4-4 8 0" class="fine" stroke-width="1.9"/>
  <path d="M18 122l52-64 34 42 22-26 46 48" class="muted" stroke-width="2.6"/>
  <path d="M70 58l14 17 7-8" class="acc" stroke-width="1.9"/>
  <path d="M8 122h214" class="muted" stroke-width="2.6"/>
</svg>
"""
ILLUS_RECORD = """
<svg class="illus" viewBox="0 0 230 160" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <rect x="52" y="22" width="108" height="112" rx="12" class="muted" stroke-width="2.6"/>
  <path d="M74 52h56M74 72h64M74 92h36" class="fine" stroke-width="2.1"/>
  <path d="M74 112l6 6 12-12" class="acc" stroke-width="2.4"/>
  <path d="M148 98l26-26a8.5 8.5 0 0 1 12 12l-26 26-16 4z" class="acc" stroke-width="2.4"/>
  <ellipse cx="110" cy="146" rx="72" ry="4" style="fill:var(--chart-muted)" opacity=".4" stroke="none"/>
</svg>
"""
ILLUS_NIGHT = """
<svg class="illus" viewBox="0 0 230 160" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M126 34a32 32 0 1 0 0 62 36 36 0 0 1 0-62z" class="acc" stroke-width="2.4" style="fill:var(--accent-soft)"/>
  <path d="M58 42h8M62 38v8" class="fine" stroke-width="2"/>
  <path d="M88 74h6M91 71v6" class="fine" stroke-width="2"/>
  <path d="M172 104h6M175 101v6" class="fine" stroke-width="2"/>
  <circle cx="44" cy="88" r="1.8" class="fine" stroke-width="2"/>
  <path d="M58 130a27 27 0 0 1 54 0" class="muted" stroke-width="2.6"/>
  <path d="M14 130h202" class="muted" stroke-width="2.6"/>
</svg>
"""

def ob_screen(step, en, jp_title, desc, illus, dots_on, cta_html, skip=True):
    dots = "".join('<i class="on"></i>' if i == dots_on else "<i></i>" for i in range(3))
    skip_html = '<span>スキップ</span>' if skip else "<span></span>"
    return f"""
<div class="screen ob-scr">
  __STATUSBAR__
  <div class="ob-top">{skip_html}</div>
  <div class="ob">
    <div class="step">STEP {step} / 3 · {en}</div>
    {illus}
    <h3>{jp_title}</h3>
    <p>{desc}</p>
    <div class="dots">{dots}</div>
    <div class="cta">{cta_html}</div>
  </div>
</div>
"""

def onboarding_screens():
    s1 = ob_screen(1, "WELCOME", "はじめに",
                   "朝にひらく、シンプルなスケジュール。<br>今日の予定と一句を、いっしょに。",
                   ILLUS_MOUNTAIN, 0, '<button class="btn btn-ghost">次へ</button>')
    s2 = ob_screen(2, "RECORD", "記録する",
                   "予定もメモも、ワンタップで。<br>書いたものは、あなたの財産になります。",
                   ILLUS_RECORD, 1, '<button class="btn btn-ghost">次へ</button>')
    s3 = ob_screen(3, "KEEP GOING", "つづける",
                   "毎日三行でも、立派な習慣。<br>むりせず、あなたのペースで。",
                   ILLUS_NIGHT, 2, '<button class="btn btn-primary">はじめる</button>', skip=False)
    return f'<div class="cols">{s1}{s2}{s3}</div>{ONBOARD_NOTES}'

ONBOARD_NOTES = """
<div class="notes full">
  <div class="g2">
    <div>
      <h4 style="margin-top:0">引导页规则</h4>
      <ul>
        <li><b>3 页封顶</b>，每页一个信息点；可整页跳过（右上スキップ，末页隐藏）</li>
        <li>插画 = 匀线稿 + 单色点睛 + 大面积留白，与空状态同一套插画语言；线宽随画幅缩放（引导画幅 230 → <b>2.6pt</b>），保持视觉线重恒定</li>
        <li>页点：当前页拉长为圆角条（22pt），其余 6pt 圆点</li>
      </ul>
    </div>
    <div>
      <h4 style="margin-top:0">文案与 CTA</h4>
      <ul>
        <li>标题汉字短语（4~5 字）+ 罗马音/英文小标 + 两行敬体描述</li>
        <li>前两页用幽灵按钮「次へ」降低压迫感，末页主按钮「はじめる」</li>
        <li>支持左右滑动翻页；仅首次启动显示，二次进入直达首页</li>
      </ul>
    </div>
  </div>
</div>
"""

LINE_CHART = """
<svg viewBox="0 0 315 128" style="width:100%" fill="none">
  <line x1="0" y1="18" x2="315" y2="18" style="stroke:var(--line)" stroke-width="1"/>
  <line x1="0" y1="48" x2="315" y2="48" style="stroke:var(--line)" stroke-width="1"/>
  <line x1="0" y1="78" x2="315" y2="78" style="stroke:var(--line)" stroke-width="1"/>
  <line x1="0" y1="108" x2="315" y2="108" style="stroke:var(--line)" stroke-width="1"/>
  <path d="M8 92L45 76L82 82L119 54L156 62L193 38L230 46L267 24L304 32L304 108L8 108Z" style="fill:var(--accent-ui)" opacity=".1" stroke="none"/>
  <path d="M8 92L45 76L82 82L119 54L156 62L193 38L230 46L267 24L304 32" style="stroke:var(--accent-ui)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="304" cy="32" r="6.5" style="fill:var(--accent-ui)" opacity=".18" stroke="none"/>
  <circle cx="304" cy="32" r="3.4" style="fill:var(--accent-ui)" stroke="var(--surface)" stroke-width="1.6"/>
</svg>
"""

def bar_chart():
    hs = [46, 70, 34, 86, 58, 96, 64]
    xs = [15, 59, 103, 147, 191, 235, 279]
    bars = ""
    for x, h, i in zip(xs, hs, range(7)):
        color = "var(--accent)" if i == 5 else "var(--fill-strong)"
        bars += f'<rect x="{x}" y="{110-h}" width="26" height="{h}" rx="7" style="fill:{color}"/>'
    return f"""
<svg viewBox="0 0 315 120" style="width:100%">
  <line x1="0" y1="110" x2="315" y2="110" style="stroke:var(--line)" stroke-width="1"/>
  {bars}
  <text x="248" y="{110-96-8}" text-anchor="middle" class="cv" style="font-size:calc(9px * var(--dt-scale,1));fill:var(--accent-ui);font-weight:700">9,214</text>
</svg>
<div class="bar-labels"><span>月</span><span>火</span><span>水</span><span>木</span><span>金</span><span class="on">土</span><span>日</span></div>
"""

DONUT = """
<div class="donut-row">
  <svg viewBox="0 0 120 120" style="width:118px;flex:none" fill="none">
    <circle cx="60" cy="60" r="46" style="stroke:var(--fill)" stroke-width="10"/>
    <g transform="rotate(-90 60 60)">
      <circle cx="60" cy="60" r="46" style="stroke:var(--accent-ui)" stroke-width="10" stroke-dasharray="130.1 158.9" stroke-dashoffset="0"/>
      <circle cx="60" cy="60" r="46" style="stroke:var(--data2)" stroke-width="10" stroke-dasharray="86.7 202.3" stroke-dashoffset="-130.1"/>
    </g>
    <text x="60" y="58" text-anchor="middle" class="cd-big">75%</text>
    <text x="60" y="74" text-anchor="middle" class="cd-sm">達成率</text>
  </svg>
  <div class="donut-legend">
    <div class="dl"><i style="background:var(--accent)"></i>運動<b>45%</b></div>
    <div class="dl"><i style="background:var(--tone2)"></i>食事<b>30%</b></div>
    <div class="dl"><i style="background:var(--fill-strong)"></i>その他<b>25%</b></div>
  </div>
</div>
"""

CHART_S1 = f"""
<div class="screen">
  __STATUSBAR__
  <div class="sec">
    <div class="sec-h"><span class="jp">統計</span><span class="en">Statistics</span></div>
    <div class="stat-row">
      <div class="stat"><div class="v">6,842</div><div class="l">歩数</div><div class="d up">▲ 12%</div></div>
      <div class="stat"><div class="v">¥4,280</div><div class="l">支出</div><div class="d down">▼ 3%</div></div>
      <div class="stat"><div class="v">7.2h</div><div class="l">睡眠</div><div class="d up">▲ 5%</div></div>
    </div>
    <div class="chart-card">
      <div class="ch-title"><b>週間アクティビティ</b><span>Weekly</span></div>
      {LINE_CHART}
      <div class="cap-row"><span>9/11 → 9/17</span><span>歩数 · 平均 6,842</span></div>
    </div>
    <div class="chart-card">
      <div class="prog">
        <div class="p-row"><span>今週の目標 · 50,000 歩</span><b>68%</b></div>
        <div class="p-track"><div class="p-fill"></div></div>
      </div>
    </div>
  </div>
</div>
"""

CHART_S2 = f"""
<div class="screen">
  __STATUSBAR__
  <div class="sec">
    <div class="sec-h"><span class="jp">曜日別</span><span class="en">By Day</span></div>
    <div class="chart-card">
      <div class="ch-title"><b>歩数 · 曜日別</b><span>Steps</span></div>
      {bar_chart()}
    </div>
    <div class="chart-card">
      <div class="ch-title"><b>カテゴリ</b><span>Category</span></div>
      {DONUT}
    </div>
    <div class="chart-card">
      <div class="ch-title"><b>今日の記録</b><span>Today</span></div>
      <div class="ctl" style="margin-top:-6px">
        <div class="ctl-row"><div class="ctl-label">水分 6 / 8 杯</div><div style="display:flex;gap:4px"><i style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--fill-strong);display:block"></i><i style="width:8px;height:8px;border-radius:50%;background:var(--fill-strong);display:block"></i></div></div>
      </div>
    </div>
  </div>
</div>
"""

CHART_NOTES = """
<div class="notes">
  <h3>图表规则 <span class="en">Charts</span></h3>
  <h4>视觉</h4>
  <ul>
    <li>网格 = 1px 发丝线，最多 4 条；<b>保留必要刻度、单位与数值摘要</b>，数值可在图中或可访问的数据列表中读取</li>
    <li>折线 2pt 圆角连接，面积填充 = 主色 10% 透明度；当前点加光晕</li>
    <li>柱状：非活跃柱用 fill-strong 中性灰，<b>仅高亮柱用主色</b></li>
    <li>环形：10pt 环宽、平头端点，中心放大数字 + 小标签</li>
  </ul>
  <h4>数据色板</h4>
  <ul>
    <li>序列使用可辨识的数据色；分类图表同时提供文字、数值或形状提示</li>
    <li>涨跌语义随业务地区配置，必须同时显示正负号或方向文字，不能只靠颜色</li>
    <li>深色模式使用独立语义数据色，按实际背景验证对比度</li>
  </ul>
</div>
"""

# ------------------------------------------------------------ ext builder ---
def _nav_links():
    """导航胶囊的全量链接（单一事实源）。

    ⚠️ D 不在 THEMES（独立 build_d.py），必须显式补入，否则导航里会缺 D。
    ⚠️ E 在 THEMES 内，**自动包含** —— 此前的硬编码列表漏了 E，
       导致所有页面的导航都点不到 E（2026-09-18 修复）。
    顺序：总览 → 各方向基础 → 各方向扩展 → 图标规则。
    """
    dirs = [(t["letter"].lower(), t["jp"], t["file"]) for t in THEMES]
    try:
        import build_d
        dirs.append(("d", "紫硝子", "d-murasaki.html"))
    except Exception as e:                                    # noqa: BLE001
        log.warning("direction D missing from nav: %s", e)
    dirs.sort(key=lambda x: x[0])

    links = [("index.html", "总览", "index")]
    for key, jp, f in dirs:
        links.append((f, "%s 基础" % key.upper(), key))
    for key, jp, f in dirs:
        links.append((f.replace(".html", "-ext.html"), "%s 扩展" % key.upper(), key + "-ext"))
    links.append(("icons.html", "图标规则", "icons"))
    return links


def nav_row(cur):
    links = _nav_links()
    a = "".join('<a href="{}"{}>{}</a>'.format(href, ' class="cur"' if key == cur else '', label)
                for href, label, key in links)
    return f'<div class="nav-row">{a}</div>'

EXT_HEADER_TPL = Template("""
<div class="bh">
  <div class="bh-left">
    <div class="appicon"><span class="kanji">$KANJI</span></div>
    <div class="bh-title">
      <div class="kicker">JP MINIMAL UI KIT — DIRECTION $LETTER · EXTENSION — DARK / SHEET / EMPTY / ONBOARDING / CHARTS</div>
      <h1>$JP<span class="romaji">$ROMAJI · 拡張</span></h1>
      <div class="cn">$TAGLINE · 扩展组件篇</div>
      <p class="desc">在基础组件之上补充五类界面要素：深色模式（墨色系三层 elevation）、Sheet 弹层（半屏/全屏）、空状态（匀线插画 + 三段式文案）、引导页（3 步 onboarding）、数据图表（发丝网格 + 单色高亮）。插画线宽随画幅调整，原生渲染单独验收。</p>
      <div class="kw">$KW</div>
    </div>
  </div>
  <div class="tate">墨の階調・静かな夜</div>
  <div class="swatches">$SW</div>
</div>
<div class="tokens">
  <span class="tk"><b>暗底</b>墨色三层 bg → surface → elev</span>
  <span class="tk"><b>Sheet</b>顶角 18 / 抓手 36×5 / 遮罩 40%</span>
  <span class="tk"><b>插画</b>线宽随画幅放大（2.4~2.6pt）</span>
  <span class="tk"><b>图表</b>网格 ≤4 条 / 高亮仅一处</span>
  <span class="tk"><b>强调色</b>独立推导并校验</span>
</div>
""")

# ------------------------------------------------------ a11y section (ext) --
# HC：浅色 .hc / 深色 .dark.hc（同元素）与 .dark .hc（后代，演示面板用），
#     并附 prefers-contrast 媒体查询（真实系统行为）。
# 色值唯一数据源：A/B/C 取 contrast_patch.json；方向 D 不在该文件内，
#     由 build_d_ext 通过 t['hc_light'] / t['hc_dark'] 传入。
A11Y_CSS_TMPL = """
/* ===== 无障碍层 · Increased Contrast + Dynamic Type ===== */
:root{--dt-scale:1}
.hc{__LIGHT_HC__}
.dark.hc{__DARK_HC__}
.dark .hc{__DARK_HC__}
@media (prefers-contrast: more){
  :root{__LIGHT_HC__}
  .dark{__DARK_HC__}
}
/* 演示面板：标准 / 高对比 / 字号阶梯，同一组 token 直接对照 */
.a11y-grid{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
.a11y-grid.dark{background:var(--bg);padding:12px;border-radius:14px;
  border:1px solid var(--line)}
.a11y-cell{flex:1;min-width:148px;background:var(--surface);border:1px solid var(--line);
  border-radius:12px;padding:14px}
.a11y-lab{font-size:calc(10px * var(--dt-scale,1));letter-spacing:.14em;color:var(--faint);
  text-transform:uppercase;margin-bottom:9px}
.a11y-t{font-size:calc(15px * var(--dt-scale,1));color:var(--ink);font-weight:600;line-height:1.4}
.a11y-s{font-size:calc(13px * var(--dt-scale,1));color:var(--sub);margin-top:6px;line-height:1.5}
.a11y-f{font-size:calc(11px * var(--dt-scale,1));color:var(--faint);margin-top:6px}
.a11y-hr{height:1px;background:var(--line);margin:11px 0}
.a11y-hr2{height:1px;background:var(--line-strong);margin-bottom:11px}
.a11y-btn{display:inline-block;background:var(--accent);color:var(--on-accent);
  font-size:calc(14px * var(--dt-scale,1));font-weight:600;padding:8px 18px;border-radius:var(--r-btn)}
"""


def a11y_css_ext(letter, t):
    """浅色/深色 HC 变量串。方向 D 走 t['hc_*']，A/B/C 回落 contrast_patch.json"""
    light = t.get("hc_light") or hc_vars(letter, "light")
    dark = t.get("hc_dark") or hc_vars(letter, "dark")
    return (A11Y_CSS_TMPL.replace("__LIGHT_HC__", light)
                         .replace("__DARK_HC__", dark))


def _a11y_cell(label, cls="", style=""):
    """cls 与 style 必须分开传：合并会产出 class="a11y-cell --dt-scale:1.176" 这类非法类名"""
    c = (" " + cls) if cls else ""
    st = (' style="' + style + '"') if style else ""
    return ('<div class="a11y-cell' + c + '"' + st + '>'
            '<div class="a11y-lab">' + label + '</div>'
            '<div class="a11y-t">本文テキスト</div>'
            '<div class="a11y-s">副次テキスト · 説明文</div>'
            '<div class="a11y-f">補助テキスト · 11px</div>'
            '<div class="a11y-hr"></div><div class="a11y-hr2"></div>'
            '<span class="a11y-btn">続ける</span></div>')


A11Y_NOTES = """
<div class="notes">
  <h3>无障碍规则 <span class="en">Accessibility</span></h3>
  <h4>增强对比度 Increased Contrast</h4>
  <ul>
    <li>系统开启后走 <code>prefers-contrast: more</code>；页内 <code>.hc</code> 类供对照演示</li>
    <li>HC 按浅色与深色分别推导文字、功能图标、控件边界和彩底字色，
        <b>底色与布局一律不动</b>，避免整体重绘</li>
    <li>发丝线在 HC 下提升到 sub 同级明度保证分隔可辨；正文对比不低于 7:1</li>
  </ul>
  <h4>Dynamic Type</h4>
  <ul>
    <li>正文类字号一律写成 <code>calc(Npx * var(--dt-scale,1))</code>，
        由 <code>--dt-scale</code> 统一驱动；原生工程使用系统 Text Style，单独验证各档位</li>
    <li>阶梯：標準 1.0 / 大 1.176 / 特大 1.41 / 排版压力 1.75×（仅为 HTML 比例演示，不对应 iOS 系统档位）</li>
    <li>放大时容器必须能撑高，禁止固定高度裁切；单行标题允许换行</li>
    <li>SwiftUI 侧直接用系统 Text Style（body / footnote / caption…），系统自动缩放</li>
  </ul>
</div>
"""


def a11y_section():
    def col(no, en, cn, inner, flex=False):
        w = ' style="width:auto;flex:1"' if flex else ''
        return ('<div class="col"' + w + '><div class="col-tag"><span class="no">' + no
                + '</span><span class="en">' + en + '</span><span class="cn">' + cn
                + '</span></div>' + inner + '</div>')
    light = ('<div class="a11y-grid">' + _a11y_cell('標準')
             + _a11y_cell('高对比', cls='hc') + '</div>'
             + '<div class="a11y-grid dark" style="margin-top:12px">'
             + _a11y_cell('深色 · 標準') + _a11y_cell('深色 · 高对比', cls='hc') + '</div>')
    dt = ('<div class="a11y-grid">' + _a11y_cell('標準 1.0')
          + _a11y_cell('大 1.176', style='--dt-scale:1.176')
          + _a11y_cell('特大 1.41', style='--dt-scale:1.41')
          + _a11y_cell('排版压力 1.75×', style='--dt-scale:1.75') + '</div>')
    return ('<div class="sec-tag"><h2>无障碍 · 高对比与字号</h2>'
            '<span class="en">Accessibility — Contrast / Dynamic Type</span></div>'
            '<div class="cols">'
            + col('A1', 'Increased Contrast', '高对比度', light)
            + col('A2', 'Dynamic Type', '字号阶梯', dt)
            + col('A3', 'Rules', '规则', A11Y_NOTES, flex=True)
            + '</div>')


def build_ext_page(t):
    L = t["letter"]
    dark_css = ";".join(f"--{k.replace('_','-')}:{v}" for k, v in DARK[L].items())
    root_add = (f"--elev:{t['vars']['surface']};--toast-bg:{t['vars']['ink']};"
                f"--toast-fg:#FFFFFF")
    _dsw = [("墨底", DARK[L]["bg"]), ("面", DARK[L]["surface"]), ("浮", DARK[L]["elev"]),
            ("字", DARK[L]["ink"]), ("主色+", DARK[L]["accent"]), ("线", DARK[L]["line_strong"])]
    sw = "".join(
        f'<div class="sw"><div class="dot" style="background:{c}"></div>'
        f'<div class="nm">{n}</div><div class="hx">{c}</div></div>'
        for n, c in _dsw
    )
    kw = "".join(f"<span>{k}</span>" for k in ["深色", "弹层", "空态", "引导", "图表"])
    header = EXT_HEADER_TPL.substitute(
        KANJI=t["kanji"], LETTER=L, JP=t["jp"], ROMAJI=t["romaji"],
        TAGLINE=t["tagline"], KW=kw, SW=sw,
    )
    body = f"""
{nav_row(L.lower() + '-ext')}
<div class="sec-tag"><h2>深色模式 · 墨</h2><span class="en">Dark Mode — Sumi</span></div>
<div class="cols">
  <div class="col">
    <div class="col-tag"><span class="no">D1</span><span class="en">Dark Components</span><span class="cn">暗色组件</span></div>
    {sub_icons(DARK_SCREEN)}
  </div>
  <div class="col">
    <div class="col-tag"><span class="no">D2</span><span class="en">Dark Screen</span><span class="cn">暗色整屏</span></div>
    {sub_icons(demo_dark())}
  </div>
  <div class="col" style="width:auto;flex:1">
    <div class="col-tag"><span class="no">D3</span><span class="en">Rules · Tokens</span><span class="cn">规则 · 色板</span></div>
    {dark_notes(L)}
  </div>
</div>

<div class="sec-tag"><h2>Sheet 弹层</h2><span class="en">Sheets · Half / Full</span></div>
<div class="cols">
  <div class="col">
    <div class="col-tag"><span class="no">S1</span><span class="en">Half Sheet</span><span class="cn">半屏 · 选择</span></div>
    {sub_icons(SHEET_HALF)}
  </div>
  <div class="col">
    <div class="col-tag"><span class="no">S2</span><span class="en">Full Sheet</span><span class="cn">全屏 · 表单</span></div>
    {sub_icons(SHEET_FULL)}
  </div>
  <div class="col" style="width:auto;flex:1">
    <div class="col-tag"><span class="no">S3</span><span class="en">Rules</span><span class="cn">规则</span></div>
    {sub_icons(SHEET_NOTES)}
  </div>
</div>

<div class="sec-tag"><h2>空状态</h2><span class="en">Empty States</span></div>
<div class="cols">
  <div class="col">
    <div class="col-tag"><span class="no">E1</span><span class="en">No Schedule</span><span class="cn">无预定</span></div>
    __EMPTY_WRAP__
  </div>
</div>
{sub_icons(EMPTY_NOTES)}

<div class="sec-tag"><h2>引导页</h2><span class="en">Onboarding · 3 Steps</span></div>
{sub_icons(onboarding_screens())}

<div class="sec-tag"><h2>图表</h2><span class="en">Charts</span></div>
<div class="cols">
  <div class="col">
    <div class="col-tag"><span class="no">C1</span><span class="en">Line · Stats</span><span class="cn">折线 · 指标卡</span></div>
    {sub_icons(CHART_S1)}
  </div>
  <div class="col">
    <div class="col-tag"><span class="no">C2</span><span class="en">Bar · Donut</span><span class="cn">柱状 · 环形</span></div>
    {sub_icons(CHART_S2)}
  </div>
  <div class="col" style="width:auto;flex:1">
    <div class="col-tag"><span class="no">C3</span><span class="en">Rules</span><span class="cn">规则</span></div>
    {sub_icons(CHART_NOTES)}
  </div>
</div>
"""
    # empty states: three screens, each in own col — rebuild that section properly
    empties = sub_icons(empty_screens())
    # split the three .screen blocks into three cols
    parts = empties.split('<div class="screen"')
    cols_html = ""
    tags = [("E1", "No Schedule", "无预定"), ("E2", "No Results", "搜索无结果"), ("E3", "Offline", "离线")]
    for (no, en, cn), part in zip(tags, parts[1:]):
        cols_html += (f'<div class="col"><div class="col-tag"><span class="no">{no}</span>'
                      f'<span class="en">{en}</span><span class="cn">{cn}</span></div>'
                      f'<div class="screen"{part}</div>')
    body = body.replace(f"""<div class="cols">
  <div class="col">
    <div class="col-tag"><span class="no">E1</span><span class="en">No Schedule</span><span class="cn">无预定</span></div>
    __EMPTY_WRAP__
  </div>
</div>""", f'<div class="cols">{cols_html}</div>')

    a11y_style = a11y_css_ext(L, t)
    body += a11y_section()
    root_css = ';'.join('--{}:{}'.format(k.replace('_', '-'), v)
                        for k, v in derive(t['vars'], True).items())

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{t['jp']} {t['romaji']} 拡張 — 深色/Sheet/空态/引导/图表</title>
<style>{CSS}</style>
<style>{EXT_CSS}</style>
<style>:root{{{root_css};{root_add}}}
.dark{{{dark_css}}}
{a11y_style}</style>
</head>
<body>
<div class="board">
{header}
{body}
<div class="foot">DIRECTION {L} · {t['jp']} — {t['romaji']} · EXTENSION · JP MINIMAL UI KIT 2026</div>
</div>
</body>
</html>
"""
    return page

# ------------------------------------------------------------ icons page ----
ICON_CSS = """
.spec-grid{display:flex;gap:26px;align-items:flex-start;margin-top:6px}
.spec-box{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:22px;flex:none}
.spec-box h5{font-size:calc(12px * var(--dt-scale,1));letter-spacing:.18em;color:var(--sub);margin-bottom:14px;font-weight:600}
.sizes-demo{display:flex;gap:20px;align-items:flex-end;background:var(--surface);
  border:1px solid var(--line);border-radius:16px;padding:22px}
.sizes-demo .s{text-align:center;color:var(--sub)}
.sizes-demo .s svg{margin:0 auto 8px}
.sizes-demo .s em{font-size:calc(9.5px * var(--dt-scale,1));color:var(--faint);font-style:normal;font-family:ui-monospace,Consolas,monospace}
.states-demo{display:flex;gap:14px;background:var(--surface);border:1px solid var(--line);
  border-radius:16px;padding:22px}
.states-demo .st{text-align:center;width:64px}
.states-demo .st .cir{width:48px;height:48px;border-radius:50%;margin:0 auto 8px;
  display:flex;align-items:center;justify-content:center;position:relative}
.states-demo .st .cir svg{width:22px;height:22px}
.states-demo .st em{font-size:calc(9.5px * var(--dt-scale,1));color:var(--faint);font-style:normal;display:block;margin-top:2px}
.states-demo .st b{font-size:calc(10.5px * var(--dt-scale,1));font-weight:500;color:var(--sub)}
.st-default .cir{color:var(--sub)}
.st-active .cir{color:var(--accent-text)}
.st-active b{color:var(--accent-text);font-weight:700}
.st-press .cir{background:var(--accent-soft);color:var(--accent-text)}
.st-disable .cir{color:var(--faint);opacity:.55}
.st-badge .cir{color:var(--sub)}
.st-badge .cir::after{content:"";position:absolute;top:10px;right:11px;width:8px;height:8px;
  border-radius:50%;background:var(--danger);border:2px solid var(--surface)}
.dd{display:flex;gap:20px;margin-top:6px}
.ddc{flex:1;background:var(--surface);border:1px solid var(--line);border-radius:16px;
  padding:20px;text-align:center}
.ddc .row{display:flex;gap:18px;justify-content:center;margin:14px 0 12px}
.ddc .row > span{width:44px;height:44px;border-radius:10px;background:var(--bg);
  display:flex;align-items:center;justify-content:center}
.ddc .row svg{width:24px;height:24px}
.ddc b{font-size:calc(12px * var(--dt-scale,1));letter-spacing:.1em}
.ddc span.lbl{font-size:calc(10.5px * var(--dt-scale,1));color:var(--sub);display:block;margin-top:5px;letter-spacing:.04em}
.ddc.do b{color:var(--tone2-text)}.ddc.dont b{color:var(--danger)}
.ddc.do{border-color:var(--tone2-text)}.ddc.dont{border-color:var(--danger)}
.igrid{display:grid;grid-template-columns:repeat(8,1fr);gap:10px;margin-top:6px}
.icell{background:var(--surface);border:1px solid var(--line);border-radius:12px;
  padding:16px 6px 12px;text-align:center;transition:border-color .15s,transform .15s}
.icell:hover{border-color:var(--accent-text);transform:translateY(-2px)}
.icell svg{width:24px;height:24px;color:var(--ink);margin:0 auto 10px}
.icell .jp{font-size:calc(10px * var(--dt-scale,1));color:var(--sub);letter-spacing:.05em;display:block}
.icell .cn{font-size:calc(9px * var(--dt-scale,1));color:var(--faint);display:block;margin-top:2px}
.notes.wide{max-width:none}
.icat{margin-bottom:30px}
.icat-h{display:flex;align-items:baseline;gap:12px;margin:0 2px 12px}
.icat-h .zh{font-size:calc(14px * var(--dt-scale,1));font-weight:700;letter-spacing:.16em;color:var(--ink)}
.icat-h .en2{font-size:calc(9.5px * var(--dt-scale,1));letter-spacing:.2em;color:var(--faint);text-transform:uppercase}
.icat-h::after{content:"";flex:1;height:1px;background:var(--line)}
/* 五方向 Token 对照 */
.dc-wrap{background:var(--surface);border:1px solid var(--line);border-radius:16px;
  padding:18px 22px 20px;overflow-x:auto}
.dc-row{display:flex;align-items:center;gap:14px;padding:11px 0;border-bottom:1px solid var(--line)}
.dc-row:last-child{border-bottom:none}
.dc-row.dc-head{padding-top:0;padding-bottom:9px;border-bottom:1px solid var(--line-strong)}
.dc-head .dc-ic{opacity:.5}
.dc-head .dc-ic svg{width:20px;height:20px;color:var(--faint)}
.dc-name{flex:none;width:104px;font-size:calc(11px * var(--dt-scale,1));color:var(--ink);
  letter-spacing:.04em;line-height:1.5}
.dc-name b{font-weight:700;color:var(--dc-accent);margin-right:5px}
.dc-name em{display:block;font-style:normal;font-size:calc(8.5px * var(--dt-scale,1));
  color:var(--faint);letter-spacing:.14em;text-transform:uppercase}
.dc-head .dc-name{font-size:calc(9.5px * var(--dt-scale,1));color:var(--faint);
  letter-spacing:.16em;text-transform:uppercase}
.dc-head .dc-name b,.dc-head .dc-name em{display:none}
.dc-ic{flex:none;width:34px;height:34px;display:flex;align-items:center;justify-content:center}
.dc-ic svg{width:22px;height:22px;color:var(--dc-accent)}
.dc-sw{flex:none;margin-left:auto;display:flex;align-items:center;gap:6px;
  font-size:calc(9px * var(--dt-scale,1));color:var(--faint);
  font-family:ui-monospace,Consolas,monospace}
.dc-sw i{width:10px;height:10px;border-radius:50%;display:inline-block;
  border:1px solid var(--line-strong)}
.dc-cap{margin-top:11px;font-size:calc(10px * var(--dt-scale,1));color:var(--sub);
  letter-spacing:.03em;text-align:center}
"""

# --- i18n：ICON_CSS 所辖选择器的拉丁降档 ---
# 刻意不动 .icat-h .zh（.16em）：那是「衣/食/住/行/娱/办」汉字分类名，属装饰性 CJK 元素，
# 宽字距对汉字是正确观感；是否随整页本地化属内容决策，不由 CSS 单方面改。
ICON_I18N_CSS = """
%(S)s .ddc b{letter-spacing:.02em}
%(S)s :is(.spec-box h5,.icat-h .en2){letter-spacing:.06em}
""".replace("%(S)s", LAT_LANG_SEL)

ICON_CSS = ICON_CSS + "\n" + ICON_I18N_CSS

GRID_SPEC_SVG = """
<svg width="256" height="256" viewBox="0 0 256 256" fill="none">
  <rect x="8" y="8" width="240" height="240" rx="6" style="fill:var(--bg);stroke:var(--line-strong)"/>
  <g style="stroke:var(--line)">
    <line x1="48" y1="8" x2="48" y2="248"/><line x1="88" y1="8" x2="88" y2="248"/>
    <line x1="128" y1="8" x2="128" y2="248"/><line x1="168" y1="8" x2="168" y2="248"/>
    <line x1="208" y1="8" x2="208" y2="248"/>
    <line x1="8" y1="48" x2="248" y2="48"/><line x1="8" y1="88" x2="248" y2="88"/>
    <line x1="8" y1="128" x2="248" y2="128"/><line x1="8" y1="168" x2="248" y2="168"/>
    <line x1="8" y1="208" x2="248" y2="208"/>
  </g>
  <rect x="28" y="28" width="200" height="200" rx="40" style="fill:var(--accent-ui)" opacity=".05"/>
  <rect x="28" y="28" width="200" height="200" rx="40" style="stroke:var(--accent-ui)" opacity=".45" stroke-dasharray="5 5"/>
  <circle cx="128" cy="128" r="2" style="stroke:var(--accent-ui)" opacity=".55"/>
  <line x1="118" y1="128" x2="138" y2="128" style="stroke:var(--accent-ui)" opacity=".4"/>
  <line x1="128" y1="118" x2="128" y2="138" style="stroke:var(--accent-ui)" opacity=".4"/>
  <!-- search glyph: 20x20 centered, stroke 1.6 scaled x10 => ~16 -->
  <g style="stroke:var(--ink)" stroke-width="16" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="120" cy="120" r="56"/>
    <line x1="160" y1="160" x2="196" y2="196"/>
  </g>
  <text x="28" y="24" font-size="10" style="fill:var(--accent-ui);font-family:ui-monospace,Consolas,monospace" letter-spacing="1">24 × 24 GRID</text>
  <text x="236" y="150" font-size="10" text-anchor="end" style="fill:var(--accent-ui);font-family:ui-monospace,Consolas,monospace">live 20×20</text>
  <text x="128" y="243" font-size="10" text-anchor="middle" style="fill:var(--sub);font-family:ui-monospace,Consolas,monospace">stroke 1.6 · cap round</text>
</svg>
"""

SIZE_DEMO = """
<div class="sizes-demo">
  <div class="s"><div style="width:24px;height:24px;color:var(--ink)">__HOME__</div><em>24 Tab</em></div>
  <div class="s"><div style="width:22px;height:22px;color:var(--ink)">__HOME__</div><em>22 导航</em></div>
  <div class="s"><div style="width:20px;height:20px;color:var(--ink)">__HOME__</div><em>20 列表</em></div>
  <div class="s"><div style="width:18px;height:18px;color:var(--ink)">__HOME__</div><em>18 行内</em></div>
  <div class="s"><div style="width:16px;height:16px;color:var(--ink)">__HOME__</div><em>16 微标</em></div>
</div>
"""

STATE_DEMO = """
<div class="states-demo">
  <div class="st st-default"><div class="cir">__BELL__</div><b>默认</b><em>sub</em></div>
  <div class="st st-active"><div class="cir">__BELL__</div><b>选中</b><em>accent</em></div>
  <div class="st st-press"><div class="cir">__BELL__</div><b>按压</b><em>soft底</em></div>
  <div class="st st-disable"><div class="cir">__BELL__</div><b>禁用</b><em>55%</em></div>
  <div class="st st-badge"><div class="cir">__BELL__</div><b>带角标</b><em>红点8</em></div>
</div>
"""

DD_HTML = """
<div class="dd">
  <div class="ddc do"><b>DO ✓</b>
    <div class="row">
      <span>__SEARCH__</span>
      <span>__HEART__</span>
      <span>__CAL__</span>
    </div>
    <span class="lbl">细线 1.6pt · 圆头圆角 · 留白充足</span>
  </div>
  <div class="ddc dont"><b>DON'T ✗</b>
    <div class="row">
      <span><svg viewBox="0 0 24 24" fill="none" style="stroke:var(--ink)" stroke-width="3"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2"/></svg></span>
      <span><svg viewBox="0 0 24 24" fill="var(--ink)" stroke="none"><path d="M20.8 5.6a5.2 5.2 0 0 0-7.4 0L12 7l-1.4-1.4a5.2 5.2 0 1 0-7.4 7.4l1.4 1.4L12 21.8l7.4-7.4 1.4-1.4a5.2 5.2 0 0 0 0-7.4z"/></svg></span>
      <span><svg viewBox="0 0 24 24" fill="none" style="stroke:var(--ink);stroke-width:1.2;stroke-linecap:square"><rect x="3.2" y="4.8" width="17.6" height="16.8"/><line x1="16.2" y1="2.4" x2="16.2" y2="7"/><line x1="7.8" y1="2.4" x2="7.8" y2="7"/><line x1="3.2" y1="10.2" x2="20.8" y2="10.2"/></svg></span>
    </div>
    <span class="lbl">通用图标避免随意混用线宽与尖角；原生 Tab 允许填充</span>
  </div>
</div>
"""

ICON_RULES_NOTES = """
<div class="notes wide">
  <div class="g2">
    <div>
      <h4 style="margin-top:0">网格与描边</h4>
      <ul>
        <li><b>24×24 网格</b>绘制，有效图形区 20×20（四周各留 2 安全边距）</li>
        <li>描边统一 <b>1.6pt</b>（放大预览 10× 即 16），全部圆头圆角（cap / join = round）</li>
        <li>光学对齐：圆形可略溢出网格（±1），方形贴网格线；线条落在整像素上防发虚</li>
        <li>优先复用 SF Symbols（linear 风格）；日式场景缺图标时按本规则自绘，导出 PDF 矢量入 Asset</li>
      </ul>
    </div>
    <div>
      <h4 style="margin-top:0">状态与配色</h4>
      <ul>
        <li>颜色只用 token：默认 sub / 选中 accent-text / 禁用 55% 透明 / 危险 danger，<b>不给图标单独配色</b></li>
        <li><b>图标是方向无关资产</b>：同一枚 SVG 在 A/B/C/D/E 五套下构造完全不变，仅随 `accent` 换色（见「五方向对照」）</li>
        <li>Tab 栏成对规则：24pt 图标 + 10pt 文字，选中变 accent 并加粗字重（原生 Tab 可使用系统填充变体）</li>
        <li>角标：红点 8pt 或数字胶囊，位于图标右上、压边 1/3，描 2pt 底色边</li>
        <li>按压态：加 accent-soft 圆形底（48pt），反馈即时、不加缩放动画以外的效果</li>
      </ul>
    </div>
  </div>
</div>
"""

# 五方向 Token 对照：同一批图标在五套配色下的表现，证明「构造不变、只换色」
ICON_DIR_COMPARE = """
<div class="dir-compare">
  {cells}
</div>
<div class="dir-cap">同一枚图标 · 五套 Token · 构造与描边完全一致，仅 accent / sub / danger 换色</div>
"""

def _dir_compare_html():
    """渲染五方向 × 代表性图标的对照网格。

    ⚠️ 不能只用 `for t in THEMES` —— D 不进 THEMES（它有独立 build_d.py），
    必须单独补入，否则对照区会静默少一行（已发生过）。顺序按字母 A/B/C/D/E。
    """
    demo = ['SEARCH', 'BELL', 'HEART', 'USER', 'LOCK', 'CAL', 'CART', 'GEAR']
    demo = [k for k in demo if k in ALL_ICONS]

    # 收集五方向：THEMES 提供 A/B/C/E，D 从 build_d 取浅色基础板
    entries = []
    for t in THEMES:
        entries.append((t["letter"], t["jp"], t["romaji"], derive(t["vars"], True)))
    try:
        import build_d
        dv = derive(dict(build_d.L_BASE), True)
        entries.append(("D", "紫硝子", "MURASAKI", dv))
    except Exception as e:                                    # noqa: BLE001
        log.warning("direction D missing from icon compare: %s", e)
    entries.sort(key=lambda x: x[0])

    head = '<div class="dc-row dc-head"><div class="dc-name">方向</div>' + \
           ''.join(f'<div class="dc-ic">{ALL_ICONS[k]}</div>' for k in demo) + \
           '<div class="dc-sw">选中 / 默认 / 禁用 / 角标</div></div>'
    rows = []
    for letter, jp, romaji, v in entries:
        cnt = ""
        rows.append(
            f'<div class="dc-row" data-dir="{letter}" style="--dc-accent:{v["accent_text"]};--dc-sub:{v["sub"]};'
            f'--dc-faint:{v["faint"]};--dc-danger:{v["danger"]}">'
            f'<div class="dc-name"><b>{letter}</b> {jp}'
            f'<em>{romaji}{cnt}</em></div>'
            + ''.join(f'<div class="dc-ic">{ALL_ICONS[k]}</div>' for k in demo)
            + f'<div class="dc-sw"><i style="background:{v["accent_text"]}"></i>{v["accent_text"]}'
              f'<i style="background:{v["sub"]}"></i>{v["sub"]}'
              f'<i style="background:{v["faint"]};opacity:.55"></i>55%'
              f'<i style="background:{v["danger"]}"></i>{v["danger"]}</div></div>')
    return '<div class="dc-wrap">' + head + ''.join(rows) + '</div>'


def build_icons_page():
    total = sum(len(items) for _, _, items in CATS)
    lib_html = ""
    for gname, gen, items in CATS:
        cells = ""
        for key, jp, cn in items:
            cells += (f'<div class="icell">{ALL_ICONS[key]}'
                      f'<span class="jp">{jp}</span><span class="cn">{cn}</span></div>')
        lib_html += (f'<div class="icat"><div class="icat-h"><span class="zh">{gname}</span>'
                     f'<span class="en2">{gen} · {len(items)}</span></div>'
                     f'<div class="igrid">{cells}</div></div>')
    dir_compare = _dir_compare_html()
    body = f"""
{nav_row('icons')}
<div class="sec-tag"><h2>图标绘制规则</h2><span class="en">Icon Construction · 24pt Grid</span></div>
<div class="spec-grid">
  <div class="spec-box"><h5>构造 · 検索 示例</h5>{GRID_SPEC_SVG}</div>
  <div style="flex:1;display:flex;flex-direction:column;gap:20px">
    <div><div class="sec-h" style="margin-bottom:10px"><span class="jp">サイズ</span><span class="en">Sizes</span></div>{sub_icons(SIZE_DEMO)}</div>
    <div><div class="sec-h" style="margin-bottom:10px"><span class="jp">ステート</span><span class="en">States</span></div>{sub_icons(STATE_DEMO)}</div>
    <div><div class="sec-h" style="margin-bottom:10px"><span class="jp">良し悪し</span><span class="en">Do / Don't</span></div>{sub_icons(DD_HTML)}</div>
  </div>
</div>
{ICON_RULES_NOTES}
<div class="sec-tag"><h2>五方向 Token 对照</h2><span class="en">Direction Token Compare · A / B / C / D / E</span></div>
{dir_compare}
<div class="sec-tag"><h2>图标库 · {total} 枚 · 衣食住行全覆盖</h2><span class="en">Icon Library · 7 Categories</span></div>
{lib_html}
"""
    header = """
<div class="bh">
  <div class="bh-left">
    <div class="appicon"><span class="kanji">図</span></div>
    <div class="bh-title">
      <div class="kicker">JP MINIMAL UI KIT — ICON DESIGN RULES — 24PT GRID · STROKE 1.6</div>
      <h1>图标规则<span class="romaji">ICON RULES</span></h1>
      <div class="cn">五方向通用 · 细线几何 · 安静克制</div>
      <p class="desc">全部图标共用一套构造规则：24×24 网格、约20×20核心区、1.6pt圆头描边；原生 Tab 允许填充。颜色只从 Design Token 取（默认 sub / 选中 accent-text / 禁用 55%），保证各主题下观感一致。</p>
      <div class="kw"><span>細線</span><span>幾何</span><span>静寂</span></div>
    </div>
  </div>
  <div class="tate">線は細く・角は丸く</div>
  <div class="swatches">
    <div class="sw"><div class="dot" style="background:#6E695E"></div><div class="nm">默认</div><div class="hx">sub</div></div>
    <div class="sw"><div class="dot" style="background:#8A6248"></div><div class="nm">选中</div><div class="hx">accent</div></div>
    <div class="sw"><div class="dot" style="background:#D8D0C0"></div><div class="nm">禁用</div><div class="hx">55%</div></div>
    <div class="sw"><div class="dot" style="background:#B4493A"></div><div class="nm">角标</div><div class="hx">danger</div></div>
  </div>
</div>
<div class="tokens">
  <span class="tk"><b>网格</b>24 × 24（有效 20 × 20）</span>
  <span class="tk"><b>描边</b>1.6 pt · round cap/join</span>
  <span class="tk"><b>填充</b>通用线性；原生 Tab 例外</span>
  <span class="tk"><b>尺寸档</b>24/22/20/18/16</span>
  <span class="tk"><b>角标</b>红点 8pt / 数字胶囊</span>
  <span class="tk"><b>来源</b>SF Symbols linear 优先</span>
</div>
"""
    t0 = THEMES[0]
    t0v = derive(t0["vars"], True)      # 统一架构：过一遍求解器（勿直接用 vars）
    vars_css = ";".join(f"--{k.replace('_','-')}:{v}" for k, v in t0v.items())
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>图标规则 ICON RULES — 日式简约 iOS UI</title>
<style>{CSS}</style>
<style>{EXT_CSS}</style>
<style>{ICON_CSS}</style>
<style>:root{{{vars_css};--elev:{t0['vars']['surface']};--toast-bg:{t0['vars']['ink']};--toast-fg:#FFFFFF}}</style>
<style>{a11y_css(t0['letter'])}</style>
</head>
<body>
<div class="board">
{header}
{body}
<div class="foot">ICON RULES · 24PT GRID · JP MINIMAL UI KIT 2026</div>
</div>
</body>
</html>
"""
    return page

# The current index is generated from theme metadata (no historical status copy).
def build_index_v2():
    return index_page(sum(len(items) for _, _, items in CATS))

# ------------------------------------------------------------------ main ----
def main():
    from catalog_pages import components_page, reuse_page
    from adaptive_demo import page as adaptive_page
    for t in THEMES:
        stem = t["file"].replace(".html", "")
        out_name = stem + "-ext.html"
        page = prepare_page(build_ext_page(t), out_name, t)
        path = os.path.join(OUT, out_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        log.info("written %s (%.1f KB)", out_name, os.path.getsize(path) / 1024)

    icons = prepare_page(build_icons_page(), "icons.html")
    p = os.path.join(OUT, "icons.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(icons)
    log.info("written icons.html (%.1f KB)", os.path.getsize(p) / 1024)

    idx = build_index_v2()
    p = os.path.join(OUT, "index.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(idx)
    log.info("rewritten index.html (%.1f KB)", os.path.getsize(p) / 1024)
    with open(os.path.join(OUT, "standards.html"), "w", encoding="utf-8") as f:
        f.write(standards_page())
    for name, generator in (("components.html", components_page), ("reuse.html", reuse_page), ("adaptive.html", adaptive_page)):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(generator())
    log.info("BUILD OK -> %s", OUT)

if __name__ == "__main__":
    main()
