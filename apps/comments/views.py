from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import UpdateView, View

from .models import Comment
from .forms import CommentForm


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/edit.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user, is_deleted=False)

    def form_valid(self, form):
        comment = form.save()
        return redirect(comment.submission.get_absolute_url())


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user, is_deleted=False)
        comment.is_deleted = True
        comment.save()
        return redirect(comment.submission.get_absolute_url())
