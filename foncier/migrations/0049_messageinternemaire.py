from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("foncier", "0048_types_imposition_fonciere"),
    ]

    operations = [
        migrations.CreateModel(
            name="MessageInterneMaire",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sujet", models.CharField(max_length=200)),
                ("contenu", models.TextField()),
                ("date_envoi", models.DateTimeField(auto_now_add=True)),
                ("lu", models.BooleanField(default=False)),
                (
                    "destinataire",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages_internes_recus",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "expediteur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages_internes_envoyes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reponses",
                        to="foncier.messageinternemaire",
                    ),
                ),
            ],
            options={
                "verbose_name": "Message maire-chef",
                "verbose_name_plural": "Messages maire-chefs",
                "ordering": ["-date_envoi"],
            },
        ),
    ]
