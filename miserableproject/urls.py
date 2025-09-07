from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import RedirectView

from apps.submissions.sitemaps import SubmissionSitemap

sitemaps = {
    'submissions': SubmissionSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('dos.ttf', RedirectView.as_view(url='/static/fonts/dos.ttf', permanent=True)),
    path('', include('apps.core.urls')),
    path('', include('apps.submissions.urls')),
    path('', include('apps.moderation.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

