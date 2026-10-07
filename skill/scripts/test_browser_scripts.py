"""Parse every generated inline script with the installed Node runtime."""
import argparse
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

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

if __name__=='__main__':main()
