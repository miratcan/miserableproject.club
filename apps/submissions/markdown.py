import markdown as _md
import bleach


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
    # Ensure links have rel
    def _add_rel(m):
        return m.replace('<a ', '<a rel="nofollow noopener" ', 1) if ' rel=' not in m else m
    # quick and simple injection for rel attr
    cleaned = cleaned.replace('<a ', '<a rel="nofollow noopener" ')
    return cleaned

