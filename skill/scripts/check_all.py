"""Run every maintained Python entry point in a disposable project copy."""
import argparse
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile

from package_release import release_files

ROOT = Path(__file__).resolve().parents[2]
GENERATORS = ('build.py', 'build_d.py', 'build_d_ext.py', 'build_devices.py', 'build_ext.py')
MODULES = ('adaptive_demo.py', 'catalog_pages.py', 'component_catalog.py', 'design_tokens.py',
           'hour_picker.py', 'shape_tokens.py', 'site_support.py', 'theme_registry.py', 'widget_spec.py', 'ui_contract.py')
SCRIPTS = ('create_theme.py', 'rebuild.py', 'package_release.py', 'validate.py', 'test_system.py',
           'test_release.py', 'test_browser_scripts.py', 'test_picker_state.py', 'test_adaptive_layout.py', 'preview_stress.py')
JS_SCRIPTS = ('test_browser_scripts.py', 'test_picker_state.py', 'test_adaptive_layout.py')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default='node', help='Node executable for JavaScript checks')
    parser.add_argument('--python-only', action='store_true', help='Explicitly skip JavaScript checks')
    parser.add_argument('--output-json', type=Path, help='Save the successful run report')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10 or later is required')
    node = shutil.which(args.node)
    if not args.python_only and not node:
        parser.error('Node is required for the complete check; use --node PATH or --python-only')
    files = [*ROOT.glob('*.py'), *(ROOT / 'skill/scripts').glob('*.py')]
    expected = {*GENERATORS, *MODULES, *(f'skill/scripts/{name}' for name in SCRIPTS),
                'skill/scripts/check_all.py'}
    actual = {path.relative_to(ROOT).as_posix() for path in files}
    if actual != expected:
        parser.error(f'Update the check inventory: missing={sorted(expected-actual)}, new={sorted(actual-expected)}')
    report = {'python': sys.version.split()[0], 'platform': sys.platform, 'files': [], 'native_tokens': 'SKIPPED'}
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    with tempfile.TemporaryDirectory(prefix='app-ui-check-') as temporary:
        project = Path(temporary) / 'app-ui'
        project.mkdir()
        for name, source in release_files(ROOT):
            target = project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        for name in sorted(actual):
            py_compile.compile(str(project / name), doraise=True)

        def run(name, *arguments):
            result = subprocess.run([sys.executable, str(project / name), *arguments], cwd=project,
                                    env=env, capture_output=True, text=True, encoding='utf-8', timeout=180)
            if result.returncode:
                print(result.stdout + result.stderr, file=sys.stderr)
                raise SystemExit(f'FAIL: {name} (exit {result.returncode})')
            report['files'].append({'file': name, 'status': 'PASS'})
            print(f'PASS: {name}')

        # These modules have no CLI; execute their imports independently, then
        # exercise their functions through the generators and behavior tests.
        for name in MODULES + GENERATORS:
            run(name)
        for name in SCRIPTS:
            relative = f'skill/scripts/{name}'
            if name in JS_SCRIPTS and args.python_only:
                report['files'].append({'file': relative, 'status': 'SKIPPED: requires Node'})
                print(f'SKIPPED: {relative} (requires Node)')
                continue
            arguments = ()
            if name == 'create_theme.py':
                arguments = ('--id', 'smoke-blue', '--name', 'Smoke blue', '--accent', '#6C8FA8', '--dry-run')
            elif name in JS_SCRIPTS:
                arguments = ('--node', node)
            run(relative, *arguments)
        if not args.python_only:
            result = subprocess.run([node, '--test', 'native/test-tokens.cjs'], cwd=project, env=env,
                                    capture_output=True, text=True, encoding='utf-8', timeout=60)
            if result.returncode:
                raise SystemExit(result.stdout + result.stderr)
            report['native_tokens'] = 'PASS'
    report['files'].append({'file': 'skill/scripts/check_all.py', 'status': 'PASS'})
    report['status'] = 'PASS_WITH_SKIPS' if args.python_only else 'PASS'
    print(f"{report['status']}: Python {report['python']}, {len(report['files'])} maintained Python files")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
