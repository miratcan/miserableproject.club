from pathlib import Path
import sys
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[3]))

from django.test import TestCase

from apps.submissions.models import Submission, strip_h1_h2


class StripH1H2Tests(TestCase):
    def test_removes_h1_and_h2_lines(self):
        md = "# Title\nFirst line\n## Subtitle\nSecond line"
        result = strip_h1_h2(md)
        self.assertEqual(result, "First line\nSecond line")


class SubmissionSlugTests(TestCase):
    def _create_submission(self, title="My Title"):
        return Submission.objects.create(
            title=title,
            snapshot="s" * 280,
            idea_md="idea",
            tech_md="tech",
            execution_md="exec",
            failure_md="fail",
            lessons_md="lessons",
        )

    @patch("apps.submissions.models._short_id", return_value="abc123")
    def test_generates_slug_from_title_and_short_id(self, mock_short_id):
        sub = self._create_submission()
        self.assertTrue(sub.slug.startswith("my-title-"))
        self.assertEqual(sub.slug, "my-title-abc123")

    @patch("apps.submissions.models._short_id", side_effect=["abc123", "abc123", "def456"])
    def test_slug_uniqueness_with_duplicate_titles(self, mock_short_id):
        first = self._create_submission(title="Same Title")
        second = self._create_submission(title="Same Title")
        self.assertEqual(first.slug, "same-title-abc123")
        self.assertEqual(second.slug, "same-title-def456")
        self.assertNotEqual(first.slug, second.slug)
