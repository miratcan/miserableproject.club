from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, FormView
from django.utils import timezone
from django.http import Http404

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
        return qs.exclude(status='removed')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = self.object
        ctx['html'] = {
            'idea': render_markdown(s.idea_md),
            'tech': render_markdown(s.tech_md),
            'execution': render_markdown(s.execution_md),
            'failure': render_markdown(s.failure_md),
            'lessons': render_markdown(s.lessons_md),
        }
        return ctx


class SubmitView(LoginRequiredMixin, FormView):
    template_name = 'submissions/submit.html'
    form_class = SubmissionForm

    def form_valid(self, form):
        if 'preview' in self.request.POST:
            # just render preview
            ctx = self.get_context_data(form=form)
            data = form.cleaned_data
            ctx['preview'] = {
                'title': data['title'],
                'snapshot': data['snapshot'],
                'idea': render_markdown(data['idea_md']),
                'tech': render_markdown(data['tech_md']),
                'execution': render_markdown(data['execution_md']),
                'failure': render_markdown(data['failure_md']),
                'lessons': render_markdown(data['lessons_md']),
                'links': data.get('links_json', []),
                'markets': data.get('markets_json', []),
                'stacks': data.get('stack_tags_json', []),
            }
            return self.render_to_response(ctx)

        # publish
        s = form.save(commit=False)
        s.user = self.request.user
        # attach parsed json fields
        s.links_json = form.cleaned_data.get('links_json', [])
        s.markets_json = form.cleaned_data.get('markets_json', [])
        s.stack_tags_json = form.cleaned_data.get('stack_tags_json', [])
        s.status = 'published'
        s.save()
        return redirect(s.get_absolute_url())


class LatestFeed(Feed):
    title = "miserableproject.club — Latest Submissions"
    link = "/rss.xml"
    description = "Latest 50 posts"

    def items(self):
        return Submission.objects.filter(status='published').order_by('-created_at')[:50]

    def item_title(self, item: Submission):
        return item.title

    def item_description(self, item: Submission):
        return item.snapshot

    def item_link(self, item: Submission):
        return reverse('submission_detail', args=[item.slug])
