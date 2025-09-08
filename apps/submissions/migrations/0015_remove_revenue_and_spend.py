from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0014_add_wins_field"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="revenue_text",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="spend_text",
        ),
    ]

