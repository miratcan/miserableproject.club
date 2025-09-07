from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from apps.submissions.models import Report


class ReportCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'moderation/report_success.html'

    def post(self, request, *args, **kwargs):
        target_type = request.POST.get('target_type')
        target_id = request.POST.get('target_id')
        reason = (request.POST.get('reason') or '').strip()
        if not (target_type and target_id and reason):
            messages.error(request, 'Eksik bilgi: target ve reason gerekli.')
            return redirect('home')
        try:
            tid = int(target_id)
        except ValueError:
            messages.error(request, 'Geçersiz hedef.')
            return redirect('home')
        Report.objects.create(target_type=target_type, target_id=tid, reporter=request.user, reason=reason)
        return self.get(request, *args, **kwargs)

