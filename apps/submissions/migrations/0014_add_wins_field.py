from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0013_rename_death_year_to_lifespan"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="wins",
            field=models.TextField(blank=True, default=""),
        ),
    ]

