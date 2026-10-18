# -*- coding: utf-8 -*-
"""
Reduit l'espace entre le bandeau photo et la barre de recherche sur la
page Actualites.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/actualites_liste.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''  .actu-toolbar {
    max-width: 900px;
    margin: 40px auto 0;'''

NOUVEAU = '''  .actu-toolbar {
    max-width: 900px;
    margin: 18px auto 0;'''

if 'margin: 18px auto 0;' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre .actu-toolbar introuvable")
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