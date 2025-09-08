from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0007_add_anonymous_and_year"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="year_started",
            new_name="year",
        ),
    ]

