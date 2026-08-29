from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0021_parcelle_id_shp'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxation',
            name='dernier_rappel_envoye',
            field=models.DateField(
                blank=True,
                null=True,
                help_text="Rempli automatiquement par la commande envoyer_rappels_echeances, pour ne jamais envoyer deux fois le même rappel.",
                verbose_name="Dernier rappel d'échéance envoyé",
            ),
        ),
    ]
