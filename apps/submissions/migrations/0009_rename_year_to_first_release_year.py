from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0008_rename_year_started_to_year"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="year",
            new_name="first_release_year",
        ),
    ]

