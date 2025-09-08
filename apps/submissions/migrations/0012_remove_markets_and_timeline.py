from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0011_rename_first_release_year_to_birth_year"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="markets_json",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="timeline_text",
        ),
    ]

