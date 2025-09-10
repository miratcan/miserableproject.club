from django.utils.text import slugify
from apps.submissions.models import Submission
from django.core.cache import cache


def get_tag_items():
    """Return ordered tag names, tag items and slug-to-name mapping."""
    cache_key = 'tags:v1'
    cached = cache.get(cache_key)
    if cached:
        return cached

    names = []
    for s in Submission.objects.filter(status='published').prefetch_related('stack_tags'):
        names.extend([t for t in s.stack_tags.names() if t])
    seen = set()
    names = [t for t in names if not (t in seen or seen.add(t))]
    tag_items = []
    mapping = {}
    for name in names:
        slug = slugify(name)
        if slug in mapping:
            continue
        mapping[slug] = name
        tag_items.append({'slug': slug, 'name': name})

    data = (names, tag_items, mapping)
    cache.set(cache_key, data, 10 * 60)  # 10 minutes
    return data
