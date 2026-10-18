# -*- coding: utf-8 -*-
"""
Surcharge le padding-top global de .page-section UNIQUEMENT sur la page
Actualites (le fichier style.css global n'est pas touche, pour ne pas
affecter les autres pages qui utilisent la meme classe).

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/actualites_liste.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''  @media (max-width: 700px){ .actu-hero{ height:95px; } }

  .actu-toolbar {'''

NOUVEAU = '''  @media (max-width: 700px){ .actu-hero{ height:95px; } }

  .container.page-section{ padding-top:22px; }

  .actu-toolbar {'''

if '.container.page-section{ padding-top:22px; }' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable")
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