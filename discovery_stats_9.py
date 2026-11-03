from foncier.models import Parcelle

print("=== Tous les champs de Parcelle ===")
for f in Parcelle._meta.get_fields():
    print(f.name, '->', type(f).__name__)

print("FIN")