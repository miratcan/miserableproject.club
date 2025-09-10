from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from django.test import TestCase

from apps.submissions.forms import SubmissionForm
from datetime import date


class SubmissionFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "project_name": "Test Project",
            "tagline": "Short one line",
            "birth_year": date.today().year,
            "idea": "idea",
            "tech": "tech",
            "failure": "fail",
            "lessons": "lessons",
        }
        data.update(overrides)
        return data

    def test_tagline_length_and_single_line_validation(self):
        data = self._valid_data(tagline="a" * 161)
        form = SubmissionForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("tagline", form.errors)

        data = self._valid_data(tagline="line1\nline2")
        form = SubmissionForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("tagline", form.errors)

    def test_links_parsed_into_json(self):
        links_text = "http://example.com\n\nhttps://foo.com"
        data = self._valid_data(links=links_text)
        form = SubmissionForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["links_json"], [
            "http://example.com",
            "https://foo.com",
        ])

    def test_tags_parsed(self):
        data = self._valid_data(tags="python, django, ")
        form = SubmissionForm(data)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.cleaned_data["tags"], ["python", "django"])
