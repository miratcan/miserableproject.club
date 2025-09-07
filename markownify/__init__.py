import markdown as _md
import bleach
import re

DEFAULT_TAGS = [
    'p', 'br', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'em', 'strong',
    'h3', 'h4', 'h5', 'h6', 'a'
]
DEFAULT_ATTRS = {
    'a': ['href', 'title', 'rel'],
}
DEFAULT_PROTOCOLS = ['http', 'https', 'mailto']


def render(md_text: str, *, tags=None, attrs=None, protocols=None) -> str:
    """Render markdown text to sanitized HTML."""
    if not md_text:
        return ''
    html = _md.markdown(md_text, extensions=['extra', 'sane_lists', 'nl2br'])
    cleaned = bleach.clean(
        html,
        tags=tags or DEFAULT_TAGS,
        attributes=attrs or DEFAULT_ATTRS,
        protocols=protocols or DEFAULT_PROTOCOLS,
        strip=True,
    )
    cleaned = re.sub(
        r"<a(?![^>]*\brel=)([^>]*)>",
        r'<a\1 rel="nofollow noopener">',
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned
