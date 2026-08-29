from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0023_signalement_agent_assigne'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalAudit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horodatage', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('action', models.CharField(choices=[('CREATION', 'Création'), ('MODIFICATION', 'Modification'), ('SUPPRESSION', 'Suppression')], max_length=15)),
                ('modele', models.CharField(db_index=True, max_length=50)),
                ('objet_id', models.CharField(max_length=30)),
                ('objet_repr', models.CharField(help_text="Description de l'objet au moment de l'action (reste lisible même si l'objet est ensuite supprimé).", max_length=255)),
                ('champs_modifies', models.JSONField(blank=True, help_text="Pour une modification : {'champ': ['ancienne valeur', 'nouvelle valeur']}.", null=True)),
                ('adresse_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('utilisateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions_audit', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Entrée du journal d'audit",
                'verbose_name_plural': "Journal d'audit",
                'ordering': ['-horodatage'],
            },
        ),
    ]
