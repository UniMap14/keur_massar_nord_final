from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0018_signalement_reference_telephone'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiement',
            name='statut_paiement',
            field=models.CharField(
                choices=[
                    ('CONFIRME', 'Confirmé'),
                    ('EN_ATTENTE', 'En attente de confirmation'),
                    ('ECHEC', 'Échoué'),
                ],
                default='CONFIRME',
                max_length=15,
                help_text="Un paiement au guichet est confirmé immédiatement. Un paiement en "
                          "ligne (Orange Money/Wave) reste 'En attente' jusqu'à la confirmation "
                          "de l'opérateur.",
            ),
        ),
        migrations.AddField(
            model_name='paiement',
            name='reference_transaction',
            field=models.CharField(
                blank=True,
                default='',
                max_length=100,
                help_text="Identifiant de transaction donné par l'opérateur de paiement en ligne (le cas échéant).",
            ),
        ),
    ]
