from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import FormView

from apps.submissions.models import Report
from .forms import ReportForm


class ReportCreateView(LoginRequiredMixin, FormView):
    template_name = 'moderation/report_form.html'
    form_class = ReportForm

    def form_valid(self, form):
        Report.objects.create(
            target_type=form.cleaned_data['target_type'],
            target_id=form.cleaned_data['target_id'],
            reporter=self.request.user,
            reason=form.cleaned_data['reason'],
        )
        return render(self.request, 'moderation/report_success.html')

