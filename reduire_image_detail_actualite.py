# -*- coding: utf-8 -*-
"""
Reduit la hauteur de la photo sur la page de detail d'une actualite.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/actualite_detail.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''  .actu-detail-photo {
    width: 100%; height: 320px; border-radius: var(--radius); overflow: hidden;'''

NOUVEAU = '''  .actu-detail-photo {
    width: 100%; height: 220px; border-radius: var(--radius); overflow: hidden;'''

if 'height: 220px; border-radius: var(--radius); overflow: hidden;' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre .actu-detail-photo introuvable")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")