# -*- coding: utf-8 -*-
"""
Corrige le cadrage du plan de situation : au lieu de dezoomer pour
inclure TOUTES les voisines trouvees (ce qui ecrasait les petites
parcelles en traits illisibles des qu'un groupe eloigne etait inclus),
le cadrage se base desormais uniquement sur la taille reelle de la
parcelle principale (zoom fixe, coherent, comme un vrai extrait de
plan cadastral). Seules les voisines qui tombent reellement dans ce
cadrage sont dessinees.

Idempotent.
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "largeur_principale = max(xs_p) - min(xs_p)"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    ancre_debut = "def _generer_image_plan_situation(parcelle, voisines, taille_px=1200):"
    ancre_fin = "def _dessiner_cadre_titre(c, x, y_haut, largeur, hauteur, titre, couleur_texte, couleur_bordure, couleur_bandeau):"
    i1 = contenu.find(ancre_debut)
    i2 = contenu.find(ancre_fin)
    if i1 == -1 or i2 == -1 or i2 < i1:
        raise SystemExit("ANCRES INTROUVABLES - abandon, rien n'a ete modifie.")

    nouveau_bloc = '''def _generer_image_plan_situation(parcelle, voisines, taille_px=1200):
    """Dessine le plan de situation (parcelle + voisines + grille +
    fleche nord) en PNG via Pillow et renvoie un buffer pret a etre
    insere dans le PDF. Le cadrage est fixe sur la parcelle principale
    (zoom coherent) : seules les voisines qui tombent dans ce cadrage
    sont affichees, pour eviter qu'un groupe de parcelles eloignees
    n'oblige a tout dezoomer."""
    import io as io_module
    import math
    from PIL import Image, ImageDraw, ImageFont

    sommets_principal = _sommets_parcelle_utm(parcelle)

    xs_p = [p[0] for p in sommets_principal]
    ys_p = [p[1] for p in sommets_principal]
    largeur_principale = max(xs_p) - min(xs_p)
    hauteur_principale = max(ys_p) - min(ys_p)
    cx = (max(xs_p) + min(xs_p)) / 2
    cy = (max(ys_p) + min(ys_p)) / 2

    etendue = max(largeur_principale, hauteur_principale, 25.0) * 1.7 + 20.0
    xmin, xmax = cx - etendue / 2, cx + etendue / 2
    ymin, ymax = cy - etendue / 2, cy + etendue / 2

    polygones_voisins = []
    for voisine in voisines:
        try:
            pts = _anneau_exterieur_utm(voisine.geom[0])
        except Exception:
            continue
        if not pts:
            continue
        vxmin = min(p[0] for p in pts)
        vxmax = max(p[0] for p in pts)
        vymin = min(p[1] for p in pts)
        vymax = max(p[1] for p in pts)
        chevauche = not (vxmax < xmin or vxmin > xmax or vymax < ymin or vymin > ymax)
        if chevauche:
            polygones_voisins.append((voisine, pts))

    marge_cadre = int(taille_px * 0.075)
    zone_dessin = taille_px - 2 * marge_cadre
    echelle = zone_dessin / etendue

    def vers_px(point_x, point_y):
        px = marge_cadre + (point_x - xmin) * echelle
        py = taille_px - marge_cadre - (point_y - ymin) * echelle
        return (px, py)

    img = Image.new("RGB", (taille_px, taille_px), "white")
    draw = ImageDraw.Draw(img)

    try:
        police_grille = ImageFont.load_default(size=18)
        police_label = ImageFont.load_default(size=22)
        police_num = ImageFont.load_default(size=28)
    except TypeError:
        police_grille = police_label = police_num = ImageFont.load_default()

    pas = _pas_grille_adapte(etendue)
    valeur = math.floor(xmin / pas) * pas
    while valeur <= xmax:
        p1 = vers_px(valeur, ymin)
        p2 = vers_px(valeur, ymax)
        draw.line([p1, p2], fill=(215, 215, 215), width=1)
        etiquette = "{:,.0f}".format(valeur).replace(",", " ")
        draw.text((p1[0], taille_px - marge_cadre + 14), etiquette, fill=(100, 100, 100), font=police_grille, anchor="mt")
        draw.text((p1[0], marge_cadre - 14), etiquette, fill=(100, 100, 100), font=police_grille, anchor="mb")
        valeur += pas

    valeur = math.floor(ymin / pas) * pas
    while valeur <= ymax:
        p1 = vers_px(xmin, valeur)
        p2 = vers_px(xmax, valeur)
        draw.line([p1, p2], fill=(215, 215, 215), width=1)
        etiquette = "{:,.0f}".format(valeur).replace(",", " ")
        draw.text((marge_cadre - 10, p1[1]), etiquette, fill=(100, 100, 100), font=police_grille, anchor="rm")
        draw.text((taille_px - marge_cadre + 10, p1[1]), etiquette, fill=(100, 100, 100), font=police_grille, anchor="lm")
        valeur += pas

    draw.rectangle(
        [marge_cadre, marge_cadre, taille_px - marge_cadre, taille_px - marge_cadre],
        outline=(60, 60, 60), width=2,
    )

    for voisine, pts in polygones_voisins:
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
        draw.text((centre_x, centre_y), str(etiquette_principale), fill=(175, 20, 20), font=police_num, anchor="mm")

    nx = taille_px - marge_cadre - 55
    ny = marge_cadre + 90
    draw.line([(nx, ny + 50), (nx, ny - 30)], fill=(25, 25, 25), width=4)
    draw.polygon([(nx, ny - 48), (nx - 14, ny - 18), (nx + 14, ny - 18)], fill=(25, 25, 25))
    draw.text((nx, ny - 62), "N", fill=(25, 25, 25), font=police_num, anchor="mm")

    tampon = io_module.BytesIO()
    img.save(tampon, format="PNG")
    tampon.seek(0)
    return tampon


'''
    contenu = contenu[:i1] + nouveau_bloc + contenu[i2:]

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")
    print("Nouvelle longueur du fichier :", len(contenu), "caracteres")