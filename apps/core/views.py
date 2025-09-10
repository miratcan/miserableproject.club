from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.http import Http404
from django.urls import reverse
from django.contrib.auth import login as auth_login
from apps.submissions.models import Submission
from .utils import get_tag_items
from .forms import SignupForm


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

        qs = Submission.objects.filter(status='published').order_by('-created_at')
        if active_name:
            qs = qs.filter(tags__name__in=[active_name])

        from django.core.paginator import Paginator
        paginator = Paginator(qs, 20)
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

        ctx['profile_user'] = user
        ctx['submissions'] = page_obj.object_list
        ctx['paginator'] = paginator
        ctx['page_obj'] = page_obj
        return ctx


class MyProfileRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse('login')
        return reverse('user_profile', args=[self.request.user.username])


class SignupView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')
