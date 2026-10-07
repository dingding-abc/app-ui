"""Check deterministic ZIP, offline links, manifest and relocated rebuild."""
import hashlib
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from package_release import build

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('a','img'):
            href=dict(attrs).get('href' if tag=='a' else 'src','')
            if href and not href.startswith(('http:','https:','mailto:','#')):
                self.links.append(href.partition('#')[0])

def verify():
    archive=build(ROOT);first=hashlib.sha256(archive.read_bytes()).hexdigest()
    second=hashlib.sha256(build(ROOT).read_bytes()).hexdigest()
    assert first==second,'Repeated package differs'
    with tempfile.TemporaryDirectory(prefix='jp-ui-release-') as temporary:
        target=Path(temporary)
        with ZipFile(archive) as package:
            entries=package.namelist()
            assert len(entries)==len(set(entries))
            assert all(name.startswith('jp-min-ui-kit/') and '..' not in Path(name).parts for name in entries)
            manifest=package.read('jp-min-ui-kit/MANIFEST.sha256').decode('utf-8')
            for row in manifest.splitlines():
                digest,name=row.split('  ',1)
                assert hashlib.sha256(package.read('jp-min-ui-kit/'+name)).hexdigest()==digest,name
            package.extractall(target)
        project=target/'jp-min-ui-kit'
        for page in project.glob('*.html'):
            links=Links();links.feed(page.read_text(encoding='utf-8'))
            for href in links.links:
                if href:assert (project/href).exists(),f'{page.name}: {href}'
        subprocess.run([sys.executable,str(project/'skill/scripts/rebuild.py')],cwd=project,check=True,capture_output=True)
        subprocess.run([sys.executable,str(project/'skill/scripts/package_release.py')],cwd=project,check=True,capture_output=True)
        subprocess.run([sys.executable,str(project/'skill/scripts/validate.py')],cwd=project,check=True,capture_output=True)
        print(f'PASS: repeatable ZIP {first}, {len(entries)} entries, offline links and relocated rebuild')

if __name__=='__main__':
    verify()
