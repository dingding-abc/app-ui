"""Rebuild all samples and semantic tokens using the invoking Python runtime."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def build(project):
    project = Path(project).resolve()
    for name in ('build.py','build_d.py','build_d_ext.py','build_devices.py','build_ext.py'):
        subprocess.run([sys.executable, str(project / name)], cwd=project, check=True)
    # Imports happen only after all producers succeed; no stale partial export.
    sys.path.insert(0, str(project))
    from site_support import all_themes
    from build import derive
    from build_ext import DARK
    from build_d import D
    from design_tokens import finish_palette
    from hour_picker import CONTRACT, TIME_CONTRACT, PRESENTATION_CONTRACT
    from shape_tokens import CONTRACT as BUTTON_CONTRACT, NAVIGATION_CONTRACT
    from widget_spec import CONTRACT as WIDGET_CONTRACT
    from component_catalog import CONTRACT as COMPONENT_CONTRACT, FORM_CONTRACT
    from ui_contract import TYPE_SIZES, TYPE_ROLES, SPACING, LAYOUT, FEEDBACK, feedback_markdown
    themes = {}
    for t in all_themes():
        light = derive(t['vars'], True)
        dark = finish_palette(D if t['letter'] == 'D' else DARK[t['letter']], False)
        themes[t['letter']] = dict(name=t['jp'], file=t['file'], material=t.get('material','paper'),
            light=light, dark=dark, light_hc=finish_palette(light,True,True), dark_hc=finish_palette(dark,False,True))
    result = dict(version='5.1', native_contract_version=1, themes=themes,
        typography=TYPE_SIZES, typography_roles=TYPE_ROLES, layout=LAYOUT,
        spacing=SPACING, components=dict(hour_picker=CONTRACT,time_picker=TIME_CONTRACT,button_shape=BUTTON_CONTRACT,navigation_selection=NAVIGATION_CONTRACT,widgetkit=WIDGET_CONTRACT,html_demo=COMPONENT_CONTRACT,picker_presentation=PRESENTATION_CONTRACT,form_interaction=FORM_CONTRACT,transient_feedback=FEEDBACK), native_validation='pending',
        source_fingerprints={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted([*project.glob('*.py'),project/'themes.json'])})
    (project/'design-tokens.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    guidance = project/'docs/interaction-standard.md'
    text = guidance.read_text(encoding='utf-8')
    start, end = '<!-- feedback-contract:start -->', '<!-- feedback-contract:end -->'
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        guidance.write_text(before + start + '\n' + feedback_markdown() + '\n' + end + after, encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    build(args.project)
