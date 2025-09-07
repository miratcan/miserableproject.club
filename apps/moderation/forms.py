from django import forms
from apps.submissions.models import Report


class ReportForm(forms.Form):
    target_type = forms.ChoiceField(choices=Report.TARGET_CHOICES)
    target_id = forms.IntegerField(min_value=1)
    reason = forms.CharField()
