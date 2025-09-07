from django.conf import settings


def site_settings(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'miserableproject.club'),
        'DEFAULT_OG_IMAGE': getattr(settings, 'DEFAULT_OG_IMAGE', '/static/img/og-placeholder.png'),
    }
