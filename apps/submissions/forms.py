from django import forms
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
    stack_tags = forms.CharField(
        required=False,
        help_text='Optional. Comma‑separated tech or stack tags (e.g., Django, Next.js, Stripe).',
    )

    class Meta:
        model = Submission
        fields = [
            'title', 'snapshot',
            'idea_md', 'tech_md', 'execution_md', 'failure_md', 'lessons_md',
            'timeline_text', 'revenue_text', 'spend_text',
        ]
        help_texts = {
            'title': 'Max 120 characters. Clear and descriptive.',
            'snapshot': '280–320 characters. A concise summary of the story.',
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
            'snapshot': forms.Textarea(attrs={'rows': 3, 'maxlength': 320}),
            'idea_md': forms.Textarea(attrs={'rows': 8}),
            'tech_md': forms.Textarea(attrs={'rows': 6}),
            'execution_md': forms.Textarea(attrs={'rows': 8}),
            'failure_md': forms.Textarea(attrs={'rows': 8}),
            'lessons_md': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_title(self):
        title = (self.cleaned_data.get('title') or '').strip()
        if len(title) > 120:
            raise forms.ValidationError('Title must be at most 120 characters.')
        return title

    def clean_snapshot(self):
        snapshot = (self.cleaned_data.get('snapshot') or '').strip()
        if not (280 <= len(snapshot) <= 320):
            raise forms.ValidationError('Snapshot must be between 280 and 320 characters.')
        return snapshot

    def _strip_h1_h2_for(self, field):
        self.cleaned_data[field] = strip_h1_h2(self.cleaned_data.get(field) or '')

    def clean(self):
        cleaned = super().clean()
        for f in ['idea_md', 'tech_md', 'execution_md', 'failure_md', 'lessons_md']:
            self._strip_h1_h2_for(f)

        # parse links/markets/stack_tags
        raw_links = (self.data.get('links') or '').strip()
        links = [l.strip() for l in raw_links.splitlines() if l.strip()]
        cleaned['links_json'] = links

        markets = [s.strip() for s in (self.data.get('markets') or '').split(',') if s.strip()]
        cleaned['markets_json'] = markets

        stacks = [s.strip() for s in (self.data.get('stack_tags') or '').split(',') if s.strip()]
        cleaned['stack_tags_json'] = stacks

        return cleaned
