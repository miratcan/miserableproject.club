from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0004_rename_md_fields"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="purpose",
            new_name="tagline",
        ),
        migrations.AlterField(
            model_name="submission",
            name="tagline",
            field=models.CharField(max_length=160),
        ),
    ]

