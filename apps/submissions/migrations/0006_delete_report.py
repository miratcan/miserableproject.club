from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0005_rename_purpose_to_tagline"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Report",
        ),
    ]

