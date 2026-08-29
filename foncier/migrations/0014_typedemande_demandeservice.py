import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foncier', '0013_actualite'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeDemande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=150)),
                ('categorie', models.CharField(choices=[('CADASTRE', 'Cadastre / Foncier'), ('ETAT_CIVIL', 'État civil'), ('URBANISME', 'Urbanisme / Construction'), ('FISCALITE', 'Fiscalité'), ('AUTRE', 'Autre')], default='CADASTRE', max_length=20)),
                ('description', models.TextField(blank=True, help_text='Ce que couvre cette démarche.')),
                ('pieces_requises', models.TextField(blank=True, help_text='Liste des pièces à fournir (une par ligne).')),
                ('delai_indicatif_jours', models.PositiveIntegerField(default=5)),
                ('necessite_parcelle', models.BooleanField(default=False, help_text="Cocher si cette démarche concerne une parcelle précise (ex : extrait cadastral).")),
                ('actif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Type de démarche',
                'verbose_name_plural': 'Types de démarche',
                'ordering': ['categorie', 'libelle'],
            },
        ),
        migrations.CreateModel(
            name='DemandeService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_dossier', models.CharField(blank=True, max_length=30, unique=True)),
                ('objet', models.TextField(blank=True, verbose_name='Précisions sur la demande')),
                ('piece_jointe', models.FileField(blank=True, null=True, upload_to='demandes/')),
                ('statut', models.CharField(choices=[('RECUE', 'Reçue'), ('EN_COURS', 'En cours de traitement'), ('PRETE', 'Prête à retirer'), ('REJETEE', 'Rejetée'), ('CLOTUREE', 'Clôturée')], default='RECUE', max_length=15)),
                ('commentaire_agent', models.TextField(blank=True)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_maj', models.DateTimeField(auto_now=True)),
                ('agent_traitant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demandes_traitees', to=settings.AUTH_USER_MODEL)),
                ('demandeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes_service', to=settings.AUTH_USER_MODEL)),
                ('parcelle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demandes_service', to='foncier.parcelle')),
                ('type_demande', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='demandes', to='foncier.typedemande')),
            ],
            options={
                'verbose_name': 'Demande de service',
                'verbose_name_plural': 'Demandes de service',
                'ordering': ['-date_demande'],
            },
        ),
    ]