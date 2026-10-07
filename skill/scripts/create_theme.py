"""Register a requested brand color without editing component templates."""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--id',required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('--accent',required=True)
    parser.add_argument('--dark-accent')
    parser.add_argument('--auxiliary',help='Second decorative brand color (#RRGGBB)')
    parser.add_argument('--tertiary',help='Third decorative brand color (#RRGGBB)')
    parser.add_argument('--description')
    parser.add_argument('--material',choices=['paper','glass'],default='paper')
    parser.add_argument('--replace',action='store_true',help='Replace this existing custom id only')
    parser.add_argument('--dry-run',action='store_true',help='Validate and show palette without writing')
    args=parser.parse_args()
    project=args.project.resolve()
    sys.path.insert(0,str(project))
    from theme_registry import check_spec,theme_from_spec
    spec={k:getattr(args,k) for k in ('id','name','accent','dark_accent','auxiliary','tertiary','description','material') if getattr(args,k) is not None}
    try:
        check_spec(spec)
        theme=theme_from_spec(spec)
        registry=project/'themes.json'
        existing=json.loads(registry.read_text(encoding='utf-8')) if registry.exists() else []
        if any(t['id']==args.id for t in existing) and not args.replace:
            raise ValueError('This custom id already exists; use --replace only for an intentional update')
        if args.dry_run:
            print(json.dumps(theme,ensure_ascii=False,indent=2))
            return
        updated=[t for t in existing if t['id']!=args.id]+[spec]
        # Validate every record before atomically replacing the registry.
        for item in updated:
            theme_from_spec(item)
        temp=registry.with_suffix('.json.tmp')
        temp.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temp.replace(registry)
        print(f'Registered {args.id}. Run rebuild.py, then validate.py.')
    except (ValueError,KeyError,TypeError) as exc:
        parser.error(str(exc))


if __name__=='__main__':
    main()
