from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submissions", "0017_alter_submission_birth_year_alter_submission_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
    ]

