"""Validated, data-only custom themes. No generated Python or executable config."""
import json
import re
from pathlib import Path
from design_tokens import hsl_color, finish_palette, luminance
import colorsys

REGISTRY = Path(__file__).with_name('themes.json')


def check_spec(spec):
    required = {'id', 'name', 'accent'}
    if not required <= spec.keys():
        raise ValueError('Theme requires id, name and accent')
    if set(spec) - {'id', 'name', 'accent', 'dark_accent', 'auxiliary', 'tertiary', 'description', 'material'}:
        raise ValueError('Unknown theme fields')
    if not re.fullmatch(r'[a-z][a-z0-9-]{1,31}', spec['id']):
        raise ValueError('id must be a lowercase slug (2–32 characters)')
    for key in ('name', 'description'):
        value = spec.get(key, '')
        if not isinstance(value, str) or any(c in value for c in '<>\n\r') or len(value) > 200:
            raise ValueError(f'Invalid {key}')
    if not spec['name'].strip():
        raise ValueError('Theme name cannot be empty')
    for key in ('accent', 'dark_accent', 'auxiliary', 'tertiary'):
        if key in spec:
            luminance(spec[key])
    if spec.get('material', 'paper') not in ('paper', 'glass'):
        raise ValueError('material must be paper or glass')
    return spec


def palette(accent, light, auxiliary=None, tertiary=None):
    h, l, s = colorsys.rgb_to_hls(*[int(accent[i:i+2], 16)/255 for i in (1,3,5)])
    def c(value, saturation=.18, offset=0):
        return hsl_color(h + offset, saturation, value)
    p = dict(page_bg=c(.91 if light else .07), bg=c(.96 if light else .10),
             surface=c(.99 if light else .14), fill=c(.93 if light else .18),
             fill_strong=c(.85 if light else .23), ink=c(.14 if light else .93),
             sub_seed=c(.34 if light else .73), faint_seed=c(.47 if light else .59),
             line=c(.89 if light else .20), line_strong=c(.81 if light else .29),
             accent=accent.upper(), accent_deep=c(max(0,l-.12) if light else min(1,l+.12),s),
             accent_soft=c(.95 if light else .20), danger='#B4493A' if light else '#E18D80',
             danger_soft='#F8ECEA' if light else '#392423', stamp='#B54336' if light else '#E68E80',
             tone2=c(.48 if light else .72,.24,.16), soft2=c(.95 if light else .20,.18,.16),
             tone3=c(.47 if light else .72,.22,-.18), soft3=c(.95 if light else .20,.18,-.18),
             sun='#B4493A' if light else '#E18D80', sat='#476C91' if light else '#A5BDD8',
             r_card='14px', r_in='9px', elev=c(.99 if light else .25),
             toast_bg=c(.16 if light else .25), toast_fg=c(.97))
    for seed, number in ((auxiliary, 2), (tertiary, 3)):
        if seed:
            ah, al, ass = colorsys.rgb_to_hls(*[int(seed[i:i+2], 16)/255 for i in (1,3,5)])
            p[f'tone{number}'] = seed.upper() if light else hsl_color(ah, min(ass,.72), max(.70,al))
            p[f'soft{number}'] = hsl_color(ah, .24, .95 if light else .20)
    return finish_palette(p, light)


def theme_from_spec(spec):
    check_spec(spec)
    h, l, s = colorsys.rgb_to_hls(*[int(spec['accent'][i:i+2],16)/255 for i in (1,3,5)])
    dark_color = spec.get('dark_accent', hsl_color(h, min(s,.55), max(.67,l)))
    light = palette(spec['accent'], True, spec.get('auxiliary'), spec.get('tertiary'))
    dark = palette(dark_color, False, spec.get('auxiliary'), spec.get('tertiary'))
    slug, name = spec['id'], spec['name']
    return dict(letter=slug.upper(), file=f'theme-{slug}.html', jp=name,
                romaji=slug.upper(), kanji=name[0], tagline='自定义色系 · 共用组件规范',
                cn_short='自定义主题', desc=spec.get('description','按指定主色生成；文字与控件颜色按用途独立求解。'),
                keywords=['统一', '清晰', '克制'], radii='卡片 14 / 按钮 胶囊 / 输入 9',
                swatches=[('底',light['bg']),('面',light['surface']),('字',light['ink']),
                          ('主色',light['accent']),('危险',light['danger']),('辅色',light['tone2'])],
                vars=light, dark_vars=dark, material=spec.get('material','paper'),
                palette_roles={key:spec[key].upper() for key in ('accent','auxiliary','tertiary') if key in spec})


def load_custom():
    if not REGISTRY.exists():
        return []
    specs = json.loads(REGISTRY.read_text(encoding='utf-8'))
    if not isinstance(specs, list):
        raise ValueError('themes.json must contain a list')
    themes = [theme_from_spec(s) for s in specs]
    if len({t['file'] for t in themes}) != len(themes):
        raise ValueError('Duplicate theme id')
    return themes
