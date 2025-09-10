from django.test import TestCase
from django.contrib.auth import get_user_model
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
