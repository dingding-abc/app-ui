"""Behavioral regressions and a new-theme end-to-end build in a temporary copy."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from design_tokens import finish_palette,ratio
from theme_registry import check_spec,theme_from_spec
from build import THEMES
from build_ext import DARK
from hour_picker import card, time_card
from validate import Document


class HourPickerContract(unittest.TestCase):
    def test_initial_value_at_both_boundaries(self):
        for hour in (0,23):
            doc=Document();doc.feed(card('boundary','light',hour))
            selected=[o for o in doc.hour_options if o['aria-selected']=='true']
            self.assertEqual([o['data-hour'] for o in selected],[str(hour)])
            self.assertEqual(doc.hour_wheels[0]['aria-activedescendant'],selected[0]['id'])
            self.assertEqual([int(o['data-hour']) for o in doc.hour_options],list(range(24)))

    def test_invalid_initial_hour_rejected(self):
        for hour in (-1,24,9.5,'9',True,None):
            with self.assertRaises(ValueError):card('invalid','light',hour)


class TimePickerContract(unittest.TestCase):
    def test_midnight_and_last_minute(self):
        for hour,minute in ((0,0),(23,59)):
            doc=Document();doc.feed(time_card('boundary','light',hour,minute))
            self.assertEqual([o['data-time-hour'] for o in doc.time_options if o['aria-selected']=='true'],[str(hour)])
            self.assertEqual([o['data-minute'] for o in doc.minute_options if o['aria-selected']=='true'],[str(minute)])
            self.assertEqual([o['data-minute'] for o in doc.minute_options],[str(n) for n in range(60)])

    def test_minute_steps_generate_values_not_row_indices(self):
        for step in (1,5,10,15,30):
            doc=Document();doc.feed(time_card('stepped','dark',9,30,step))
            self.assertEqual([int(o['data-value']) for o in doc.minute_options],list(range(0,60,step)))
            self.assertEqual([o['data-value'] for o in doc.minute_options if o['aria-selected']=='true'],['30'])

    def test_invalid_minutes_and_steps_never_round(self):
        for minute,step in ((-1,1),(60,1),(1.5,1),('30',1),(True,1),(None,1),(32,5),(30,0),(30,7),(30,True)):
            with self.assertRaises(ValueError):time_card('invalid','light',9,minute,step)


class ColorBehavior(unittest.TestCase):
    def test_reference_contrast(self):
        self.assertAlmostEqual(ratio('#000000','#FFFFFF'),21)
        self.assertAlmostEqual(ratio('#123456','#123456'),1)

    def test_danger_text_on_actual_component_backgrounds(self):
        from site_support import all_themes
        from build_d import D
        for theme in all_themes():
            for light, base in ((True,theme['vars']),(False,D if theme['letter']=='D' else DARK[theme['letter']])):
                for hc in (False,True):
                    p=finish_palette(base,light,hc)
                    for bg in ('bg','surface','fill','danger_soft'):
                        self.assertGreaterEqual(ratio(p['danger_text'],p[bg]),7 if hc else 4.5,(theme['letter'],light,hc,bg))
    def test_dark_hc_regression(self):
        for key in ('E','F'):
            p=finish_palette(DARK[key],False,True)
            for fg in ('sub','faint','accent_text'):
                for bg in ('bg','surface','fill'):
                    self.assertGreaterEqual(ratio(p[fg],p[bg]),7,(key,fg,bg))
            self.assertEqual(p['bg'],DARK[key]['bg'])

    def test_light_brand_stays_light_but_text_is_readable(self):
        theme=next(t for t in THEMES if t['letter']=='F')
        p=finish_palette(theme['vars'],True)
        self.assertEqual(p['accent'],'#EBB4AC')
        self.assertNotEqual(p['accent_text'],p['accent'])
        self.assertGreaterEqual(ratio(p['accent_text'],p['bg']),4.5)
        self.assertGreaterEqual(ratio(p['accent_deep'],p['accent_soft']),4.5)

    def test_custom_color_extremes_and_idempotence(self):
        for seed in ('#FFFFFF','#000000','#FCE79A','#00FFFF','#FF0000','#6C8FA8'):
            t=theme_from_spec(dict(id='sample',name='Sample',accent=seed))
            for light,p in ((True,t['vars']),(False,t['dark_vars'])):
                self.assertEqual(p,finish_palette(p,light))
                for hc in (False,True):
                    v=finish_palette(p,light,hc)
                    minimum=7 if hc else 4.5
                    for fg,bg in [('accent_text','bg'),('on_accent','accent'),('tone2_text','soft2')]:
                        self.assertGreaterEqual(ratio(v[fg],v[bg]),minimum,(seed,light,hc,fg))

    def test_invalid_specs(self):
        for update in ({'id':'../escape'},{'accent':'red'},{'auxiliary':'red'},{'tertiary':'#12345G'},{'name':'<script>'},{'material':'unknown'},{'unknown':True}):
            with self.assertRaises((ValueError,TypeError)):
                check_spec(dict(id='valid',name='Valid',accent='#112233',**{}) | update)

    def test_three_color_theme_has_independent_roles_in_four_modes(self):
        t=theme_from_spec(dict(id='sunny-test',name='Sunny',accent='#399BE8',auxiliary='#F26B5B',tertiary='#F4C84A'))
        self.assertEqual((t['vars']['accent'],t['vars']['tone2'],t['vars']['tone3']),('#399BE8','#F26B5B','#F4C84A'))
        for light,p in ((True,t['vars']),(False,t['dark_vars'])):
            for hc in (False,True):
                result=finish_palette(p,light,hc)
                target=7 if hc else 4.5
                for color,bg in (('tone2_text','soft2'),('tone3_text','soft3'),('danger_text','bg'),('success_text','success_soft')):
                    self.assertGreaterEqual(ratio(result[color],result[bg]),target,(light,hc,color))
                self.assertNotEqual(result['danger'],result['tone2'])
                self.assertNotEqual(result['success_text'],result['tone3_text'])


class BuildBehavior(unittest.TestCase):
    def test_new_theme_generation_and_repeatability(self):
        with tempfile.TemporaryDirectory(prefix='jp-ui-acceptance-') as temporary:
            project=Path(temporary)/'project';project.mkdir()
            for p in ROOT.glob('*.py'):shutil.copy2(p,project/p.name)
            shutil.copy2(ROOT/'themes.json',project/'themes.json')
            for p in ROOT.glob('*.md'):shutil.copy2(p,project/p.name)
            for name in ('LICENSE','.python-version','.gitignore','.gitattributes','.nojekyll','acceptance-results.json','design-tokens.json'):
                shutil.copy2(ROOT/name,project/name)
            shutil.copytree(ROOT/'docs',project/'docs')
            (project/'skill').mkdir(exist_ok=True)
            shutil.copy2(ROOT/'skill/SKILL.md',project/'skill/SKILL.md')
            shutil.copytree(ROOT/'skill/references',project/'skill/references')
            shutil.copytree(ROOT/'skill/scripts',project/'skill/scripts',ignore=shutil.ignore_patterns('old','__pycache__'))
            env=dict(os.environ,PYTHONIOENCODING='utf-8')
            def run(script,*args,success=True):
                r=subprocess.run([sys.executable,str(project/'skill/scripts'/script),*args],cwd=project,env=env,capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(r.returncode==0,success,r.stdout+'\n'+r.stderr)
                return r
            before=(project/'themes.json').read_bytes()
            run('create_theme.py','--id','../escape','--name','Invalid','--accent','#123456',success=False)
            self.assertEqual(before,(project/'themes.json').read_bytes())
            run('create_theme.py','--id','acceptance-blue','--name','Acceptance blue','--accent','#6C8FA8','--dry-run')
            self.assertEqual(before,(project/'themes.json').read_bytes())
            run('create_theme.py','--id','acceptance-blue','--name','Acceptance blue','--accent','#6C8FA8','--material','glass')
            registered=(project/'themes.json').read_bytes()
            run('create_theme.py','--id','acceptance-blue','--name','Duplicate','--accent','#112233',success=False)
            self.assertEqual(registered,(project/'themes.json').read_bytes())
            run('rebuild.py');run('package_release.py');run('validate.py')
            # Removing the final candidate must be detected even with valid colors.
            hour_output=project/'theme-acceptance-blue.html'
            valid_hour_page=hour_output.read_text(encoding='utf-8')
            hour_output.write_text(valid_hour_page.replace('data-hour="23"','data-hour="22"',1),encoding='utf-8')
            failed=run('validate.py',success=False)
            self.assertIn('hour range/order differs',failed.stdout)
            hour_output.write_text(valid_hour_page.replace('data-minute="59"','data-minute="60"',1),encoding='utf-8')
            failed=run('validate.py',success=False)
            self.assertIn('minute range/order incorrect',failed.stdout)
            hour_output.write_text(valid_hour_page,encoding='utf-8')
            hour_output.write_text(valid_hour_page.replace('.btn-danger{background:var(--danger-soft);color:var(--danger-text)}','.btn-danger{background:var(--danger-soft);color:var(--danger)}',1),encoding='utf-8')
            failed=run('validate.py',success=False)
            self.assertIn('actual component color binding .btn-danger',failed.stdout)
            hour_output.write_text(valid_hour_page,encoding='utf-8')
            run('validate.py')
            glass_output=project/'d-murasaki-ext.html'
            valid_glass_page=glass_output.read_text(encoding='utf-8')
            glass_output.write_text(valid_glass_page.replace('screen dev gspec dark','screen dev gspec',1),encoding='utf-8')
            failed=run('validate.py',success=False)
            self.assertIn('glass sample mode coverage',failed.stdout)
            glass_output.write_text(valid_glass_page,encoding='utf-8')
            run('validate.py')
            result=json.loads((project/'acceptance-results.json').read_text(encoding='utf-8'))
            self.assertEqual(result['status'],'PASS')
            tokens=json.loads((project/'design-tokens.json').read_text(encoding='utf-8'))
            self.assertEqual(tokens['themes']['ACCEPTANCE-BLUE']['light']['accent'],'#6C8FA8')
            def snapshot():
                return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [*project.glob('*.html'),project/'design-tokens.json']}
            first=snapshot();run('rebuild.py');self.assertEqual(first,snapshot())
            run('create_theme.py','--id','acceptance-blue','--name','Acceptance blue','--accent','#738E99','--replace')
            specs=json.loads((project/'themes.json').read_text(encoding='utf-8'))
            self.assertEqual(sum(t['id']=='acceptance-blue' for t in specs),1)
            self.assertEqual(next(t for t in specs if t['id']=='acceptance-blue')['accent'],'#738E99')
            run('validate.py',success=False)  # stale registry must be detected
            run('rebuild.py');run('validate.py')
            # Validate an intentionally corrupted output to prove the checker detects drift.
            output=project/'theme-acceptance-blue-ext.html'
            src=output.read_text(encoding='utf-8')
            marker='.dark.hc{'
            pos=src.index(marker)+len(marker)
            output.write_text(src[:pos]+src[pos:].replace('--sub:','--sub:#111111;--old-sub:',1),encoding='utf-8')
            run('validate.py',success=False)


if __name__=='__main__':
    unittest.main(verbosity=2)
