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


def test_allowed_tags_preserved():
    html = render_markdown("**bold**")
    assert '<strong>bold</strong>' in html


def test_disallowed_tags_stripped():
    html = render_markdown('<span>hi</span>')
    assert '<span>' not in html
    assert 'hi' in html


def test_disallowed_attribute_removed():
    html = render_markdown('<a href="https://example.com" onclick="alert(1)">link</a>')
    assert 'onclick' not in html
    assert 'href="https://example.com"' in html


def test_allowed_protocols_preserved():
    html = render_markdown('[mail](mailto:test@example.com)')
    assert 'href="mailto:test@example.com"' in html


def test_disallowed_protocol_removed():
    html = render_markdown('[bad](javascript:alert(1))')
    assert 'href' not in html
    assert '<a rel="nofollow noopener">bad</a>' in html

