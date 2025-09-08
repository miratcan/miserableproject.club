from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0010_add_death_year"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="first_release_year",
            new_name="birth_year",
        ),
    ]

