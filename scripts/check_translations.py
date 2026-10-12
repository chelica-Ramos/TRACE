"""Check matching translation keys/placeholders and generate the review list.

Run: python scripts/check_translations.py
"""
import json
from pathlib import Path
from string import Formatter

ROOT = Path(__file__).resolve().parents[1]


def check():
    catalogs = {
        lang: json.loads((ROOT / 'locales' / f'{lang}.json').read_text(encoding='utf-8'))
        for lang in ('en', 'tl')
    }
    en, tl = catalogs['en'], catalogs['tl']
    assert en.keys() == tl.keys(), f'Key mismatch: {en.keys() ^ tl.keys()}'
    for key, english in en.items():
        assert isinstance(tl[key], str) and tl[key].strip(), key
        fields = lambda text: {name for _, name, _, _ in Formatter().parse(text) if name is not None}
        if key != 'pie_hover':
            assert fields(english) == fields(tl[key]), f'Placeholder mismatch: {key}'
    # Catch misspelled literal lookup keys in the live Python source.
    import ast
    for filename in ('app.py', 'tracey_component.py', 'i18n.py'):
        for node in ast.walk(ast.parse((ROOT / filename).read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 't':
                if node.args and isinstance(node.args[0], ast.Constant):
                    assert node.args[0].value in en, f'{filename}: {node.args[0].value}'
    docs = ROOT / 'docs'
    docs.mkdir(exist_ok=True)
    def cell(text):
        return text.replace('|', '\\|').replace('\n', '<br>')
    rows = ['# TRACE translation review', '', 'Every app-owned string in the EN/TL dictionaries is listed below.',
            'Technical terms and proper names intentionally remain in English where natural.', '',
            '| Key | English | Tagalog |', '| --- | --- | --- |']
    rows.extend(f'| `{key}` | {cell(english)} | {cell(tl[key])} |' for key, english in en.items())
    (docs / 'translations-review.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'PASS: {len(en)} matching EN/TL keys, format placeholders, and Python lookups. Review: docs/translations-review.md')


if __name__ == '__main__':
    check()
