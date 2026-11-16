"""Read-only checks for the published notebook pages and original downloads."""
import base64
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.cells = [], [], []
        self.scripts = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.scripts += tag == 'script'
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'data-cell' in attrs:
            self.cells.append(int(attrs['data-cell']))


class NotebookPagesTests(unittest.TestCase):
    def test_saved_cells_figures_and_original_downloads(self):
        sources = sorted(p for p in (ROOT / 'notebooks').glob('*.ipynb')
                         if p.stem != '00_build_dataset_csvs')
        self.assertEqual(len(sources), 4)
        home = (SITE / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('00_build_dataset_csvs', home)
        self.assertFalse((SITE / 'notebooks' / '00_build_dataset_csvs.html').exists())
        self.assertEqual(home.count('class="text-link notebook-analysis-link"'), 4)
        for source in sources:
            with self.subTest(notebook=source.name):
                folder = SITE / 'notebooks'
                self.assertEqual(source.read_bytes(), (folder / source.name).read_bytes())
                self.assertIn(f'href="notebooks/{source.stem}.html"', home)
                self.assertIn(f'href="notebooks/{source.name}" download', home)
                notebook = json.loads(source.read_text(encoding='utf-8'))
                markup = (folder / f'{source.stem}.html').read_text(encoding='utf-8')
                page = Page(markup)
                self.assertEqual(page.cells, list(range(len(notebook['cells']))))
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertEqual(page.scripts, 0, 'saved code must never execute')
                self.assertEqual(markup.count('<details class="code-cell">'),
                                 sum(c['cell_type'] == 'code' for c in notebook['cells']))
                self.assertEqual(markup.count('<div class="saved-output">'),
                                 sum(len(c.get('outputs', [])) for c in notebook['cells']))
                for link in page.links:
                    url = urlsplit(link)
                    if not url.scheme and not url.netloc:
                        if url.path:
                            self.assertTrue((folder / unquote(url.path)).is_file(), link)
                        elif url.fragment:
                            self.assertIn(url.fragment, page.ids)
                figures = []
                for i, cell in enumerate(notebook['cells']):
                    for j, output in enumerate(cell.get('outputs', [])):
                        png = output.get('data', {}).get('image/png')
                        if png:
                            name = f'{source.stem}-cell-{i}-output-{j}.png'
                            figures.append(name)
                            self.assertEqual((folder / 'figures' / name).read_bytes(),
                                             base64.b64decode(''.join(png)))
                            self.assertIn(f'src="figures/{name}"', markup)
                self.assertEqual(len(re.findall(r'<img\b', markup)), len(figures))


if __name__ == '__main__':
    unittest.main()
