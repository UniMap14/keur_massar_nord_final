from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foncier', '0022_taxation_dernier_rappel_envoye'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='signalement',
            name='agent_assigne',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='signalements_assignes',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Agent assigné',
            ),
        ),
    ]
