from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0012_remove_markets_and_timeline"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="death_year",
            new_name="lifespan",
        ),
        migrations.AlterField(
            model_name="submission",
            name="lifespan",
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]

