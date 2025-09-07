from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import secrets
import string


STATUS_CHOICES = (
    ('published', 'Published'),
    ('flagged', 'Flagged'),
    ('removed', 'Removed'),
)


def _short_id(length: int = 6) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def strip_h1_h2(md: str) -> str:
    if not md:
        return md
    lines = []
    for line in md.splitlines():
        if line.startswith('# '):
            continue
        if line.startswith('## '):
            continue
        lines.append(line)
    return '\n'.join(lines)


class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    project_name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    purpose = models.CharField(max_length=320)

    idea_md = models.TextField()
    tech_md = models.TextField()
    execution_md = models.TextField()
    failure_md = models.TextField()
    lessons_md = models.TextField()

    links_json = models.JSONField(default=list, blank=True)
    markets_json = models.JSONField(default=list, blank=True)
    stack_tags_json = models.JSONField(default=list, blank=True)
    timeline_text = models.CharField(max_length=120, blank=True)
    revenue_text = models.CharField(max_length=120, blank=True)
    spend_text = models.CharField(max_length=120, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.project_name

    def get_absolute_url(self):
        return reverse('submission_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        # enforce strip of H1/H2
        self.idea_md = strip_h1_h2(self.idea_md)
        self.tech_md = strip_h1_h2(self.tech_md)
        self.execution_md = strip_h1_h2(self.execution_md)
        self.failure_md = strip_h1_h2(self.failure_md)
        self.lessons_md = strip_h1_h2(self.lessons_md)

        if not self.slug:
            base = slugify(self.project_name)[:64] or 'post'
            sid = _short_id()
            candidate = f"{base}-{sid}"
            # ensure uniqueness with a couple tries
            for _ in range(5):
                if not Submission.objects.filter(slug=candidate).exists():
                    break
                sid = _short_id()
                candidate = f"{base}-{sid}"
            self.slug = candidate
        super().save(*args, **kwargs)


class Report(models.Model):
    TARGET_CHOICES = (
        ('submission', 'Submission'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id = models.PositiveBigIntegerField()
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.pk} {self.target_type}:{self.target_id}"

