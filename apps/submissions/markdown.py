import markownify

ALLOWED_TAGS = [
    'p', 'br', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'em', 'strong',
    'h3', 'h4', 'h5', 'h6', 'a'
]
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel'],
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def render_markdown(md_text: str) -> str:
    return markownify.render(
        md_text,
        tags=ALLOWED_TAGS,
        attrs=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
    )
