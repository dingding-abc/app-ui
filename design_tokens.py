"""Semantic colors shared by HTML, exports and theme generation (stdlib only)."""
import colorsys
import re
from shape_tokens import SHAPES

TEXT_MIN = 4.6
TEXT_HC = 7.0
UI_MIN = 3.1


def luminance(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError(f"Expected #RRGGBB, got {value!r}")
    channels = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(a * b for a, b in zip(linear, (.2126, .7152, .0722)))


def ratio(a, b):
    x, y = sorted((luminance(a), luminance(b)))
    return (y + .05) / (x + .05)


def hsl_color(hue, saturation, lightness):
    return '#' + ''.join(f'{round(c * 255):02X}' for c in colorsys.hls_to_rgb(hue % 1, lightness, saturation))


def readable(seed, backgrounds, minimum, light):
    """Adjust only lightness; fail explicitly if a mixed backdrop is unsolvable."""
    rgb = [int(seed[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    hue, value, saturation = colorsys.rgb_to_hls(*rgb)
    for step in range(1001):
        v = max(0, value - step / 1000) if light else min(1, value + step / 1000)
        color = hsl_color(hue, saturation, v)
        if all(ratio(color, bg) >= minimum for bg in backgrounds):
            return color
    raise ValueError(f'Cannot reach {minimum}:1 for {seed} on {backgrounds}')


def finish_palette(base, light, high_contrast=False):
    p = {k: v for k, v in base.items() if not k.startswith('hc_')}
    for key in ('sub', 'faint'):
        seed = p.pop(key + '_seed', p.get(key, p['ink']))
        p[key] = seed
    backgrounds = [p['bg'], p['surface'], p.get('fill', p['bg'])]
    target = TEXT_HC if high_contrast else TEXT_MIN
    p['ink'] = readable(p['ink'], backgrounds, TEXT_HC, light)
    p['sub'] = readable(p['sub'], backgrounds, TEXT_HC, light)
    p['faint'] = readable(p['faint'], backgrounds, target, light)
    # Brand fills retain their identity; readable foregrounds have separate roles.
    for key in ('accent', 'danger', 'stamp'):
        p['on_' + key] = max(('#FFFFFF', '#111111'), key=lambda c: ratio(c, p[key]))
        if high_contrast and ratio(p['on_' + key], p[key]) < TEXT_HC:
            p[key] = readable(p[key], [p['on_' + key]], TEXT_HC, p['on_' + key] == '#FFFFFF')
    for key in ('accent', 'danger'):
        # Text-only destructive actions are also rendered on danger_soft.
        text_backgrounds = backgrounds + ([p['danger_soft']] if key == 'danger' else [])
        p[key + '_text'] = readable(p[key], text_backgrounds, target, light)
    p['accent_ui'] = readable(p['accent'], backgrounds, 4.5 if high_contrast else UI_MIN, light)
    p['accent_deep'] = readable(p['accent_deep'], [p['accent_soft']], target, light)
    p['control_border'] = readable(p['line_strong'], backgrounds, 4.5 if high_contrast else UI_MIN, light)
    p['chart_muted'] = readable(p['fill_strong'], [p['surface']], UI_MIN, light)
    for n in (2, 3):
        p[f'tone{n}_text'] = readable(p[f'tone{n}'], [p[f'soft{n}']], target, light)
        p[f'data{n}'] = readable(p[f'tone{n}'], [p['surface'], p['bg']], UI_MIN, light)
    for key in ('sun', 'sat'):
        p[key] = readable(p[key], backgrounds, target, light)
    for key, seed in [('success', '#417358'), ('warning', '#8C641C'), ('info', '#386C96')]:
        p[key + '_soft'] = hsl_color(colorsys.rgb_to_hls(*[int(seed[i:i+2], 16)/255 for i in (1,3,5)])[0], .2, .95 if light else .18)
        p[key + '_text'] = readable(seed, [p[key + '_soft'], *backgrounds], target, light)
    if high_contrast:
        p['line'] = p['line_strong']
        p['line_strong'] = p['control_border']
    p.update(SHAPES)
    return p


def css_vars(palette):
    return ';'.join(f'--{k.replace("_", "-")}:{v}' for k, v in palette.items() if not k.startswith('hc_'))


def hc_css(palette, light):
    return css_vars(finish_palette(palette, light, True))
