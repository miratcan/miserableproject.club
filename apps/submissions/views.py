from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import DetailView, FormView, View
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.contrib import messages

from .models import Submission
from .forms import SubmissionForm
from .markdown import render_markdown
from django.core.cache import cache
from apps.comments.forms import CommentForm
from apps.comments.models import Comment


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
        # Cache rendered markdown per-field, invalidated on update
        def _md(field_name: str, text: str) -> str:
            key = f"md:{field_name}:{s.pk}:{int(s.updated_at.timestamp())}"
            html = cache.get(key)
            if html is None:
                html = render_markdown(text)
                cache.set(key, html, 12 * 60 * 60)  # 12 hours
            return html

        ctx['html'] = {
            'description': _md('description', s.description),
            'idea': _md('idea', s.idea),
            'tech': _md('tech', s.tech),
            'wins': _md('wins', s.wins),
            'failure': _md('failure', s.failure),
            'lessons': _md('lessons', s.lessons),
        }
        
        can_comment = False
        if self.request.user.is_authenticated:
            if not hasattr(self, '_can_comment'):
                self._can_comment = Submission.objects.filter(user=self.request.user).exists()
            can_comment = self._can_comment

        ctx['can_comment'] = can_comment
        ctx['comment_form'] = CommentForm()
        ctx['comments'] = s.comments.all()
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not hasattr(self, '_can_comment'):
                self._can_comment = Submission.objects.filter(user=request.user).exists()

            if not self._can_comment:
                messages.error(request, "You need to have at least one submission to comment.")
                return redirect(self.object.get_absolute_url())

            comment = form.save(commit=False)
            comment.user = request.user
            comment.submission = self.object
            comment.save()
            messages.success(request, "Your comment has been added.")
            return redirect(self.object.get_absolute_url())
        
        context = self.get_context_data()
        context['comment_form'] = form
        return self.render_to_response(context)


class SubmitView(LoginRequiredMixin, FormView):
    template_name = 'submissions/submit.html'
    form_class = SubmissionForm

    def dispatch(self, request, *args, **kwargs):
        self.instance = None
        slug = kwargs.get('slug')
        if slug:
            try:
                self.instance = Submission.objects.get(slug=slug, user=request.user)
            except Submission.DoesNotExist:
                return redirect('submit')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.instance:
            kwargs['instance'] = self.instance
        return kwargs

    def form_valid(self, form):
        editing = bool(self.instance and getattr(self.instance, 'pk', None))
        s = form.save(commit=False)
        s.user = self.request.user
        # attach parsed json fields
        s.links_json = form.cleaned_data.get('links_json', [])
        s.status = 'published'
        s.save()
        form.save_m2m()
        if editing:
            messages.success(self.request, 'Submission updated successfully.')
        else:
            messages.success(self.request, 'Submission published successfully.')
        return redirect(s.get_absolute_url())


class LatestFeed(Feed):
    title = "miserableprojects.directory - Latest Submissions"
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


 


class DeleteSubmissionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            s = Submission.objects.get(slug=slug, user=request.user)
        except Submission.DoesNotExist:
            return redirect('submission_detail', slug=slug)
        s.delete()
        messages.success(request, 'Submission deleted successfully.')
        return redirect('home')
