from django.urls import path
from .views import SubmissionDetailView, SubmitView, LatestFeed, DeleteSubmissionView

urlpatterns = [
    path('p/<slug:slug>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('p/<slug:slug>/delete/', DeleteSubmissionView.as_view(), name='submission_delete'),
    path('submit/', SubmitView.as_view(), name='submit'),
    path('submit/<slug:slug>/', SubmitView.as_view(), name='submit_edit'),
    path('rss.xml', LatestFeed(), name='rss'),
]
