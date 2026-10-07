"""Static acceptance: palette pairs, emitted CSS, links and registered coverage.

This does not launch a browser or claim device/native accessibility validation.
"""
import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[];self.ids=set();self.icons=0;self.devices=[];self.styles=[];self.in_style=False
        self.viewport=False;self.nav=False;self.svg_issues=[];self.in_icon=False;self.level=0
        self.hour_modes=[];self.hour_options=[];self.hour_wheels=[]
        self.time_modes=[];self.time_options=[];self.minute_options=[];self.time_wheels=[]
        self.widget_modes=[];self.widget_families=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-widget-mode' in a:self.widget_modes.append(a['data-widget-mode'])
        if 'data-widget-family' in a:self.widget_families.append(a['data-widget-family'])
        if 'data-hour-mode' in a:self.hour_modes.append(a['data-hour-mode'])
        if 'data-hour' in a:self.hour_options.append(a)
        if 'data-time-mode' in a:self.time_modes.append(a['data-time-mode'])
        if 'data-time-hour' in a:self.time_options.append(a)
        if 'data-minute' in a:self.minute_options.append(a)
        classes=a.get('class','').split()
        if 'hp-time-wheel' in classes:self.time_wheels.append(a)
        elif 'hp-wheel' in classes:self.hour_wheels.append(a)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='meta' and a.get('name')=='viewport':self.viewport=True
        if tag=='nav' and a.get('aria-label')=='规范导航':self.nav=True
        if tag=='style':self.in_style=True
        if 'icell' in a.get('class','').split():self.icons+=1;self.in_icon=True;self.level=0
        if self.in_icon and tag=='div':self.level+=1
        if self.in_icon and tag=='svg':
            if a.get('viewbox')!='0 0 24 24' or a.get('stroke')!='currentColor' or a.get('stroke-width') not in ('1.6','1.8','2.2') or 'width' in a or 'height' in a:
                self.svg_issues.append(a)
        if 'dev' in a.get('class','').split() and 'data-dir' in a:self.devices.append(a['data-dir'])
    def handle_endtag(self,tag):
        if tag=='style':self.in_style=False
        if tag=='div' and self.in_icon:
            self.level-=1
            if self.level==0:self.in_icon=False
    def handle_data(self,data):
        if self.in_style:self.styles.append(data)


def variables(block):
    return {k.replace('-','_'):v.strip() for k,v in re.findall(r'--([\w-]+):\s*([^;}]+)',block)}


def validate(project,write=True):
    project=Path(project).resolve();sys.path.insert(0,str(project))
    from design_tokens import ratio
    from hour_picker import CONTRACT, TIME_CONTRACT
    from shape_tokens import SHAPES, CONTRACT as BUTTON_CONTRACT
    from widget_spec import CONTRACT as WIDGET_CONTRACT
    from component_catalog import CONTRACT as COMPONENT_CONTRACT
    data=json.loads((project/'design-tokens.json').read_text(encoding='utf-8'))
    failures=[];checks=0;minimums={}
    def check(condition,reason):
        nonlocal checks
        checks+=1
        if not condition:failures.append(reason)
    def pair(p,a,b,target,context):
        score=ratio(p[a],p[b]);check(score>=target,f'{context}: {a}/{b} = {score:.3f} < {target}')
        return score
    sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted([*project.glob('*.py'),project/'themes.json'])}
    check(sources==data.get('source_fingerprints'),'Source/configuration changed: rebuild required')
    check(data.get('components',{}).get('hour_picker')==CONTRACT,'Hour picker export differs from source contract')
    check(data.get('components',{}).get('time_picker')==TIME_CONTRACT,'Time picker export differs from source contract')
    check(data.get('components',{}).get('hour_picker',{}).get('wraps') is True,'Hour picker must wrap at 00/23')
    check(data.get('components',{}).get('time_picker',{}).get('wraps') is True,'Time picker must wrap at 00/59')
    check(data.get('components',{}).get('button_shape')==BUTTON_CONTRACT,'Button shape export differs from source contract')
    check(data.get('components',{}).get('widgetkit')==WIDGET_CONTRACT,'WidgetKit export differs from source contract')
    check(data.get('components',{}).get('html_demo')==COMPONENT_CONTRACT,'HTML demo catalog differs from source contract')
    for key,t in data['themes'].items():
        minimums[key]={}
        for mode in ('light','dark','light_hc','dark_hc'):
            p=t[mode];hc=mode.endswith('_hc');target=7 if hc else 4.5;context=f'{key}/{mode}'
            scores=[]
            for token,value in SHAPES.items():check(p.get(token)==value,f'{context}: inconsistent control shape {token}')
            for bg in ('bg','surface','fill'):
                for fg in ('ink','sub','faint','accent_text','danger_text'):
                    scores.append(pair(p,fg,bg,7 if fg in ('ink','sub') else target,context))
                for fg in ('accent_ui','control_border'):pair(p,fg,bg,3,context)
            for fg,bg in [('on_accent','accent'),('on_danger','danger'),('on_stamp','stamp'),('accent_deep','accent_soft'),('tone2_text','soft2'),('tone3_text','soft3')]:
                scores.append(pair(p,fg,bg,target,context))
            for state in ('success','warning','info'):pair(p,state+'_text',state+'_soft',target,context)
            for fg in ('data2','data3','chart_muted'):pair(p,fg,'surface',3,context)
            minimums[key][mode]=round(min(scores),3)
    pages={}
    expected={'index.html','icons.html','devices.html','standards.html','components.html','adaptive.html','reuse.html'}
    for t in data['themes'].values():expected.update((t['file'],t['file'].replace('.html','-ext.html')))
    for name in sorted(expected):
        path=project/name;check(path.exists(),f'Missing {name}')
        if not path.exists():continue
        src=path.read_text(encoding='utf-8');doc=Document();doc.feed(src);pages[name]=(src,doc)
        check(doc.viewport,f'{name}: missing viewport');check(doc.nav,f'{name}: missing navigation')
        check('人眼对青绿波段聚焦最省力' not in src,f'{name}: unsupported health claim')
        check('✔ 已确认' not in src and '✔ 四套通过' not in src,f'{name}: stale signoff')
        check(not re.search(r'\$[A-Z][A-Z_]+|__[A-Z][A-Z_]+__',src),f'{name}: unresolved template')
        declarations=set(re.findall(r'(--[\w-]+)\s*:',src))
        required=set(re.findall(r'var\((--[\w-]+)\)',src))
        check(not required-declarations,f'{name}: undefined CSS variables {sorted(required-declarations)}')
    links=0
    for name,(src,doc) in pages.items():
        for href in doc.links:
            if re.match(r'^[a-z]+:',href):continue
            links+=1;file,_,anchor=href.partition('#');target=project/(file or name)
            check(target.exists(),f'{name}: broken link {href}')
            if anchor and target.name in pages:check(anchor in pages[target.name][1].ids,f'{name}: missing anchor {href}')
    check(pages['icons.html'][1].icons==169,'Icon library count changed')
    check(not pages['icons.html'][1].svg_issues,'Icon SVG contract violated')
    check((project/'LICENSE').exists(),'Missing MIT license')
    check((project/'dist/jp-min-ui-kit-5.1.zip').exists(),'Missing downloadable release ZIP')
    check('data-cc-demo' in pages[next(iter(data['themes'].values()))['file']][0],'Missing interactive component demonstration')
    adaptive=pages['adaptive.html'][0]
    for control in ('scenario','width','height','safe-left','safe-right','control-align','hinge'):
        check(f'<label for="{control}">' in adaptive,f'adaptive.html: missing explicit label for {control}')
    check('fold-unavailable' in adaptive and 'fold-single' in adaptive,'adaptive.html: fold fallback states missing')
    for key,t in data['themes'].items():
        check(pages['devices.html'][1].devices.count(key)==4,f'{key}: device coverage')
        check(f'data-dir="{key}"' in pages['icons.html'][0],f'{key}: missing icon comparison')
        check(t['file'] in pages['index.html'][1].links,f'{key}: missing index card')
        for name in (t['file'],t['file'].replace('.html','-ext.html')):
            src=pages[name][0]
            doc=pages[name][1]
            expected_demo='class="notes cc-section dark"' if name.endswith('-ext.html') else 'class="notes cc-section"'
            check(expected_demo in src,f'{name}: interactive demo color mode missing')
            if not name.endswith('-ext.html'):
                check(not any(stale in src for stale in ('全屏仅一个强调色','下一步产出','三个方向选一','是否补充：深色模式')),f'{name}: stale design notes')
                check(name.replace('.html','-ext.html') in src,f'{name}: missing extension link in notes')
            if t['file']=='theme-sunny-day.html' and not name.endswith('-ext.html'):
                check('辅助色 #F26B5B 与第三色 #F4C84A' in src,f'{name}: missing multicolor role explanation')
            modes=['dark','dark_hc'] if name.endswith('-ext.html') else ['light','light_hc']
            check(doc.widget_modes==modes,f'{name}: WidgetKit mode coverage')
            check(doc.widget_families==WIDGET_CONTRACT['preview_families']*2,f'{name}: WidgetKit family preview coverage')
            check('widgetkit' in doc.ids,f'{name}: missing WidgetKit anchor')
            check(doc.hour_modes==modes,f'{name}: hour picker mode coverage')
            check('hour-picker' in doc.ids,f'{name}: hour picker anchor missing')
            check(len(doc.hour_wheels)==2,f'{name}: missing hour wheels')
            check([o['data-hour'] for o in doc.hour_options]==[str(n) for n in range(24)]*2,f'{name}: hour range/order differs from contract')
            selected=[o['id'] for o in doc.hour_options if o.get('aria-selected')=='true']
            check(selected==['hp-'+m+'-9' for m in modes],f'{name}: initial hour selection incorrect')
            check([w.get('aria-activedescendant') for w in doc.hour_wheels]==selected,f'{name}: accessible hour selection mismatch')
            check(all(w.get('role')=='listbox' and w.get('tabindex')=='0' and w.get('aria-labelledby') in doc.ids for w in doc.hour_wheels),f'{name}: inaccessible hour wheel label/focus')
            check(doc.time_modes==modes,f'{name}: time picker mode coverage')
            check('time-picker' in doc.ids,f'{name}: time picker anchor missing')
            check([o['data-time-hour'] for o in doc.time_options]==[str(n) for n in range(24)]*2,f'{name}: time hour range/order incorrect')
            check([o['data-minute'] for o in doc.minute_options]==[str(n) for n in range(60)]*2,f'{name}: minute range/order incorrect')
            check(all(o.get('data-value')==o.get('data-minute',o.get('data-time-hour')) for o in [*doc.time_options,*doc.minute_options]),f'{name}: time candidate value mismatch')
            check([o['id'] for o in doc.time_options if o.get('aria-selected')=='true']==['tp-'+m+'-time-hour-9' for m in modes],f'{name}: initial time hour incorrect')
            check([o['id'] for o in doc.minute_options if o.get('aria-selected')=='true']==['tp-'+m+'-minute-30' for m in modes],f'{name}: initial minute incorrect')
            check([w.get('aria-activedescendant') for w in doc.time_wheels]==[v for m in modes for v in ('tp-'+m+'-time-hour-9','tp-'+m+'-minute-30')],f'{name}: accessible time selection mismatch')
            check(all(w.get('role')=='listbox' and w.get('tabindex')=='0' and len(w.get('aria-labelledby','').split())==2 and all(label in doc.ids for label in w['aria-labelledby'].split()) for w in doc.time_wheels),f'{name}: time column labels/focus incorrect')
            css='\n'.join(pages[name][1].styles)
            roots=re.findall(r':root\{([^}]+)\}',css)
            actual=next((variables(b) for b in roots if '--page-bg:' in b),{})
            for token in ('accent','accent_text','accent_ui','on_accent','tone2_text','control_border','r_btn','r_segment','r_segment_item'):
                check(actual.get(token)==t['light'][token],f'{name}: stale light {token}')
            if name.endswith('-ext.html') or key=='D':
                matches=re.findall(r'\.dark\.hc\{([^}]+)\}',css)
                actual=variables(matches[-1]) if matches else {}
                for token in ('sub','faint','accent_text','on_accent','danger','on_danger'):
                    check(actual.get(token)==t['dark_hc'][token],f'{name}: incorrect dark HC {token}')
            check('prefers-contrast: more' in css,f'{name}: missing system HC rule')
            check('prefers-reduced-motion' in css,f'{name}: missing reduced motion')
    skill=project/'skill/SKILL.md'
    if skill.exists():
        text=skill.read_text(encoding='utf-8')
        check(text.startswith('---\nname: jp-min-ui-build\n'), 'Skill identity/frontmatter changed')
        check(bool(re.search(r'^description: .+',text,re.M)), 'Skill description missing')
        for href in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in href:check((skill.parent/href).exists(),f'Skill reference missing: {href}')
        for entry in ('create_theme.py','rebuild.py','validate.py','test_system.py'):
            check((skill.parent/'scripts'/entry).exists(),f'Skill entry missing: {entry}')
    result=dict(status='PASS' if not failures else 'FAIL',checks=checks,html_pages=len(pages),links=links,
        themes=len(data['themes']),icons=169,minimum_text_contrast=minimums,failures=failures,
        browser_visual='NOT_RUN: browser layout and interaction require separate review',
        native_ios='NOT_RUN: no iOS application or simulator in this project',
        files={name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in sorted(expected)})
    if write:
        (project/'acceptance-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args();result=validate(args.project)
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','minimum_text_contrast')},ensure_ascii=False,indent=2))
    sys.exit(0 if result['status']=='PASS' else 1)
