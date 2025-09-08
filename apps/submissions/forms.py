from django import forms
from datetime import date
from taggit.forms import TagField
from .models import Submission, strip_h1_h2


class SubmissionForm(forms.ModelForm):
    is_anonymous = forms.TypedChoiceField(
        label='Publish as Anonymous? (Optional)',
        choices=((False, 'No'), (True, 'Yes')),
        coerce=lambda v: v in (True, 'True', 'true', '1', 1, 'on'),
        widget=forms.RadioSelect,
        required=False,
        help_text="If selected, your username will be hidden on the public page.",
    )
    birth_year = forms.IntegerField(
        label='Birth year',
        required=True,
        widget=forms.NumberInput(attrs={'min': 1995, 'max': date.today().year}),
        help_text='Year you launched the project (1995–current).',
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

    class Meta:
        model = Submission
        fields = [
            'project_name', 'tagline', 'is_anonymous', 'birth_year', 'lifespan',
            'idea', 'tech', 'wins', 'failure', 'lessons',
        ]
        labels = {
            'tagline': 'Tagline',
            'wins': 'What went right?',
            'idea': 'Where the idea came from?',
            'tech': 'What was the tech & stack?',
            'failure': 'Why did it fail? What went wrong?',
            'lessons': 'Key lessons & advice',
        }
        help_texts = {
            'project_name': 'Max 120 characters. Clear and descriptive.',
            'tagline': 'Single line, max 160 characters.',
            'idea': 'Where the idea came from and the problem it solved. Markdown is supported except H1/H2 headers.',
            'tech': 'Describe the stack and key technical choices. Mention tradeoffs. Markdown is supported except H1/H2 headers.',
            'execution': 'How you built, launched, and iterated. Focus on actions and timelines. Markdown is supported except H1/H2 headers.',
            'wins': 'What went well — design, code, launch tactics. Small wins matter.',
            'failure': 'What went wrong and why. Be specific and honest. Markdown is supported except H1/H2 headers.',
            'lessons': 'Key lessons and actionable advice. Think about what you’d tell a friend. Markdown is supported except H1/H2 headers.',
        }
        widgets = {
            'tagline': forms.TextInput(attrs={'maxlength': 160}),
            'idea': forms.Textarea(attrs={'rows': 6}),
            'tech': forms.Textarea(attrs={'rows': 4}),
            'wins': forms.Textarea(attrs={'rows': 4}),
            'failure': forms.Textarea(attrs={'rows': 6}),
            'lessons': forms.Textarea(attrs={'rows': 4}),
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

    def _strip_h1_h2_for(self, field):
        self.cleaned_data[field] = strip_h1_h2(self.cleaned_data.get(field) or '')

    def clean(self):
        cleaned = super().clean()
        for f in ['idea', 'tech', 'wins', 'failure', 'lessons']:
            self._strip_h1_h2_for(f)

        # parse links
        raw_links = (self.data.get('links') or '').strip()
        links = [l.strip() for l in raw_links.splitlines() if l.strip()]
        cleaned['links_json'] = links

        return cleaned
