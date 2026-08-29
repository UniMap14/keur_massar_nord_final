import foncier.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0014_typedemande_demandeservice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demandeservice',
            name='piece_jointe',
            field=models.FileField(
                blank=True,
                null=True,
                storage=foncier.models.stockage_pieces_jointes,
                upload_to='',
            ),
        ),
    ]