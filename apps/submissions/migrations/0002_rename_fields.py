from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('submissions', '0001_initial'),
    ]
    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='title',
            new_name='project_name',
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='snapshot',
            new_name='purpose',
        ),
    ]

