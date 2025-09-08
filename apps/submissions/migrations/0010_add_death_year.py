from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0009_rename_year_to_first_release_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="death_year",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

