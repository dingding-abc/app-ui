"""Exercise the generated fold state logic at minimum-width boundaries."""
import argparse
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CHECK=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(process.argv[1],'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const classes=new Set();
const frame={clientWidth:274,style:{setProperty(k,v){this[k]=v}},dataset:{},classList:{
  add(k){classes.add(k)},remove(...names){names.forEach(n=>classes.delete(n))},
  contains(k){return classes.has(k)},toggle(k,on){if(on)classes.add(k);else classes.delete(k)}
}};
const values={scenario:'2',width:'280',height:'560','safe-left':'60','safe-right':'60',hinge:'20','control-align':'center'};
const elements={frame};
for(const [id,value] of Object.entries(values))elements[id]={value,addEventListener(){}};
elements['layout-note']={textContent:''};
elements.draft={value:'准备出发',addEventListener(){}};
elements.save={addEventListener(){}};
const context={document:{getElementById:id=>elements[id],querySelectorAll:()=>[]},ResizeObserver:class{observe(){}},console};
vm.runInNewContext(script,context,{filename:'adaptive.html'});
function scenario(width,left,right,hinge){
  Object.assign(elements.width,{value:String(width)});
  elements['safe-left'].value=String(left);elements['safe-right'].value=String(right);elements.hinge.value=String(hinge);
  frame.clientWidth=width-6;context.render();
  return {single:classes.has('fold-single'),unavailable:classes.has('fold-unavailable'),note:elements['layout-note'].textContent};
}
assert.equal(scenario(280,60,60,20).unavailable,true,'59px pane cannot hold a 44px control inside padded card');
assert.equal(scenario(280,40,60,20).unavailable,true,'79px pane is below the safe minimum');
assert.equal(scenario(280,39,60,20).single,true,'80px pane can use one side');
assert.equal(scenario(330,120,0,20).single,true,'asymmetric narrow fold uses the right side');
const wide=scenario(680,120,0,20);
assert.equal(wide.single,false);assert.equal(wide.unavailable,false);
assert.equal(frame.style['--fold-pad-left'],'120px');
console.log('PASS: fold geometry at 59/79/80px, asymmetric narrow and two-column cases');
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',default='node');args=parser.parse_args()
    result=subprocess.run([args.node,'-e',CHECK,str(ROOT/'adaptive.html')],capture_output=True,text=True)
    if result.returncode:raise SystemExit(result.stdout+result.stderr)
    print(result.stdout.strip())

if __name__=='__main__':main()
