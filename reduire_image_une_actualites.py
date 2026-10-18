# -*- coding: utf-8 -*-
"""
Reduit la hauteur de l'image "A la une" sur la page Actualites (liste).

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/actualites_liste.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN_DESKTOP = '''  .actu-une-img { position: relative; min-height: 320px; background: var(--off-white, #f4f0e8); }'''
NOUVEAU_DESKTOP = '''  .actu-une-img { position: relative; min-height: 220px; background: var(--off-white, #f4f0e8); }'''

ANCIEN_MOBILE = '''    .actu-une-img { min-height: 220px; }'''
NOUVEAU_MOBILE = '''    .actu-une-img { min-height: 170px; }'''

if 'min-height: 220px; background' in contenu:
    pass
elif ANCIEN_DESKTOP not in contenu:
    erreurs.append("ancre desktop .actu-une-img introuvable")
else:
    contenu = contenu.replace(ANCIEN_DESKTOP, NOUVEAU_DESKTOP, 1)
    remplacements_ok += 1

if 'min-height: 170px; }' in contenu:
    pass
elif ANCIEN_MOBILE not in contenu:
    erreurs.append("ancre mobile .actu-une-img introuvable")
else:
    contenu = contenu.replace(ANCIEN_MOBILE, NOUVEAU_MOBILE, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")