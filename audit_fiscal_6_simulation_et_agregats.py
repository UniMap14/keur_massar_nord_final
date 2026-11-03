# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_fiscal_6_simulation_et_agregats.py', encoding='utf-8').read())"

ETAPE 6 de l'audit fiscal :
A) Verifier si le champ Taxation.simulation_fiscale (taxations "academiques",
   pas reelles) est bien exclu de tous les calculs de montant_du /
   montant_paye / totaux affiches dans les tableaux de bord.
B) Chercher toutes les occurrences de 'simulation_fiscale' dans le code
   pour voir ou ce filtre est (ou n'est pas) applique.
C) Donnees reelles en base : combien de taxations sont marquees comme
   simulation, et quel montant total ca represente (pour mesurer l'impact
   si jamais ce n'est pas filtre).
"""
import os
import re
import foncier.models as m
from django.db.models import Sum

print("=" * 100)
print("A) Recherche de 'simulation_fiscale' dans tout le code Python du projet")
print("=" * 100)
racine = "."
for dossier, sous_dossiers, fichiers in os.walk(racine):
    # on ignore les dossiers techniques / environnement virtuel
    sous_dossiers[:] = [d for d in sous_dossiers if d not in (
        "venv", ".git", "__pycache__", "node_modules", "staticfiles", "media"
    )]
    for nomf in fichiers:
        if not nomf.endswith(".py"):
            continue
        chemin = os.path.join(dossier, nomf)
        try:
            with open(chemin, "r", encoding="utf-8", errors="replace") as f:
                contenu = f.read()
        except Exception:
            continue
        if "simulation_fiscale" in contenu:
            print("-" * 100)
            print("FICHIER :", chemin)
            for i, ligne in enumerate(contenu.splitlines(), start=1):
                if "simulation_fiscale" in ligne:
                    print(f"  L{i}: {ligne.strip()}")
print()

print("=" * 100)
print("B) Les agregats de dashboard_views.py (dashboard_home) excluent-ils simulation_fiscale ?")
print("=" * 100)
chemin_dv = "foncier/dashboard_views.py"
with open(chemin_dv, "r", encoding="utf-8", errors="replace") as f:
    contenu_dv = f.read()
idx = contenu_dv.find("def dashboard_home")
if idx != -1:
    fin = contenu_dv.find("\ndef ", idx + 10)
    print(contenu_dv[idx:fin if fin != -1 else idx + 6000])
print()

print("=" * 100)
print("C) Donnees reelles en base : impact des taxations 'simulation_fiscale=True'")
print("=" * 100)
nb_total = m.Taxation.objects.count()
nb_simulees = m.Taxation.objects.filter(simulation_fiscale=True).count()
montant_du_total = m.Taxation.objects.aggregate(t=Sum("montant_du"))["t"] or 0
montant_du_simule = m.Taxation.objects.filter(simulation_fiscale=True).aggregate(t=Sum("montant_du"))["t"] or 0
montant_du_reel = m.Taxation.objects.filter(simulation_fiscale=False).aggregate(t=Sum("montant_du"))["t"] or 0

print(f"Nombre total de taxations        : {nb_total}")
print(f"  dont simulations academiques   : {nb_simulees}")
print(f"Montant du total (TOUTES)        : {montant_du_total}")
print(f"  dont du sur simulations        : {montant_du_simule}")
print(f"  dont du sur taxations reelles  : {montant_du_reel}")
print()

montant_paye_total = m.Paiement.objects.filter(statut_paiement="CONFIRME").aggregate(t=Sum("montant"))["t"] or 0
montant_paye_sur_simulations = m.Paiement.objects.filter(
    statut_paiement="CONFIRME", taxation__simulation_fiscale=True
).aggregate(t=Sum("montant"))["t"] or 0
print(f"Montant recouvre total (CONFIRME)         : {montant_paye_total}")
print(f"  dont recouvre sur taxations simulees    : {montant_paye_sur_simulations}")