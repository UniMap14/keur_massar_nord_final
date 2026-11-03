# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_fiscal_2_crud_generique.py', encoding='utf-8').read())"

ETAPE 2/4 (bis) : comprendre la fonction generique qui produit
dashboard_contribuable_create/update/delete, dashboard_paiement_*,
dashboard_taxation_* -- et confirmer si le role fiscal y est verifie
ou non.
"""
import inspect
import foncier.dashboard_views as dv

# On cherche la fonction usine (factory) en inspectant le module source
chemin = "foncier/dashboard_views.py"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    source = f.read()

print("=" * 100)
print("1) Definition de dashboard_contribuable_create / update / delete dans le fichier")
print("=" * 100)
for nom in ["dashboard_contribuable_create", "dashboard_contribuable_update", "dashboard_contribuable_delete",
            "dashboard_paiement_create", "dashboard_paiement_update", "dashboard_paiement_delete",
            "dashboard_taxation_create", "dashboard_taxation_update", "dashboard_taxation_delete"]:
    idx = source.find(f"\n{nom} = ")
    if idx == -1:
        idx = source.find(f"\n{nom}=")
    if idx == -1:
        # peut-etre assigne autrement, chercher 'nom ='
        import re
        m = re.search(rf"^{nom}\s*=.*$", source, re.MULTILINE)
        if m:
            print(f"{nom} :", m.group(0))
        else:
            print(f"{nom} : definition non trouvee par ce motif")
    else:
        fin = source.find("\n", idx + 1)
        print(source[idx:fin])
print()

print("=" * 100)
print("2) Recherche de la fonction usine (ex: '_vue_creation_generique', '_crud_generique', 'def create_view' alentours)")
print("=" * 100)
idx_factory = source.find("def create_view")
print(source[max(0, idx_factory - 1200): idx_factory + 2500])