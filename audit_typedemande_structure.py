# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_typedemande_structure.py', encoding='utf-8').read())"

Verifie la structure exacte du modele TypeDemande (champs, categories
existantes) et comment l'actuel "extrait de plan" y est configure, pour
preparer l'ajout des 5 motifs separes.
"""
import inspect
import foncier.models as m

print("=" * 100)
print("Champs du modele TypeDemande")
print("=" * 100)
for champ in m.TypeDemande._meta.get_fields():
    print("-", champ.name, "|", type(champ).__name__)
print()

print("=" * 100)
print("Source du modele TypeDemande")
print("=" * 100)
print(inspect.getsource(m.TypeDemande))
print()

print("=" * 100)
print("Toutes les lignes TypeDemande actuelles")
print("=" * 100)
for td in m.TypeDemande.objects.all():
    print(vars(td))
    print()

print("=" * 100)
print("Source du modele DemandeService (pour voir le lien avec parcelle/type_demande)")
print("=" * 100)
print(inspect.getsource(m.DemandeService))