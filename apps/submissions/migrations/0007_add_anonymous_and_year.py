from django.db import migrations, models
import datetime


def current_year():
    return datetime.date.today().year


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0006_delete_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="is_anonymous",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="submission",
            name="year_started",
            field=models.IntegerField(default=current_year),
        ),
    ]

