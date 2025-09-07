from django import forms
from taggit.forms import TagField
from .models import Submission, strip_h1_h2


class SubmissionForm(forms.ModelForm):
    links = forms.CharField(
        required=False,
        help_text='Optional. One URL per line. External links related to the project (demo, landing, repo).',
        widget=forms.Textarea(attrs={'rows': 3})
    )
    markets = forms.CharField(
        required=False,
        help_text='Optional. Comma‑separated markets/geo or audience (e.g., B2B, US, EU).',
    )
    stack_tags = TagField(
        required=False,
        help_text='Optional. Comma‑separated tech or stack tags (e.g., Django, Next.js, Stripe).',
    )

    class Meta:
        model = Submission
        fields = [
            'project_name', 'purpose',
            'idea_md', 'tech_md', 'execution_md', 'failure_md', 'lessons_md',
            'timeline_text', 'revenue_text', 'spend_text', 'stack_tags',
        ]
        help_texts = {
            'project_name': 'Max 120 characters. Clear and descriptive.',
            'purpose': '280–320 characters. A concise summary of the story.',
            'idea_md': 'No H1/H2. Share where the idea came from and why.',
            'tech_md': 'No H1/H2. Stack and key technical choices.',
            'execution_md': 'No H1/H2. How you built, launched, and iterated.',
            'failure_md': 'No H1/H2. What went wrong. Be specific and honest.',
            'lessons_md': 'No H1/H2. Key lessons and actionable advice.',
            'timeline_text': 'Optional. Duration, e.g., 3 months.',
            'revenue_text': 'Optional. Approx revenue, e.g., $10k.',
            'spend_text': 'Optional. Approx spend, e.g., $200.',
        }
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3, 'maxlength': 320}),
            'idea_md': forms.Textarea(attrs={'rows': 8}),
            'tech_md': forms.Textarea(attrs={'rows': 6}),
            'execution_md': forms.Textarea(attrs={'rows': 8}),
            'failure_md': forms.Textarea(attrs={'rows': 8}),
            'lessons_md': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_project_name(self):
        project_name = (self.cleaned_data.get('project_name') or '').strip()
        if len(project_name) > 120:
            raise forms.ValidationError('Project name must be at most 120 characters.')
        return project_name

    def clean_purpose(self):
        purpose = (self.cleaned_data.get('purpose') or '').strip()
        if not (280 <= len(purpose) <= 320):
            raise forms.ValidationError('Purpose must be between 280 and 320 characters.')
        return purpose

    def _strip_h1_h2_for(self, field):
        self.cleaned_data[field] = strip_h1_h2(self.cleaned_data.get(field) or '')

    def clean(self):
        cleaned = super().clean()
        for f in ['idea_md', 'tech_md', 'execution_md', 'failure_md', 'lessons_md']:
            self._strip_h1_h2_for(f)

        # parse links/markets
        raw_links = (self.data.get('links') or '').strip()
        links = [l.strip() for l in raw_links.splitlines() if l.strip()]
        cleaned['links_json'] = links

        markets = [s.strip() for s in (self.data.get('markets') or '').split(',') if s.strip()]
        cleaned['markets_json'] = markets

        return cleaned
