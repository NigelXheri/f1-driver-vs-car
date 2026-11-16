#!/usr/bin/env python3
"""Publish saved notebook cells as static reading pages; never execute code.

Build dependency: pip install -r scripts/build/notebook-requirements.txt
Run from any directory: python scripts/build/build_notebook_pages.py
"""
import base64
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil

import mistune

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'src' / 'result_showcase_website'
DEST = SITE / 'notebooks'
NOTEBOOKS = [
    ('01_lap_times_eda', 'Lap-time quality & coverage', 'Explore the 639,293 recorded laps: coverage, missing values, duration formats, unusual timings and race-level patterns.'),
    ('02_lap_performance', 'What shapes lap pace?', 'Follow the detailed analysis of circuits, teammate gaps, constructor pace and race progression, including selection rules.'),
    ('02_driver_career_eda', 'Driver careers & peak performance', 'Explore peak ages and career stages for 15 selected drivers, then the Welch and early/later career tests and their uncertainty.'),
    ('03_lap_time_analysis', 'Lap-performance findings', 'Read the streamlined findings: circuit associations, the 0.611-second teammate gap, 2024 constructor pace and race progression.'),
]
markdown = mistune.create_markdown(escape=True, plugins=['table'])


def text(value):
    return ''.join(value) if isinstance(value, list) else str(value)


class TableHTML(HTMLParser):
    """Retain saved table formatting without scripts, styles or active content."""
    tags = {'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
            'div', 'p', 'span', 'b', 'strong', 'em', 'i', 'br', 'pre', 'code'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.blocked = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.blocked += 1
        elif not self.blocked and tag in self.tags:
            safe = ''.join(f' {key}="{html.escape(value, quote=True)}"'
                           for key, value in attrs
                           if key in {'colspan', 'rowspan'} and value and value.isdigit())
            self.parts.append(f'<{tag}{safe}>')

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.blocked = max(0, self.blocked - 1)
        elif not self.blocked and tag in self.tags and tag != 'br':
            self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.blocked:
            self.parts.append(html.escape(data))


def pre(value):
    clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text(value))
    return f'<pre>{html.escape(clean)}</pre>'


def output_html(output, stem, cell, index):
    data = output.get('data', {})
    if 'image/png' in data:
        filename = f'{stem}-cell-{cell}-output-{index}.png'
        (DEST / 'figures' / filename).write_bytes(base64.b64decode(text(data['image/png'])))
        return (f'<figure><a href="figures/{filename}"><img loading="lazy" '
                f'src="figures/{filename}" alt="Saved notebook figure, cell {cell}, output {index + 1}"></a>'
                f'<figcaption>Original saved figure · cell {cell} · <a href="figures/{filename}">Open full size</a></figcaption></figure>')
    if 'text/html' in data:
        parser = TableHTML()
        parser.feed(text(data['text/html']))
        return '<div class="table-scroll">' + ''.join(parser.parts) + '</div>'
    if 'text/markdown' in data:
        return markdown(text(data['text/markdown']))
    if 'text/plain' in data:
        return pre(data['text/plain'])
    if 'text' in output:
        return pre(output['text'])
    if output.get('output_type') == 'error':
        return pre('\n'.join(output.get('traceback', [output.get('evalue', 'Saved error')])))
    return '<p>Output format available in the downloadable notebook.</p>'


def build():
    (DEST / 'figures').mkdir(parents=True, exist_ok=True)
    cards = []
    for stem, title, description in NOTEBOOKS:
        source = ROOT / 'notebooks' / f'{stem}.ipynb'
        notebook = json.loads(source.read_text(encoding='utf-8'))
        shutil.copyfile(source, DEST / source.name)
        cells, contents = [], []
        for index, cell in enumerate(notebook['cells']):
            value = text(cell.get('source', ''))
            if cell['cell_type'] == 'markdown':
                heading = re.search(r'^#{1,6}\s+(.+)', value, re.M)
                if heading:
                    contents.append(f'<li><a href="#cell-{index}">{html.escape(heading[1])}</a></li>')
                content = markdown(value)
            elif cell['cell_type'] == 'code':
                content = f'<details class="code-cell"><summary>Show code · cell {index}</summary>{pre(value)}</details>'
                outputs = cell.get('outputs', [])
                content += ''.join(f'<div class="saved-output">{output_html(o, stem, index, j)}</div>' for j, o in enumerate(outputs))
                if not outputs:
                    content += '<p class="empty-output">No saved output for this cell.</p>'
            else:
                content = pre(value)
            cells.append(f'<section class="notebook-cell" id="cell-{index}" data-cell="{index}">{content}</section>')
        page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'self'; base-uri 'none'">
<title>{html.escape(title)} — The Science of Speed</title><link rel="icon" href="../assets/mark.svg"><link rel="stylesheet" href="reader.css"></head>
<body><a class="skip" href="#analysis">Skip to analysis</a><header><a href="../index.html#archive">← The Science of Speed / Archive</a><a href="{stem}.ipynb" download>Download notebook ↓</a></header>
<main><div class="reader-intro"><p class="eyebrow">NOTEBOOK {stem[:2]} / SAVED ANALYSIS</p><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p>
<p class="snapshot">These are the notebook’s saved narrative and outputs, exported without running code. Original wording and any inconsistencies are retained; see the <a href="../REPOSITORY_AUDIT.md">claim audit</a> and <a href="../FINDINGS.md">reviewed findings</a> for corrections. Cell numbers are zero-based. Downloads need the repository’s data and Python dependencies to run.</p>
<details class="contents"><summary>On this page</summary><ol>{''.join(contents)}</ol></details></div>
<article id="analysis" aria-label="Notebook analysis">{''.join(cells)}</article>
<footer><a href="../index.html#archive">← Back to the project archive</a><a href="{stem}.ipynb" download>Download original .ipynb ↓</a></footer></main></body></html>'''
        (DEST / f'{stem}.html').write_text(page, encoding='utf-8', newline='\n')
        cards.append(f'''<article class="notebook-card"><p class="eyebrow">NOTEBOOK {stem[:2]} / RESEARCH</p><h3>{html.escape(title)}</h3><p>{html.escape(description)}</p><div class="notebook-actions"><a class="text-link notebook-analysis-link" href="notebooks/{stem}.html" aria-label="View analysis: {html.escape(title, quote=True)}">View analysis →</a><a class="text-link" href="notebooks/{stem}.ipynb" download>Download notebook ↓</a></div></article>''')
        print(f'Exported {stem}: {len(notebook["cells"])} cells')
    index = SITE / 'index.html'
    markup = index.read_text(encoding='utf-8')
    start, end = '<!-- notebook-cards:start -->', '<!-- notebook-cards:end -->'
    if start not in markup or end not in markup:
        raise ValueError('Notebook card markers are missing from index.html')
    before, rest = markup.split(start, 1)
    _, after = rest.split(end, 1)
    index.write_text(before + start + '\n<div class="notebook-grid">' + '\n'.join(cards) + '</div>\n' + end + after, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    build()
