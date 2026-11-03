# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_fiscal_1_vues.py', encoding='utf-8').read())"

ETAPE 1/4 de l'audit fiscal : inventaire de toutes les pages/vues liees
a la fiscalite (Taxations, Paiements, Contribuables, Types de taxe,
Plans de paiement, Exonerations, Recours...).
"""
import re
import os

print("=" * 100)
print("1) Toutes les routes dashboard_urls.py mentionnant taxation/paiement/contribuable/exoneration/recours/plan-paiement/type-taxe")
print("=" * 100)
chemin_urls = "foncier/dashboard_urls.py"
with open(chemin_urls, "r", encoding="utf-8", errors="replace") as f:
    contenu_urls = f.read()

mots_cles = ["taxation", "paiement", "contribuable", "exoneration", "exonér", "recours", "plan_paiement", "plan-paiement", "type_taxe", "type-taxe"]
for ligne in contenu_urls.splitlines():
    bas = ligne.lower()
    if any(m in bas for m in mots_cles):
        print(ligne.strip())
print()

print("=" * 100)
print("2) Toutes les fonctions de vue dans dashboard_views.py dont le nom contient l'un de ces mots")
print("=" * 100)
import foncier.dashboard_views as dv
noms_vues = [n for n in dir(dv) if any(m in n.lower() for m in [
    "taxation", "paiement", "contribuable", "exoner", "recours", "plan_paiement", "type_taxe"
])]
for n in sorted(noms_vues):
    print(n)
print()

print("=" * 100)
print("3) role_requis(...) utilise sur chacune de ces vues (pour verifier le cloisonnement)")
print("=" * 100)
import inspect
for n in sorted(noms_vues):
    fonction = getattr(dv, n)
    try:
        source = inspect.getsource(fonction)
    except Exception:
        continue
    premiere_lignes = "\n".join(source.splitlines()[:4])
    print(f"--- {n} ---")
    print(premiere_lignes)
    print()