from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0026_parcelle_section_cadastrale'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcelle',
            name='numero_parcelle',
            field=models.CharField(blank=True, max_length=50, verbose_name="Numéro de parcelle"),
        ),
        migrations.AddField(
            model_name='parcelle',
            name='numero_lot',
            field=models.CharField(blank=True, max_length=50, verbose_name="Numéro de lot"),
        ),
        migrations.AddField(
            model_name='parcelle',
            name='numero_titre_foncier',
            field=models.CharField(blank=True, max_length=100, verbose_name="Numéro du titre foncier"),
        ),
    ]