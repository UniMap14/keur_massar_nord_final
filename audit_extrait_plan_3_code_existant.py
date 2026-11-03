# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_extrait_plan_3_code_existant.py', encoding='utf-8').read())"

Affiche le contenu integral du script fix_extrait_plan_foncier_pdf.py (deja
applique precedemment) et la portion de foncier/views.py qui genere le PDF
de l'extrait de plan, pour savoir precisement quoi adapter au vrai modele.
"""
import os

print("=" * 100)
print("1) Contenu de fix_extrait_plan_foncier_pdf.py")
print("=" * 100)
chemin = "fix_extrait_plan_foncier_pdf.py"
if os.path.exists(chemin):
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        print(f.read())
else:
    print("fichier introuvable")
print()

print("=" * 100)
print("2) Portion de foncier/views.py autour de 'extrait de plan' / 'extrait_plan'")
print("=" * 100)
chemin_vues = "foncier/views.py"
with open(chemin_vues, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

bas = contenu.lower()
positions = []
idx = 0
while True:
    idx = bas.find("extrait", idx)
    if idx == -1:
        break
    positions.append(idx)
    idx += 1

# on regroupe les positions proches pour eviter les doublons de blocs
blocs = []
for p in positions:
    if not blocs or p - blocs[-1][-1] > 3000:
        blocs.append([p])
    else:
        blocs[-1].append(p)

for bloc in blocs:
    debut = max(0, bloc[0] - 300)
    fin = min(len(contenu), bloc[-1] + 1500)
    print("-" * 100)
    print(f"[extrait du fichier, positions {debut}-{fin}]")
    print(contenu[debut:fin])
    print()