from django.views.generic import TemplateView
from apps.submissions.models import Submission
from .utils import get_tag_items


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Submission.objects.filter(status='published')
        ctx['submissions'] = qs.order_by('-created_at')[:20]

        names, tag_items, _ = get_tag_items()
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

        names, tag_items, mapping = get_tag_items()
        active_name = mapping.get(slug)

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
        ctx['tag_items'] = tag_items
        ctx['active_tag'] = slug
        return ctx


    


    
