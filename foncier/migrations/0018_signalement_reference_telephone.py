import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0017_signalement_commentaire_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='signalement',
            name='reference',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
                help_text="Identifiant secret donné au citoyen pour suivre son signalement, sans compte.",
                verbose_name="Code de suivi",
            ),
        ),
        migrations.AddField(
            model_name='signalement',
            name='telephone',
            field=models.CharField(
                blank=True,
                max_length=20,
                help_text="Si renseigné : un SMS est envoyé au citoyen quand le signalement est résolu.",
                verbose_name="Téléphone (optionnel)",
            ),
        ),
    ]
