from django.urls import path
from .views import SubmissionDetailView, SubmitView, LatestFeed

urlpatterns = [
    path('p/<slug:slug>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('submit/', SubmitView.as_view(), name='submit'),
    path('rss.xml', LatestFeed(), name='rss'),
]

