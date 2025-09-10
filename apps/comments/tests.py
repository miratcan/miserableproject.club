from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.submissions.models import Submission
from .models import Comment
from .forms import CommentForm


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )
        self.submission = Submission.objects.create(
            user=self.user,
            project_name="Test Project",
            tagline="A test project",
            idea="Test idea",
            tech="Test tech",
            failure="Test failure",
            lessons="Test lessons",
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            user=self.user,
            submission=self.submission,
            content="This is a test comment.",
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.submission, self.submission)
        self.assertEqual(comment.content, "This is a test comment.")
        self.assertIsNotNone(comment.created_at)
        self.assertIsNone(comment.parent)
        self.assertFalse(comment.is_deleted)

    def test_reply_creation(self):
        parent = Comment.objects.create(
            user=self.user,
            submission=self.submission,
            content="Parent comment.",
        )
        reply = Comment.objects.create(
            user=self.user,
            submission=self.submission,
            content="Child comment.",
            parent=parent,
        )
        self.assertEqual(reply.parent, parent)


class CommentFormTests(TestCase):
    def test_valid_form(self):
        form = CommentForm(data={"content": "This is a test comment."})
        self.assertTrue(form.is_valid())

    def test_empty_form(self):
        form = CommentForm(data={"content": ""})
        self.assertFalse(form.is_valid())

    def test_help_text_ascii(self):
        form = CommentForm()
        help_text = form.fields["content"].help_text or ""
        self.assertTrue(help_text.isascii())

    def test_textarea_rows(self):
        form = CommentForm()
        self.assertEqual(form.fields["content"].widget.attrs.get("rows"), 3)


class CommentViewMessageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="u1", password="pw"
        )
        self.client.force_login(self.user)
        self.submission = Submission.objects.create(
            user=self.user,
            project_name="Test Project",
            tagline="A test project",
            idea="Test idea",
            tech="Test tech",
            failure="Test failure",
            lessons="Test lessons",
        )

    def test_create_comment_shows_message(self):
        url = reverse("comment_form") + f"?submission={self.submission.pk}"
        resp = self.client.post(
            url, {"content": "Hello", "parent": ""}, follow=True
        )
        messages = [str(m) for m in resp.context["messages"]]
        self.assertIn("Comment added successfully.", messages)

    def test_update_comment_shows_message(self):
        c = Comment.objects.create(
            user=self.user,
            submission=self.submission,
            content="Old",
        )
        url = reverse("comment_form") + f"?comment={c.pk}"
        resp = self.client.post(
            url, {"content": "New", "parent": ""}, follow=True
        )
        messages = [str(m) for m in resp.context["messages"]]
        self.assertIn("Comment updated successfully.", messages)

    def test_delete_comment_shows_message(self):
        c = Comment.objects.create(
            user=self.user,
            submission=self.submission,
            content="To delete",
        )
        url = reverse("comment_delete", args=[c.pk])
        resp = self.client.post(url, follow=True)
        messages = [str(m) for m in resp.context["messages"]]
        self.assertIn("Comment deleted successfully.", messages)
