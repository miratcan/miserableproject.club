from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0003_remove_submission_stack_tags_json_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="idea_md",
            new_name="idea",
        ),
        migrations.RenameField(
            model_name="submission",
            old_name="tech_md",
            new_name="tech",
        ),
        migrations.RenameField(
            model_name="submission",
            old_name="execution_md",
            new_name="execution",
        ),
        migrations.RenameField(
            model_name="submission",
            old_name="failure_md",
            new_name="failure",
        ),
        migrations.RenameField(
            model_name="submission",
            old_name="lessons_md",
            new_name="lessons",
        ),
    ]

