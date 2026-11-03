# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_extrait_plan_2_recherche.py', encoding='utf-8').read())"
"""
import foncier.models as m

print("=" * 100)
print("Champs du modele TypeDemande")
print("=" * 100)
for champ in m.TypeDemande._meta.get_fields():
    print("-", champ.name)
print()

print("=" * 100)
print("Toutes les lignes TypeDemande (tous les champs texte)")
print("=" * 100)
for td in m.TypeDemande.objects.all():
    print(vars(td))
    print()