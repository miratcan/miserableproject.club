from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('snapshot', models.CharField(max_length=320)),
                ('idea_md', models.TextField()),
                ('tech_md', models.TextField()),
                ('execution_md', models.TextField()),
                ('failure_md', models.TextField()),
                ('lessons_md', models.TextField()),
                ('links_json', models.JSONField(blank=True, default=list)),
                ('markets_json', models.JSONField(blank=True, default=list)),
                ('stack_tags_json', models.JSONField(blank=True, default=list)),
                ('timeline_text', models.CharField(blank=True, max_length=120)),
                ('revenue_text', models.CharField(blank=True, max_length=120)),
                ('spend_text', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(choices=[('published', 'Published'), ('flagged', 'Flagged'), ('removed', 'Removed')], db_index=True, default='published', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.CharField(choices=[('submission', 'Submission')], max_length=20)),
                ('target_id', models.PositiveBigIntegerField()),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], db_index=True, default='open', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

