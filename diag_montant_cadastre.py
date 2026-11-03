# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_montant_cadastre.py', encoding='utf-8').read())"

Objectif : comprendre pourquoi le dashboard du Chef Cadastre n'affiche pas
de "montant total encaisse", alors que celui du Chef Fiscal en a un, et
verifier comment l'argent d'un "Extrait cadastral" (DemandeService) est
enregistre (y a-t-il un paiement lie, un tarif, etc.)
"""
import inspect
import foncier.models as m
import foncier.dashboard_views as dv

print("=" * 100)
print("1) Modele Paiement (champs)")
print("=" * 100)
try:
    print(inspect.getsource(m.Paiement))
except Exception as e:
    print("Erreur :", e)
print()

print("=" * 100)
print("2) Modele DemandeService (champs)")
print("=" * 100)
try:
    print(inspect.getsource(m.DemandeService))
except Exception as e:
    print("Erreur :", e)
print()

print("=" * 100)
print("3) Modele TypeDemande (champs)")
print("=" * 100)
try:
    print(inspect.getsource(m.TypeDemande))
except Exception as e:
    print("Erreur :", e)
print()

print("=" * 100)
print("4) Recherche de 'encaisse' / 'montant' dans dashboard_views.py")
print("=" * 100)
import os
chemin = "foncier/dashboard_views.py"
if os.path.exists(chemin):
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        lignes = f.readlines()
    for i, ligne in enumerate(lignes, start=1):
        if "encaiss" in ligne.lower() or ("montant" in ligne.lower() and "total" in ligne.lower()):
            debut = max(0, i - 3)
            fin = min(len(lignes), i + 2)
            print(f"--- autour de la ligne {i} ---")
            print("".join(lignes[debut:fin]))
            print()

print("=" * 100)
print("5) Y a-t-il un paiement/montant lie directement a DemandeService (sans passer par Taxation) ?")
print("=" * 100)
champs_demande = [f.name for f in m.DemandeService._meta.get_fields()]
print("Champs DemandeService :", champs_demande)
print()

print("=" * 100)
print("6) Combien de DemandeService 'Extrait cadastral' existent, ont-elles un tarif/montant ?")
print("=" * 100)
try:
    td = m.TypeDemande.objects.get(libelle__icontains="cadastral")
    print("TypeDemande :", td.libelle, "| tarif :", td.tarif, "| categorie :", td.categorie)
    nb = m.DemandeService.objects.filter(type_demande=td).count()
    print("Nombre de demandes de ce type :", nb)
except Exception as e:
    print("Erreur :", e)
print()

print("=" * 100)
print("7) Dashboard_home : contexte renvoye, cherche-t-on un decoupage par role pour les KPIs financiers ?")
print("=" * 100)
try:
    source = inspect.getsource(dv.dashboard_home)
    # On affiche seulement les 120 premieres lignes pour reperer la structure des KPIs
    print("\n".join(source.splitlines()[:120]))
except Exception as e:
    print("Erreur :", e)