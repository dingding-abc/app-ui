"""Parse every generated inline script with the installed Node runtime."""
import argparse
import subprocess
import tempfile
import sys
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from component_catalog import SCRIPT

STATE_FIXTURE=r'''
const assert=require('assert/strict'),vm=require('vm');
const timers=[];
const node=()=>({value:'',textContent:'',disabled:false,dataset:{},attrs:{},handlers:{},classes:new Set(),querySelectorAll:()=>[],
  addEventListener(k,f){this.handlers[k]=f},setAttribute(k,v){this.attrs[k]=v},removeAttribute(k){delete this.attrs[k]},
  focus(){this.focused=true},click(){if(!this.disabled)this.handlers.click?.({target:this,currentTarget:this})},
  fire(k){this.handlers[k]?.({target:this,currentTarget:this})}});
const elements=new Map();
const get=s=>{if(!elements.has(s)){const n=node();n.classList={add:k=>n.classes.add(k),remove:(...ks)=>ks.forEach(k=>n.classes.delete(k))};elements.set(s,n)}return elements.get(s)};
const modes=['success','empty','error'].map(mode=>{const n=get('[data-cc-load-mode='+mode+']');n.dataset.ccLoadMode=mode;return n});
const root={querySelector:get,querySelectorAll:s=>s==='[data-cc-load-mode]'?modes:[]};
const context={document:{querySelectorAll:()=>[root]},setTimeout:f=>timers.push(f)};
vm.runInNewContext(SCRIPT,context);
const input=get('[data-cc-required]'),feedback=get('[data-cc-error]');
get('[data-cc-validate]').click();
assert.equal(input.attrs['aria-invalid'],'true');assert.ok(feedback.classes.has('cc-error'));assert.equal(input.focused,true);
input.value='长名称 name';input.fire('input');assert.equal(feedback.textContent,'');assert.equal(input.attrs['aria-invalid'],undefined);
get('[data-cc-validate]').click();assert.equal(input.attrs['aria-invalid'],'false');assert.ok(feedback.classes.has('cc-success'));assert.ok(!feedback.classes.has('cc-error'));
const load=get('[data-cc-load]'),result=get('[data-cc-load-result]');
modes[0].click();assert.ok([load,...modes].every(n=>n.disabled&&n.attrs['aria-busy']==='true'));assert.equal(result.attrs['aria-busy'],'true');
modes[2].click();assert.equal(timers.length,1,'disabled/repeated triggers must not queue extra work');
timers.shift()();assert.equal(result.attrs['aria-busy'],'false');assert.ok(result.classes.has('cc-success'));assert.ok([load,...modes].every(n=>!n.disabled&&n.attrs['aria-busy']===undefined));
modes[2].click();timers.shift()();assert.ok(result.classes.has('cc-error'));assert.ok(!result.classes.has('cc-success'));assert.match(result.textContent,/重试/);
modes[1].click();timers.shift()();assert.ok(!result.classes.has('cc-error'));assert.ok(!result.classes.has('cc-success'));
console.log('PASS: validation error/success/reset; submitting disables all triggers; retry and empty states');
'''

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__();self.active=False;self.parts=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script' and 'src' not in dict(attrs):self.active=True;self.parts=[]
    def handle_data(self,data):
        if self.active:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.active:self.scripts.append(''.join(self.parts));self.active=False

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',default='node');args=parser.parse_args()
    count=0
    with tempfile.TemporaryDirectory(prefix='jp-ui-js-') as temporary:
        source=Path(temporary)/'script.js'
        for page in ROOT.glob('*.html'):
            doc=Scripts();doc.feed(page.read_text(encoding='utf-8'))
            for script in doc.scripts:
                source.write_text(script,encoding='utf-8')
                result=subprocess.run([args.node,'--check',str(source)],capture_output=True,text=True)
                if result.returncode:raise RuntimeError(f'{page.name}: {result.stderr}')
                count+=1
    print(f'PASS: {count} inline scripts parsed across generated pages')
    fixture='const SCRIPT='+json.dumps(SCRIPT)+';\n'+STATE_FIXTURE
    result=subprocess.run([args.node,'-e',fixture],capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    print(result.stdout.strip())

if __name__=='__main__':main()
