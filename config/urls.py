from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.conf import settings

from apps.submissions.sitemaps import SubmissionSitemap
from apps.core.views import SignupView

sitemaps = {
    "submissions": SubmissionSitemap,
}

urlpatterns = [
    path(settings.ADMIN_URL.lstrip("/"), admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", SignupView.as_view(), name="signup"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("dos.ttf", RedirectView.as_view(url="/static/fonts/dos.ttf", permanent=True)),
    path("", include("apps.core.urls")),
    path("", include("apps.submissions.urls")),
    path("comments/", include("apps.comments.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
