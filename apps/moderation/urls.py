from django.urls import path
from .views import ReportCreateView

urlpatterns = [
    path('report/', ReportCreateView.as_view(), name='report_create'),
]

