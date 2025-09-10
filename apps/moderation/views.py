from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import FormView

from .forms import ReportForm


class ReportCreateView(LoginRequiredMixin, FormView):
    template_name = 'moderation/report_form.html'
    form_class = ReportForm

    def form_valid(self, form):
        # This is a placeholder, as the Report model has been removed.
        # In a real application, you would handle the report submission here.
        return render(self.request, 'moderation/report_success.html')

