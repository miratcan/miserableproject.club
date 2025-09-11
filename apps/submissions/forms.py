from django import forms
from datetime import date
import json
from jsonschema import Draft7Validator
from taggit.forms import TagField
from .models import Submission, strip_h1_h2


class SubmissionForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'hidden'}))
    is_anonymous = forms.TypedChoiceField(
        label='Publish as Anonymous? (Optional)',
        choices=((False, 'No'), (True, 'Yes')),
        coerce=lambda v: v in (True, 'True', 'true', '1', 1, 'on'),
        widget=forms.Select,
        required=False,
        help_text="If selected, your username will be hidden on the public page.",
    )
    birth_year = forms.IntegerField(
        label='Birth year',
        required=True,
        widget=forms.NumberInput(attrs={'min': 1995, 'max': date.today().year}),
        help_text='Year you launched the project',
    )
    lifespan = forms.IntegerField(
        label='Lifespan (Months. Optional)',
        required=False,
        widget=forms.NumberInput(attrs={'min': 1}),
        help_text='How many months it ran before you shut it down.',
    )
    links = forms.CharField(
        label='Links (Optional)',
        required=False,
        help_text='One URL per line. Add relevant links (demo, landing page, repo).',
        widget=forms.Textarea(attrs={'rows': 2})
    )
    tags = TagField(
        label='Tags (Optional)',
        required=False,
        help_text='Comma-separated tags for this submission.',
    )

    class Meta:
        model = Submission
        fields = [
            'project_name', 'tagline', 'is_anonymous', 'birth_year', 'lifespan',
            'description', 'idea', 'tech', 'tags', 'wins', 'failure', 'lessons',
        ]
        labels = {
            'tagline': 'Tagline',
            'description': 'Project Description',
            'wins': 'What went right?',
            'idea': 'Where the idea came from?',
            'tech': 'What was the tech & stack?',
            'failure': 'Why did it fail? What went wrong?',
            'lessons': 'Key lessons & advice',
        }
        help_texts = {
            'project_name': 'Max 120 characters. Clear and descriptive.',
            'tagline': 'Single line, max 160 characters.',
            'description': 'Explain what the project is/was and who it was for.',
            'idea': 'Where the idea came from and the problem it solved. Markdown is supported except H1/H2 headers.',
            'tech': 'Describe the stack and key technical choices. Mention tradeoffs. Markdown is supported except H1/H2 headers.',
            'wins': 'What went well? design, code, launch tactics? Small wins matter.',
            'failure': 'What went wrong and why. Be specific and honest. Markdown is supported except H1/H2 headers.',
            'lessons': "Key lessons and actionable advice. Think about what you'd tell a friend. Markdown is supported except H1/H2 headers.",
        }
        widgets = {
            'tagline': forms.TextInput(attrs={'maxlength': 160}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'idea': forms.Textarea(attrs={'rows': 3}),
            'tech': forms.Textarea(attrs={'rows': 3}),
            'wins': forms.Textarea(attrs={'rows': 3}),
            'failure': forms.Textarea(attrs={'rows': 3}),
            'lessons': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_project_name(self):
        project_name = (self.cleaned_data.get('project_name') or '').strip()
        if len(project_name) > 120:
            raise forms.ValidationError('Project name must be at most 120 characters.')
        return project_name

    def clean_tagline(self):
        tagline = (self.cleaned_data.get('tagline') or '').strip()
        if '\n' in tagline or '\r' in tagline:
            raise forms.ValidationError('Short Description must be a single line (no line breaks).')
        if len(tagline) > 160:
            raise forms.ValidationError('Short Description must be at most 160 characters.')
        if not tagline:
            raise forms.ValidationError('Short Description is required.')
        return tagline

    def clean_birth_year(self):
        y = self.cleaned_data.get('birth_year')
        current = date.today().year
        if y is None:
            raise forms.ValidationError('This field is required.')
        if not (1995 <= int(y) <= current):
            raise forms.ValidationError(f'Year must be between 1995 and {current}.')
        return int(y)

    def clean_lifespan(self):
        y = self.cleaned_data.get('lifespan')
        if y in (None, "", ''):
            return None
        try:
            y = int(y)
        except (TypeError, ValueError):
            raise forms.ValidationError('Enter a valid integer (months).')
        if y < 1:
            raise forms.ValidationError('Must be at least 1 month.')
        return y

    def clean_description(self):
        return strip_h1_h2(self.cleaned_data.get('description', ''))

    def clean_idea(self):
        return strip_h1_h2(self.cleaned_data.get('idea', ''))

    def clean_tech(self):
        return strip_h1_h2(self.cleaned_data.get('tech', ''))

    def clean_wins(self):
        return strip_h1_h2(self.cleaned_data.get('wins', ''))

    def clean_failure(self):
        return strip_h1_h2(self.cleaned_data.get('failure', ''))

    def clean_lessons(self):
        return strip_h1_h2(self.cleaned_data.get('lessons', ''))

    def clean_tags(self):
        tags = self.cleaned_data.get('tags') or []
        return [t.strip() for t in tags if t.strip()]

    def clean(self):
        cleaned = super().clean()
        # honeypot
        if (self.cleaned_data.get('honeypot') or '').strip():
            raise forms.ValidationError('Invalid submission.')

        # parse links
        raw_links = (self.data.get('links') or '').strip()
        links = [l.strip() for l in raw_links.splitlines() if l.strip()]
        cleaned['links_json'] = links

        return cleaned


SUBMISSION_IMPORT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Submission",
    "type": "object",
    "required": [
        "project_name",
        "tagline",
        "birth_year",
        "idea",
        "tech",
        "failure",
        "lessons",
    ],
    "properties": {
        "project_name": {"type": "string", "maxLength": 120},
        "tagline": {
            "type": "string",
            "maxLength": 160,
            "pattern": "^[^\\n\\r]*$",
        },
        "description": {"type": "string"},
        "is_anonymous": {"type": "boolean", "default": False},
        "birth_year": {
            "type": "integer",
            "minimum": 1995,
            "maximum": date.today().year,
        },
        "lifespan": {"type": ["integer", "null"], "minimum": 1},
        "idea": {"type": "string"},
        "tech": {"type": "string"},
        "failure": {"type": "string"},
        "lessons": {"type": "string"},
        "wins": {"type": "string", "default": ""},
        "links_json": {
            "type": "array",
            "items": {"type": "string", "format": "uri"},
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1,
                "pattern": "^\\S(.*\\S)?$",
            },
            "uniqueItems": True,
        },
        "user": {"type": ["integer", "null"]},
    },
    "additionalProperties": False,
}


class SubmissionImportForm(forms.Form):
    json_data = forms.CharField(
        label="Submission JSON",
        widget=forms.Textarea(attrs={"rows": 10}),
        help_text="Paste a JSON object or array of objects.",
    )

    def clean_json_data(self):
        raw = self.cleaned_data.get("json_data", "")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f"Invalid JSON: {exc.msg}")

        if isinstance(parsed, dict):
            items = [parsed]
        elif isinstance(parsed, list):
            items = parsed
        else:
            raise forms.ValidationError("JSON must be an object or list of objects.")

        validator = Draft7Validator(SUBMISSION_IMPORT_SCHEMA)
        for idx, item in enumerate(items):
            errors = sorted(validator.iter_errors(item), key=lambda e: e.path)
            if errors:
                msgs = [f"{'/'.join(str(p) for p in err.path) or '(root)'}: {err.message}" for err in errors]
                raise forms.ValidationError(f"Item {idx}: {'; '.join(msgs)}")

        self.cleaned_data["items"] = items
        return raw
