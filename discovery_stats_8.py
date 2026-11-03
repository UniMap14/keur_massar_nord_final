from foncier.models import Parcelle, Infrastructure

print("=== Champs de Infrastructure ===")
for f in Infrastructure._meta.get_fields():
    print(f.name, '->', type(f).__name__)

print()
print("=== Champs de Parcelle lies a une date ===")
for f in Parcelle._meta.get_fields():
    if 'date' in f.name.lower() or 'creat' in f.name.lower() or 'maj' in f.name.lower() or 'modif' in f.name.lower():
        print(f.name, '->', type(f).__name__)

print()
print("=== Exemple de superficie (min/max) ===")
from django.db.models import Min, Max, Avg
print(Parcelle.objects.aggregate(mn=Min('superficie'), mx=Max('superficie'), moy=Avg('superficie')))