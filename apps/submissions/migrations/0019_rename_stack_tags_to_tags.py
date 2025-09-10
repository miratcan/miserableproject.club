from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0018_add_description"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="stack_tags",
            new_name="tags",
        ),
    ]
