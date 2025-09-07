from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from django.test import TestCase

from apps.submissions.forms import SubmissionForm


class SubmissionFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "title": "Test Title",
            "snapshot": "s" * 280,
            "idea_md": "idea",
            "tech_md": "tech",
            "execution_md": "exec",
            "failure_md": "fail",
            "lessons_md": "lessons",
        }
        data.update(overrides)
        return data

    def test_snapshot_length_validation(self):
        data = self._valid_data(snapshot="a" * 279)
        form = SubmissionForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("snapshot", form.errors)

    def test_links_parsed_into_json(self):
        links_text = "http://example.com\n\nhttps://foo.com"
        data = self._valid_data(links=links_text)
        form = SubmissionForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["links_json"], [
            "http://example.com",
            "https://foo.com",
        ])
