# -*- coding: utf-8 -*-
"""
Reduit de moitie la hauteur du bandeau photo (hero) sur Cartotheque et
Galerie : 340px -> 170px (desktop), 300px -> 150px (mobile).

Idempotent.
"""
FICHIERS = [
    ("foncier/templates/foncier/cartotheque.html", "carto-hero"),
    ("foncier/templates/foncier/galerie.html", "gal-hero"),
]

erreurs = []
total_remplacements = 0

for chemin, prefixe in FICHIERS:
    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read()

    ANCIEN_DESKTOP = f'.{prefixe}{{ position:relative; height:340px; overflow:hidden; }}'
    NOUVEAU_DESKTOP = f'.{prefixe}{{ position:relative; height:170px; overflow:hidden; }}'

    ANCIEN_MOBILE = f'@media (max-width: 700px){{ .{prefixe}{{ height:300px; }} }}'
    NOUVEAU_MOBILE = f'@media (max-width: 700px){{ .{prefixe}{{ height:150px; }} }}'

    deja_fait = (f'height:170px' in contenu and f'.{prefixe}{{' in contenu)

    if deja_fait:
        print(f"{chemin} : deja a la bonne taille (ignore).")
        continue

    if ANCIEN_DESKTOP not in contenu:
        erreurs.append(f"{chemin} : ancre hauteur desktop introuvable")
        continue
    if ANCIEN_MOBILE not in contenu:
        erreurs.append(f"{chemin} : ancre hauteur mobile introuvable")
        continue

    contenu = contenu.replace(ANCIEN_DESKTOP, NOUVEAU_DESKTOP, 1)
    contenu = contenu.replace(ANCIEN_MOBILE, NOUVEAU_MOBILE, 1)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    total_remplacements += 1
    print(f"{chemin} : OK, bandeau reduit.")

if erreurs:
    print("\nERREUR(S) :")
    for e in erreurs:
        print(" -", e)
else:
    print(f"\nTermine : {total_remplacements} fichier(s) modifie(s).")