from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0015_demandeservice_piece_jointe_stockage_prive'),
    ]

    operations = [
        migrations.AddField(
            model_name='typetaxe',
            name='mois_echeance',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                choices=[
                    (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
                    (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
                    (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
                ],
                verbose_name="Mois de l'échéance annuelle",
                help_text="Mois de la date limite de paiement (se répète chaque année).",
            ),
        ),
        migrations.AddField(
            model_name='typetaxe',
            name='jour_echeance',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                verbose_name="Jour de l'échéance",
                help_text="Jour du mois (1 à 31).",
            ),
        ),
        migrations.AddField(
            model_name='typetaxe',
            name='penalite_retard',
            field=models.CharField(
                blank=True, max_length=150,
                verbose_name="Pénalité de retard",
                help_text="Ex : « Majoration de 10% après la date limite ».",
            ),
        ),
    ]