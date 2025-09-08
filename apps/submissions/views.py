from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, FormView, View

from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Submission
from .forms import SubmissionForm
from .markdown import render_markdown


class SubmissionDetailView(DetailView):
    model = Submission
    template_name = 'submissions/detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status='published')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = self.object
        ctx['html'] = {
            'idea': render_markdown(s.idea),
            'tech': render_markdown(s.tech),
            'wins': render_markdown(s.wins),
            'failure': render_markdown(s.failure),
            'lessons': render_markdown(s.lessons),
        }
        return ctx


class SubmitView(LoginRequiredMixin, FormView):
    template_name = 'submissions/submit.html'
    form_class = SubmissionForm

    def dispatch(self, request, *args, **kwargs):
        self.instance = None
        slug = kwargs.get('slug')
        if slug:
            try:
                self.instance = Submission.objects.get(slug=slug, user=request.user, status='draft')
            except Submission.DoesNotExist:
                return redirect('submit')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.instance:
            kwargs['instance'] = self.instance
        return kwargs

    def form_valid(self, form):
        if 'preview' in self.request.POST:
            # save as draft and redirect to preview page
            s = form.save(commit=False)
            s.user = self.request.user
            s.links_json = form.cleaned_data.get('links_json', [])
            s.status = 'draft'
            s.save()
            form.save_m2m()
            return redirect('submission_preview', slug=s.slug)

        # publish
        s = form.save(commit=False)
        s.user = self.request.user
        # attach parsed json fields
        s.links_json = form.cleaned_data.get('links_json', [])
        s.status = 'published'
        s.save()
        form.save_m2m()
        return redirect(s.get_absolute_url())


class LatestFeed(Feed):
    title = "miserableproject.club — Latest Submissions"
    link = "/rss.xml"
    description = "Latest 50 posts"

    def items(self):
        return Submission.objects.filter(status='published').order_by('-created_at')[:50]

    def item_title(self, item: Submission):
        return item.project_name

    def item_description(self, item: Submission):
        return item.tagline

    def item_link(self, item: Submission):
        return reverse('submission_detail', args=[item.slug])


class DraftPreviewView(LoginRequiredMixin, DetailView):
    model = Submission
    template_name = 'submissions/detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status='draft', user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = self.object
        ctx['html'] = {
            'idea': render_markdown(s.idea),
            'tech': render_markdown(s.tech),
            'wins': render_markdown(s.wins),
            'failure': render_markdown(s.failure),
            'lessons': render_markdown(s.lessons),
        }
        ctx['is_preview'] = True
        return ctx


class PublishDraftView(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            s = Submission.objects.get(slug=slug, user=request.user, status='draft')
        except Submission.DoesNotExist:
            return redirect('submission_detail', slug=slug)
        s.status = 'published'
        s.save(update_fields=['status'])
        return redirect(s.get_absolute_url())
