import pathlib
import os
assert os.sep == '/', 'Not implemented yet for Windows system.'
import argparse
import json
import contextlib


FRIENDLY = pathlib.Path.home() / '.local/share/nvim/lazy/friendly-snippets'
CYTHON = pathlib.Path.home() / '.local/share/nvim/lazy/cython-snips'


def _symlink(link, file, create=True):
    with contextlib.suppress(Exception):
        if create:
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(file)
        else:
            link.unlink()


def _package(package):
    with open(package, 'r') as j:
        package = json.load(j)
    return package['contributes']['snippets']


def _generator():
    for item in _package(FRIENDLY / 'package.json'):
        file = FRIENDLY / item['path']
        language = item['language']
        yield file, language


def friendly(create=True):
    for file, language in _generator():
        if not isinstance(language, (list, tuple)):
            language = [language]
        links = []
        for l in language:
            filename = file.stem
            if filename != l:
                link = file.parent / filename / f'{l}.json'
                links.append(link)
        for link in links:
            _symlink(link, file, create)


def cython(create=True):
    for file, language in _generator():
        if language == 'python':
            link = CYTHON / file.relative_to(FRIENDLY)
            _symlink(link, file, create)

    package_json = CYTHON / 'package.json'
    package = {
        'contributes': {
            'snippets': []
        }
    }
    for item in CYTHON.glob('**/*.json'):
        if item.as_posix() == package_json.as_posix():
            continue
        relative = item.relative_to(CYTHON)
        # TODO:
        # 1. Create symlink of `cython.json` from python snippets.
        # 2. Write package.json
        path = relative.parent / item.stem / 'cython.json'
        pack = {
            'language': 'cython',
            'path': path.as_posix()
        }
        package['contributes']['snippets'].append(pack)

    print(package)

    # package_json.parent.mkdir(parents=True, exist_ok=True)
    # with open(package_json, 'w') as j:
    #     json.dump(package, j)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fn')
    parser.add_argument('--no-create', action='store_true')
    args = parser.parse_args()

    if args.fn:
        eval(f'{args.fn}(create={not args.no_create})')
