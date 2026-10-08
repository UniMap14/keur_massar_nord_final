import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from foncier.models import CategorieInfrastructure

ordre_max = CategorieInfrastructure.objects.order_by("-ordre").first()
nouvel_ordre = (ordre_max.ordre + 1) if ordre_max else 0

obj, cree = CategorieInfrastructure.objects.get_or_create(
    code="hotellerie",
    defaults={
        "label": "Hôtellerie",
        "description": "",
        "texte_intro": "",
        "icone": "fa-hotel",
        "couleur": "#7b3fa0",
        "ordre": nouvel_ordre,
    },
)

if cree:
    print(f"OK : categorie 'hotellerie' creee (id={obj.id}, ordre={obj.ordre}).")
else:
    print("DEJA FAIT : la categorie 'hotellerie' existait deja.")