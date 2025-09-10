from django.conf import settings
from django.db import models

from apps.submissions.models import Submission
from apps.submissions.markdown import render_markdown


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.submission.project_name}"

    @property
    def content_html(self) -> str:
        """Return sanitized HTML version of the comment content."""
        return render_markdown(self.content)
