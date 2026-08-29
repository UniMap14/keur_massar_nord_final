from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0016_typetaxe_echeances'),
    ]

    operations = [
        migrations.AddField(
            model_name='signalement',
            name='commentaire_agent',
            field=models.TextField(
                blank=True,
                default='',
                help_text="Visible uniquement par l'administration, jamais par le public.",
                verbose_name='Note interne (agent)',
            ),
        ),
    ]