from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parents[3]))

from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.submissions.models import Submission


class SubmitViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="u1", password="pw"
        )
        self.client.force_login(self.user)

    def _post_data(self, **overrides):
        data = {
            "project_name": "Test Project",
            "tagline": "Short one line",
            "birth_year": date.today().year,
            "idea": "idea",
            "tech": "tech",
            "failure": "fail",
            "lessons": "lessons",
            "tags": "python, django",
        }
        data.update(overrides)
        return data

    def test_create_submission_saves_tags(self):
        resp = self.client.post(reverse("submit"), self._post_data())
        self.assertEqual(resp.status_code, 302)
        sub = Submission.objects.get(project_name="Test Project")
        self.assertCountEqual(sub.tags.names(), ["python", "django"])

    def test_edit_submission_updates_tags(self):
        sub = Submission.objects.create(
            user=self.user,
            project_name="Test Project",
            tagline="Short one line",
            birth_year=date.today().year,
            idea="idea",
            tech="tech",
            failure="fail",
            lessons="lessons",
        )
        sub.tags.add("python")
        url = reverse("submit_edit", args=[sub.slug])
        resp = self.client.post(
            url, self._post_data(tags="go, rust", project_name="Test Project")
        )
        self.assertEqual(resp.status_code, 302)
        sub.refresh_from_db()
        self.assertCountEqual(sub.tags.names(), ["go", "rust"])


class ImportViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="imp", password="pw"
        )
        self.client.force_login(self.user)

    def test_import_creates_submission(self):
        payload = {
            "project_name": "Imported",
            "tagline": "Short line",
            "birth_year": date.today().year,
            "idea": "idea",
            "tech": "tech",
            "failure": "fail",
            "lessons": "lessons",
        }
        resp = self.client.post(
            reverse("submission_import"),
            {"json_data": json.dumps(payload)},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Submission.objects.filter(project_name="Imported").exists())

    def test_invalid_json_shows_error(self):
        resp = self.client.post(
            reverse("submission_import"),
            {"json_data": "{"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid JSON")

