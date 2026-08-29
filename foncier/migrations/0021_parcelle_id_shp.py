from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0020_creer_groupes_agents'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcelle',
            name='id_shp',
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                help_text="Identifiant du polygone source (ex: KMN-000001), pour éviter les doublons lors d'un ré-import.",
                verbose_name="ID unique (import shapefile)",
            ),
        ),
    ]
