import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0030_taxation_simulation_fiscale_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilAgent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fonction', models.CharField(
                    blank=True, max_length=150, verbose_name="Fonction",
                    help_text="Ex : Maire, Chef du Service Cadastre, Chef du Service Fiscalité",
                )),
                ('telephone', models.CharField(blank=True, max_length=20, verbose_name="Téléphone")),
                ('photo', models.ImageField(
                    blank=True, null=True, upload_to='profils_agents/',
                    verbose_name="Photo de profil",
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profil_agent', to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': "Profil agent",
                'verbose_name_plural': "Profils agents",
            },
        ),
    ]