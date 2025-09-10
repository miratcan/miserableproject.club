from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.submissions.models import Submission
from .forms import CommentForm
from .models import Comment


class CommentView(LoginRequiredMixin, View):
    form_class = CommentForm
    template_name = "comments/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.submission = None
        self.parent = None
        self.comment = None
        submission_id = request.GET.get("submission")
        parent_id = request.GET.get("parent")
        comment_id = request.GET.get("comment")
        if comment_id:
            self.comment = get_object_or_404(
                Comment, pk=comment_id, user=request.user, is_deleted=False
            )
            self.submission = self.comment.submission
        elif parent_id:
            self.parent = get_object_or_404(Comment, pk=parent_id, is_deleted=False)
            self.submission = self.parent.submission
        elif submission_id:
            self.submission = get_object_or_404(Submission, pk=submission_id)
        else:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.comment)
        if self.parent and not self.comment:
            form.initial["parent"] = self.parent.pk
        context = {
            "form": form,
            "submission": self.submission,
            "parent": self.parent,
            "comment": self.comment,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.submission = self.submission
            if not self.comment:
                parent = form.cleaned_data.get("parent")
                if parent and parent.submission_id != self.submission.id:
                    comment.parent = None
            comment.save()
            return redirect(comment.submission.get_absolute_url())
        context = {
            "form": form,
            "submission": self.submission,
            "parent": self.parent,
            "comment": self.comment,
        }
        return render(request, self.template_name, context)


class CommentDeleteView(LoginRequiredMixin, View):
    def _delete(self, request, pk):
        comment = get_object_or_404(
            Comment, pk=pk, user=request.user, is_deleted=False
        )
        comment.is_deleted = True
        comment.save()
        return redirect(comment.submission.get_absolute_url())

    def post(self, request, pk):
        return self._delete(request, pk)

    def get(self, request, pk):
        return self._delete(request, pk)
