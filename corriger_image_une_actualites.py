# -*- coding: utf-8 -*-
"""
Corrige l'affichage de la photo "A la une" (liste) et de la photo sur la
page de detail : hauteur fixe (plus de min-height qui pouvait gonfler),
overflow cache, et recadrage vers le haut pour ne pas couper les visages
sur les photos au format portrait.

Gere les deux etats possibles du fichier (avant ou apres les scripts
precedents) grace a plusieurs ancres candidates.

Idempotent.
"""

# ------------------------------------------------------------------
# 1) Page liste : foncier/templates/foncier/actualites_liste.html
# ------------------------------------------------------------------
CHEMIN_LISTE = "foncier/templates/foncier/actualites_liste.html"
with open(CHEMIN_LISTE, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

CANDIDATS_DESKTOP = [
    '''  .actu-une-img { position: relative; min-height: 320px; background: var(--off-white, #f4f0e8); }''',
    '''  .actu-une-img { position: relative; min-height: 220px; background: var(--off-white, #f4f0e8); }''',
]
NOUVEAU_DESKTOP = '''  .actu-une-img { position: relative; height: 240px; overflow: hidden; background: var(--off-white, #f4f0e8); }'''

if 'height: 240px; overflow: hidden; background' in contenu:
    pass
else:
    trouve = False
    for ancre in CANDIDATS_DESKTOP:
        if ancre in contenu:
            contenu = contenu.replace(ancre, NOUVEAU_DESKTOP, 1)
            remplacements_ok += 1
            trouve = True
            break
    if not trouve:
        erreurs.append(f"{CHEMIN_LISTE} : ancre desktop .actu-une-img introuvable")

CANDIDATS_MOBILE = [
    '''    .actu-une-img { min-height: 220px; }''',
    '''    .actu-une-img { min-height: 170px; }''',
]
NOUVEAU_MOBILE = '''    .actu-une-img { height: 190px; }'''

if 'height: 190px; }' in contenu:
    pass
else:
    trouve = False
    for ancre in CANDIDATS_MOBILE:
        if ancre in contenu:
            contenu = contenu.replace(ancre, NOUVEAU_MOBILE, 1)
            remplacements_ok += 1
            trouve = True
            break
    if not trouve:
        erreurs.append(f"{CHEMIN_LISTE} : ancre mobile .actu-une-img introuvable")

ANCIEN_IMG_RULE = '''  .actu-une-img img { width: 100%; height: 100%; object-fit: cover; display: block; }'''
NOUVEAU_IMG_RULE = '''  .actu-une-img img { width: 100%; height: 100%; object-fit: cover; object-position: top center; display: block; }'''

if 'object-position: top center' in contenu and 'actu-une-img img' in contenu:
    pass
elif ANCIEN_IMG_RULE not in contenu:
    erreurs.append(f"{CHEMIN_LISTE} : ancre .actu-une-img img introuvable")
else:
    contenu = contenu.replace(ANCIEN_IMG_RULE, NOUVEAU_IMG_RULE, 1)
    remplacements_ok += 1

if not erreurs:
    with open(CHEMIN_LISTE, "w", encoding="utf-8") as f:
        f.write(contenu)

# ------------------------------------------------------------------
# 2) Page detail : foncier/templates/foncier/actualite_detail.html
# ------------------------------------------------------------------
CHEMIN_DETAIL = "foncier/templates/foncier/actualite_detail.html"
with open(CHEMIN_DETAIL, "r", encoding="utf-8") as f:
    contenu2 = f.read()

CANDIDATS_DETAIL = [
    '''  .actu-detail-photo {
    width: 100%; height: 320px; border-radius: var(--radius); overflow: hidden;''',
    '''  .actu-detail-photo {
    width: 100%; height: 220px; border-radius: var(--radius); overflow: hidden;''',
]
NOUVEAU_DETAIL = '''  .actu-detail-photo {
    width: 100%; height: 260px; border-radius: var(--radius); overflow: hidden;'''

if 'height: 260px; border-radius: var(--radius); overflow: hidden;' in contenu2:
    pass
else:
    trouve = False
    for ancre in CANDIDATS_DETAIL:
        if ancre in contenu2:
            contenu2 = contenu2.replace(ancre, NOUVEAU_DETAIL, 1)
            remplacements_ok += 1
            trouve = True
            break
    if not trouve:
        erreurs.append(f"{CHEMIN_DETAIL} : ancre .actu-detail-photo introuvable")

ANCIEN_DETAIL_IMG = '''  .actu-detail-photo img { width: 100%; height: 100%; object-fit: cover; }'''
NOUVEAU_DETAIL_IMG = '''  .actu-detail-photo img { width: 100%; height: 100%; object-fit: cover; object-position: top center; }'''

if 'object-position: top center' in contenu2 and 'actu-detail-photo img' in contenu2:
    pass
elif ANCIEN_DETAIL_IMG not in contenu2:
    erreurs.append(f"{CHEMIN_DETAIL} : ancre .actu-detail-photo img introuvable")
else:
    contenu2 = contenu2.replace(ANCIEN_DETAIL_IMG, NOUVEAU_DETAIL_IMG, 1)
    remplacements_ok += 1

if not erreurs:
    with open(CHEMIN_DETAIL, "w", encoding="utf-8") as f:
        f.write(contenu2)

# ------------------------------------------------------------------
if erreurs:
    print("ERREUR(S) : certains fichiers n'ont pas ete modifies.")
    for e in erreurs:
        print(" -", e)
else:
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")