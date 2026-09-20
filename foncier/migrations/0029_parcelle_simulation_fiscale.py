from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0028_merge_20260911_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcelle',
            name='simulation_fiscale',
            field=models.BooleanField(
                default=False,
                verbose_name="Montant fiscal simulé",
                help_text=(
                    "Coché si le montant de taxe/valeur locative provient d'une simulation "
                    "académique (superficie x valeur au m² estimée), et non d'une déclaration "
                    "ou d'un calcul réel. Ne jamais présenter comme une donnée officielle."
                ),
            ),
        ),
    ]