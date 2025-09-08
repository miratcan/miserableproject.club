from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0015_remove_revenue_and_spend"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="execution",
        ),
    ]

