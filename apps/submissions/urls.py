from django.urls import path
from .views import SubmissionDetailView, SubmitView, LatestFeed, DraftPreviewView, PublishDraftView

urlpatterns = [
    path('p/<slug:slug>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('p/<slug:slug>/preview/', DraftPreviewView.as_view(), name='submission_preview'),
    path('p/<slug:slug>/publish/', PublishDraftView.as_view(), name='submission_publish'),
    path('submit/', SubmitView.as_view(), name='submit'),
    path('submit/<slug:slug>/', SubmitView.as_view(), name='submit_edit'),
    path('rss.xml', LatestFeed(), name='rss'),
]
