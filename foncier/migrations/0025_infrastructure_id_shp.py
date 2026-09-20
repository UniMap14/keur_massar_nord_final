from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0024_journalaudit'),
    ]

    operations = [
        migrations.AddField(
            model_name='infrastructure',
            name='id_shp',
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                help_text="Identifiant du point source, pour éviter les doublons lors d'un ré-import.",
                verbose_name="ID unique (import shapefile)",
            ),
        ),
    ]