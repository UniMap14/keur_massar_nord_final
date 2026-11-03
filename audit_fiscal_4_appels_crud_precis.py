# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_fiscal_4_appels_crud_precis.py', encoding='utf-8').read())"
"""
chemin = "foncier/dashboard_views.py"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

for motif in ["_crud_views(\n    Contribuable", "_crud_views(Contribuable", "_crud_views(\n    Taxation", "_crud_views(Taxation",
              "_crud_views(\n    Paiement", "_crud_views(Paiement"]:
    idx = contenu.find(motif)
    if idx != -1:
        print("=" * 100)
        print("trouve :", repr(motif), "a la position", idx)
        print("=" * 100)
        print(contenu[idx: idx + 400])
        print()

print("=" * 100)
print("Recherche large : toute ligne contenant '_crud_views(' suivie des 3 lignes suivantes")
print("=" * 100)
lignes = contenu.splitlines()
for i, l in enumerate(lignes):
    if "_crud_views(" in l:
        for j in range(i, min(i + 4, len(lignes))):
            print(lignes[j])
        print("...")
        print()