"""Build a deterministic, relocatable source and preview ZIP (stdlib only)."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
NAME = 'jp-min-ui-kit-5.1.zip'


def release_files(root):
    fixed = ['AGENTS.md', 'PROJECT.md', 'README.md', 'ACCEPTANCE.md', 'ACCEPTANCE_REPORT.md',
             'LICENSE', '.python-version', 'themes.json', 'design-tokens.json',
             'acceptance-results.json', '.gitignore', '.gitattributes', '.nojekyll']
    files = [root / name for name in fixed]
    files += sorted(root.glob('*.py')) + sorted(root.glob('*.html'))
    files += sorted((root / 'docs').glob('*.md'))
    files += sorted((root / 'docs/previews').glob('*.md'))
    files += sorted((root / 'docs/previews').glob('*.jpg'))
    files += sorted((root / 'skill').glob('*.md'))
    files += sorted((root / 'skill/references').glob('*.md'))
    files += sorted((root / 'skill/scripts').glob('*.py'))
    files += sorted((root / 'native').glob('*'))
    unique = {p.relative_to(root).as_posix(): p for p in files}
    missing = [n for n,p in unique.items() if not p.is_file()]
    if missing:
        raise FileNotFoundError('Release source missing: ' + ', '.join(missing))
    return sorted(unique.items())


def build(root=ROOT):
    root=Path(root).resolve();dest=root/'dist';dest.mkdir(exist_ok=True)
    rows=release_files(root)
    contents={name:path.read_bytes() for name,path in rows}
    # The extracted archive cannot contain itself. Point its offline download page
    # at the included manifest until the user rebuilds, which creates a new ZIP.
    offline=contents['reuse.html'].decode('utf-8')
    offline=offline.replace('<a href="dist/jp-min-ui-kit-5.1.zip" download>下载完整离线 ZIP</a> · <a href="dist/jp-min-ui-kit-5.1.zip.sha256" download>下载 ZIP SHA256</a>', '<a href="MANIFEST.sha256">查看已下载归档的文件清单</a>')
    contents['reuse.html']=offline.encode('utf-8')
    manifest=''.join(f'{hashlib.sha256(contents[name]).hexdigest()}  {name}\n' for name,_ in rows).encode('utf-8')
    output=dest/NAME
    with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in [*rows,('MANIFEST.sha256',None)]:
            info=ZipInfo('jp-min-ui-kit/'+name,(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=0o644 << 16
            archive.writestr(info,manifest if path is None else contents[name],compress_type=ZIP_DEFLATED,compresslevel=9)
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    (dest/(NAME+'.sha256')).write_text(f'{digest}  {NAME}\n',encoding='ascii')
    print(json.dumps({'archive':str(output),'sha256':digest,'files':len(rows)},ensure_ascii=False))
    return output


if __name__=='__main__':
    build()
