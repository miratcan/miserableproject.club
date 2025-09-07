from django.views.generic import TemplateView
from django.utils.text import slugify
from apps.submissions.models import Submission


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Submission.objects.filter(status='published')
        ctx['submissions'] = qs.order_by('-created_at')[:20]

        # collect available tags and build slug map (name -> slug)
        names = []
        for s in Submission.objects.filter(status='published').only('stack_tags_json'):
            if s.stack_tags_json:
                names.extend([t for t in s.stack_tags_json if isinstance(t, str) and t])
        seen = set()
        names = [t for t in names if not (t in seen or seen.add(t))]
        tag_items = []
        used = set()
        for name in names:
            s = slugify(name)
            if s in used:
                continue
            used.add(s)
            tag_items.append({'slug': s, 'name': name})
        ctx['tags'] = names
        ctx['tag_items'] = tag_items
        ctx['active_tag'] = None
        return ctx


class TagView(TemplateView):
    template_name = 'core/tag.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        page = int(kwargs.get('page') or 1)

        # Build ordered unique tag names and slug map
        names = []
        for s in Submission.objects.filter(status='published').only('stack_tags_json'):
            if s.stack_tags_json:
                names.extend([t for t in s.stack_tags_json if isinstance(t, str) and t])
        seen = set()
        names = [t for t in names if not (t in seen or seen.add(t))]
        mapping = []  # list of tuples (slug, name) preserving order and uniqueness by slug
        used = set()
        for name in names:
            s = slugify(name)
            if s in used:
                continue
            used.add(s)
            mapping.append((s, name))

        slug_to_name = {s: n for s, n in mapping}
        active_name = slug_to_name.get(slug)

        # Build base queryset and filter in Python for SQLite compatibility
        base_qs = Submission.objects.filter(status='published').order_by('-created_at')
        if active_name:
            items = [s for s in base_qs if s.stack_tags_json and active_name in s.stack_tags_json]
        else:
            items = list(base_qs)

        # pagination
        from django.core.paginator import Paginator
        paginator = Paginator(items, 20)
        page_obj = paginator.get_page(page)

        ctx['tag_slug'] = slug
        ctx['tag_name'] = active_name or slug
        ctx['submissions'] = page_obj.object_list
        ctx['paginator'] = paginator
        ctx['page_obj'] = page_obj
        ctx['tags'] = names
        ctx['tag_items'] = [{'slug': s, 'name': n} for s, n in mapping]
        ctx['active_tag'] = slug
        return ctx


    


    
