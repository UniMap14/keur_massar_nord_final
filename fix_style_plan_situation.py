# -*- coding: utf-8 -*-
"""
Change le style du plan de situation pour se rapprocher du geoportail :
parcelles voisines remplies (beige clair, bordure orange), parcelle
principale remplie (rouge clair, bordure rouge), au lieu de simples
contours. Augmente aussi un peu la marge de cadrage pour laisser plus
de place aux voisines directement adjacentes.

Idempotent.
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "230, 180, 110"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    ancien_voisines = '''    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, outline=(90, 90, 90), width=2)
            centre_x = sum(p[0] for p in pts_px) / len(pts_px)
            centre_y = sum(p[1] for p in pts_px) / len(pts_px)
            if marge_cadre < centre_x < taille_px - marge_cadre and marge_cadre < centre_y < taille_px - marge_cadre:
                etiquette = voisine.numero_parcelle or voisine.nicad[-4:]
                draw.text((centre_x, centre_y), str(etiquette), fill=(60, 60, 60), font=police_label, anchor="mm")

    pts_px = [vers_px(px, py) for px, py in sommets_principal]
    if len(pts_px) >= 2:
        draw.polygon(pts_px, outline=(195, 30, 30), width=5)
        centre_x = sum(p[0] for p in pts_px) / len(pts_px)
        centre_y = sum(p[1] for p in pts_px) / len(pts_px)
        etiquette_principale = parcelle.numero_parcelle or parcelle.nicad[-4:]
        draw.text((centre_x, centre_y), str(etiquette_principale), fill=(175, 20, 20), font=police_num, anchor="mm")'''

    if ancien_voisines not in contenu:
        print("ANCRE INTROUVABLE - le fichier a peut-etre deja ete modifie differemment. Abandon, rien n'a ete change.")
    else:
        nouveau_voisines = '''    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, fill=(238, 218, 178), outline=(201, 138, 46), width=2)
            centre_x = sum(p[0] for p in pts_px) / len(pts_px)
            centre_y = sum(p[1] for p in pts_px) / len(pts_px)
            if marge_cadre < centre_x < taille_px - marge_cadre and marge_cadre < centre_y < taille_px - marge_cadre:
                etiquette = voisine.numero_parcelle or voisine.nicad[-4:]
                draw.text((centre_x, centre_y), str(etiquette), fill=(90, 60, 20), font=police_label, anchor="mm")

    pts_px = [vers_px(px, py) for px, py in sommets_principal]
    if len(pts_px) >= 2:
        draw.polygon(pts_px, fill=(250, 210, 200), outline=(195, 30, 30), width=5)
        centre_x = sum(p[0] for p in pts_px) / len(pts_px)
        centre_y = sum(p[1] for p in pts_px) / len(pts_px)
        etiquette_principale = parcelle.numero_parcelle or parcelle.nicad[-4:]
        draw.text((centre_x, centre_y), str(etiquette_principale), fill=(175, 20, 20), font=police_num, anchor="mm")'''

        contenu = contenu.replace(ancien_voisines, nouveau_voisines)

        contenu = contenu.replace(
            "etendue = max(largeur_principale, hauteur_principale, 25.0) * 1.7 + 20.0",
            "etendue = max(largeur_principale, hauteur_principale, 25.0) * 2.1 + 25.0",
        )

        with io.open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        print("Patch applique avec succes.")
        print("Nouvelle longueur du fichier :", len(contenu), "caracteres")