# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_logo_dgid.py', encoding='utf-8').read())"

Retrouve le fichier image du logo DGID deja utilise dans le footer du
site (foncier/templates/foncier/base.html), pour le reutiliser tel quel
dans le PDF de l'extrait de plan.
"""
import os

with open("foncier/templates/foncier/base.html", "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

bas = contenu.lower()
idx = bas.find("dgid")
while idx != -1:
    print("-" * 100)
    print(contenu[max(0, idx - 300): idx + 300])
    print()
    idx = bas.find("dgid", idx + 1)

print("=" * 100)
print("Fichiers sur disque dont le nom contient 'dgid' (sous static/)")
print("=" * 100)
for dossier, sous_dossiers, fichiers in os.walk("."):
    sous_dossiers[:] = [d for d in sous_dossiers if d not in (
        "venv", ".git", "__pycache__", "node_modules", "media"
    )]
    for nomf in fichiers:
        if "dgid" in nomf.lower():
            chemin = os.path.join(dossier, nomf)
            print(chemin, "-", os.path.getsize(chemin), "octets")