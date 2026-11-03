from django.db import migrations, models


TYPES_IMPOSITION = [
    ("CFPB", "Contribution foncière des propriétés bâties (CFPB)"),
    ("CFPNB", "Contribution foncière des propriétés non bâties (CFPNB)"),
    ("IRF", "Impôt sur le revenu foncier (IRF)"),
    ("TEOM", "Taxe d'enlèvement des ordures ménagères (TEOM)"),
]


def creer_types_imposition(apps, schema_editor):
    TypeTaxe = apps.get_model("foncier", "TypeTaxe")
    for code, libelle in TYPES_IMPOSITION:
        TypeTaxe.objects.using(schema_editor.connection.alias).get_or_create(
            code=code,
            defaults={"libelle": libelle},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("foncier", "0047_alter_actualite_date_publication"),
    ]

    operations = [
        migrations.AlterField(
            model_name="typetaxe",
            name="code",
            field=models.CharField(
                choices=TYPES_IMPOSITION,
                max_length=20,
                unique=True,
            ),
        ),
        migrations.RunPython(creer_types_imposition, migrations.RunPython.noop),
    ]
