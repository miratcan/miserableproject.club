from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import get_user_model
from django.http import Http404
from django.urls import reverse
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
        base_qs = Submission.objects.filter(status='published').prefetch_related('stack_tags').order_by('-created_at')
        if active_name:
            items = [s for s in base_qs if active_name in s.stack_tags.names()]
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


class UserProfileView(TemplateView):
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        username = kwargs.get('username')
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404("User not found")

        # Respect anonymity: do not list anonymous posts on profile
        from apps.submissions.models import Submission
        published_qs = (
            Submission.objects
            .filter(status='published', user=user, is_anonymous=False)
            .order_by('-created_at')
        )

        # Pagination for published items
        from django.core.paginator import Paginator
        page = int(self.request.GET.get('page') or 1)
        paginator = Paginator(published_qs, 20)
        page_obj = paginator.get_page(page)

        # If owner viewing their own profile, also include drafts (not paginated)
        draft_items = None
        if self.request.user.is_authenticated and self.request.user == user:
            draft_qs = (
                Submission.objects
                .filter(status='draft', user=user)
                .order_by('-updated_at')
            )
            dpage = int(self.request.GET.get('dpage') or 1)
            draft_paginator = Paginator(draft_qs, 20)
            draft_page_obj = draft_paginator.get_page(dpage)
            draft_items = draft_page_obj.object_list

        ctx['profile_user'] = user
        ctx['submissions'] = page_obj.object_list
        ctx['paginator'] = paginator
        ctx['page_obj'] = page_obj
        if draft_items is not None:
            ctx['draft_submissions'] = draft_items
            ctx['draft_paginator'] = draft_paginator
            ctx['draft_page_obj'] = draft_page_obj
        return ctx


class MyProfileRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse('account_login')
        return reverse('user_profile', args=[self.request.user.username])
