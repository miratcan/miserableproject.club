import markdown as _md
import bleach
import re


ALLOWED_TAGS = [
    'p', 'br', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'em', 'strong',
    'h3', 'h4', 'h5', 'h6', 'a'
]
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel'],
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def render_markdown(md_text: str) -> str:
    if not md_text:
        return ''
    html = _md.markdown(md_text, extensions=['extra', 'sane_lists', 'nl2br'])
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    # Ensure links without a rel attribute get the default
    cleaned = re.sub(
        r"<a(?![^>]*\brel=)([^>]*)>",
        r'<a\1 rel="nofollow noopener">',
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned

