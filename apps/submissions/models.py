from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import secrets
import string
from taggit.managers import TaggableManager
from datetime import date
from django.core.validators import MinValueValidator


STATUS_CHOICES = (
    ('draft', 'Draft'),
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


def current_year() -> int:
    return date.today().year


class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    project_name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    tagline = models.CharField(max_length=160)
    description = models.TextField(blank=True, default="")
    is_anonymous = models.BooleanField(default=False)
    birth_year = models.IntegerField(default=current_year, validators=[MinValueValidator(1995)])
    lifespan = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])

    idea = models.TextField()
    tech = models.TextField()
    failure = models.TextField()
    lessons = models.TextField()
    wins = models.TextField(blank=True, default="")

    links_json = models.JSONField(default=list, blank=True)
    stack_tags = TaggableManager(blank=True)
    # timeline_text removed for MVP
    # revenue_text removed for MVP
    # spend_text removed for MVP

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
        self.description = strip_h1_h2(self.description)
        self.idea = strip_h1_h2(self.idea)
        self.tech = strip_h1_h2(self.tech)
        self.failure = strip_h1_h2(self.failure)
        self.lessons = strip_h1_h2(self.lessons)

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


# Report model removed for MVP
