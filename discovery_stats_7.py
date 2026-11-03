from foncier.models import Parcelle, CategorieInfrastructure

print("=== Champs de Parcelle lies a 'zone' ===")
for f in Parcelle._meta.get_fields():
    if 'zone' in f.name.lower():
        print(f.name, '->', type(f).__name__)

print()
print("=== Champs de CategorieInfrastructure ===")
for f in CategorieInfrastructure._meta.get_fields():
    print(f.name, '->', type(f).__name__)

print()
print("=== Exemple d'une parcelle avec zone (si elle existe) ===")
p = Parcelle.objects.exclude(zone__isnull=True).select_related('zone').first()
if p:
    print("zone.nom =", repr(p.zone.nom))
else:
    print("Aucune parcelle avec zone renseignee.")