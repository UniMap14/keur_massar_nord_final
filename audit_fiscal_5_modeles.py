# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_fiscal_5_modeles.py', encoding='utf-8').read())"

ETAPE 5 de l'audit fiscal : recuperer la definition complete des modeles
fiscaux (Taxation, Paiement, Contribuable, TypeTaxe, PlanPaiement,
EcheancePlanPaiement, RecoursFiscal, DemandeExoneration) pour verifier
leur coherence (champs, defauts, contraintes, proprietes calculees).
"""
import inspect
import foncier.models as m

NOMS_A_CHERCHER = [
    "Contribuable", "TypeTaxe", "Taxation", "Paiement",
    "PlanPaiement", "EcheancePlanPaiement", "RecoursFiscal",
    "DemandeExoneration", "ExonerationFiscale", "Exoneration",
]

print("=" * 100)
print("1) Classes de modeles presentes dans foncier/models.py dont le nom correspond")
print("=" * 100)
noms_presents = []
for n in NOMS_A_CHERCHER:
    if hasattr(m, n):
        noms_presents.append(n)
        print("TROUVE :", n)
    else:
        print("absent :", n)
print()

print("=" * 100)
print("2) Source complete de chaque modele trouve")
print("=" * 100)
for n in noms_presents:
    cls = getattr(m, n)
    try:
        source = inspect.getsource(cls)
    except Exception as e:
        print(f"--- {n} : impossible de recuperer la source ({e}) ---")
        continue
    print("#" * 100)
    print(f"# MODELE : {n}")
    print("#" * 100)
    print(source)
    print()