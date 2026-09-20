from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0024_journalaudit'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcelle',
            name='section_cadastrale',
            field=models.CharField(
                blank=True,
                max_length=10,
                verbose_name="Section cadastrale",
            ),
        ),
    ]