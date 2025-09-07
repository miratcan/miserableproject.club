from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))
from apps.submissions.markdown import render_markdown


def test_adds_rel_when_missing():
    html = render_markdown("[link](https://example.com)")
    assert '<a href="https://example.com" rel="nofollow noopener">' in html


def test_existing_rel_preserved():
    html = render_markdown('<a href="https://example.com" rel="me">link</a>')
    assert 'rel="me"' in html
    assert 'nofollow' not in html

