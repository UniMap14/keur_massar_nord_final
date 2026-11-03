# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_zones.py', encoding='utf-8').read())"

Diagnostic de la page "Zones" (menu Foncier > Zones), vide pour le Chef
du Service Cadastre. On veut savoir :
  1) combien de zones existent reellement en base
  2) si la vue applique un filtre (par role, par agent...) qui pourrait
     exclure a tort des zones existantes
"""
import inspect
import foncier.dashboard_views as dv

print("=" * 100)
print("1) Code de la vue dashboard_zone_list :")
print("=" * 100)
print(inspect.getsource(dv.dashboard_zone_list))
print()

# Trouver le modele utilise par cette vue (QuartierOfficiel ? Zone ? ZoneAdministrative ?)
import foncier.models as m
candidats = [n for n in dir(m) if "zone" in n.lower() or "quartier" in n.lower()]
print("Classes candidates dans foncier.models :", candidats)
print()

for nom in candidats:
    classe = getattr(m, nom)
    if hasattr(classe, "_meta") and hasattr(classe.objects, "count"):
        try:
            total = classe.objects.count()
            print(f"  {nom}.objects.count() = {total}")
        except Exception as e:
            print(f"  {nom}.objects.count() -> erreur : {e}")
print()

print("Script termine. Copiez-collez toute la sortie ci-dessus.")