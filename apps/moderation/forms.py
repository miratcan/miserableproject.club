from django import forms


class ReportForm(forms.Form):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    target_id = forms.IntegerField(min_value=1)
    reason = forms.CharField()

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get('honeypot') or '').strip():
            raise forms.ValidationError('Invalid submission.')
        return cleaned
