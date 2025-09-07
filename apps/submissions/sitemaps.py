from django.contrib.sitemaps import Sitemap
from .models import Submission


class SubmissionSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Submission.objects.filter(status='published').order_by('-created_at')[:50]

    def lastmod(self, obj: Submission):
        return obj.updated_at

