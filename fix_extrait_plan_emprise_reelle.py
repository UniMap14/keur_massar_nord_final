# -*- coding: utf-8 -*-
"""
Correction de fond du cadrage du plan de l'extrait de plan foncier :

Cause reelle identifiee : le plan etait toujours dessine dans un CANVAS
CARRE (largeur == hauteur), puis place dans une case CARREE du PDF.
Comme la vraie disposition des parcelles est rarement un carre parfait
(terrain en diagonale, lotissement allonge...), une bonne partie du
carre restait necessairement blanche -- ce n'etait pas un probleme de
resolution ni de CSS, mais de forme du cadre impose.

Correctif : le plan est maintenant dessine avec un cadre qui epouse la
vraie forme (largeur/hauteur) du nuage de parcelles trouvees, sans la
forcer a etre carree ; et cote PDF, l'image est placee en utilisant la
largeur ET la hauteur reellement disponibles entre le titre et le bas
de page (au lieu d'une case fixe de 148mm), en conservant exactement
les proportions (aucune deformation des polygones).

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_emprise_reelle.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "taille_px_cible"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

ANCIENNE_FONCTION = '''def _generer_image_plan_type_officiel(parcelle, voisines, taille_px=1400):
    """Dessine le plan de situation sur le modele d'un extrait de plan
    cadastral officiel : parcelles voisines en trait fin avec leur
    numero, parcelle principale en rouge avec cotes (longueur de chaque
    cote) et reperes B1..Bn a chaque sommet, fleche du Nord -- sans
    grille de coordonnees (absente du modele officiel). Renvoie
    (buffer_png, texte_echelle)."""
    import io as io_module
    import math
    from PIL import Image, ImageDraw, ImageFont

    sommets_principal = _sommets_parcelle_utm(parcelle)

    polygones_voisins = []
    for voisine in voisines:
        try:
            pts = _anneau_exterieur_utm(voisine.geom[0])
        except Exception:
            continue
        if pts:
            polygones_voisins.append((voisine, pts))

    tous_points = list(sommets_principal)
    for _, pts in polygones_voisins:
        tous_points.extend(pts)

    xs = [p[0] for p in tous_points]
    ys = [p[1] for p in tous_points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    etendue_brute = max(xmax - xmin, ymax - ymin, 10.0)
    marge_m = etendue_brute * 0.06 + 3
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    etendue = etendue_brute + 2 * marge_m
    xmin, xmax = cx - etendue / 2, cx + etendue / 2
    ymin, ymax = cy - etendue / 2, cy + etendue / 2

    marge_cadre = int(taille_px * 0.06)
    zone_dessin = taille_px - 2 * marge_cadre
    echelle_px_par_m = zone_dessin / etendue

    def vers_px(point_x, point_y):
        px = marge_cadre + (point_x - xmin) * echelle_px_par_m
        py = taille_px - marge_cadre - (point_y - ymin) * echelle_px_par_m
        return (px, py)

    img = Image.new("RGB", (taille_px, taille_px), "white")
    draw = ImageDraw.Draw(img)

    try:
        police_num = ImageFont.load_default(size=26)
        police_label = ImageFont.load_default(size=20)
        police_cote = ImageFont.load_default(size=18)
        police_nord = ImageFont.load_default(size=24)
    except TypeError:
        police_num = police_label = police_cote = police_nord = ImageFont.load_default()

    # Parcelles voisines : trait fin noir + numero au centre, avec une
    # taille de police adaptee a la taille reelle de chaque parcelle a
    # l'ecran (pour ne jamais deborder), et pas de numero du tout si la
    # parcelle est trop petite pour l'accueillir proprement.
    cache_polices = {}

    def _police_adaptee(taille_cible):
        taille_cible = max(6, min(26, int(taille_cible)))
        if taille_cible not in cache_polices:
            try:
                cache_polices[taille_cible] = ImageFont.load_default(size=taille_cible)
            except TypeError:
                cache_polices[taille_cible] = ImageFont.load_default()
        return cache_polices[taille_cible]

    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, outline=(40, 40, 40), width=2)
            xs_v = [p[0] for p in pts_px]
            ys_v = [p[1] for p in pts_px]
            largeur_bbox = max(xs_v) - min(xs_v)
            hauteur_bbox = max(ys_v) - min(ys_v)
            centre_x = sum(xs_v) / len(pts_px)
            centre_y = sum(ys_v) / len(pts_px)
            taille_police_v = min(largeur_bbox, hauteur_bbox) * 0.32
            if taille_police_v >= 7:
                etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else "?")
                draw.text(
                    (centre_x, centre_y), str(etiquette), fill=(30, 30, 30),
                    font=_police_adaptee(taille_police_v), anchor="mm",
                )

    # Parcelle principale : contour rouge epais, cotes et reperes B1..Bn.
    pts_px = [vers_px(px, py) for px, py in sommets_principal]
    if len(pts_px) >= 2:
        draw.polygon(pts_px, outline=(192, 20, 20), width=6)

        centre_x = sum(p[0] for p in pts_px) / len(pts_px)
        centre_y = sum(p[1] for p in pts_px) / len(pts_px)

        n = len(pts_px)
        for i in range(n):
            x1, y1 = pts_px[i]
            x2, y2 = pts_px[(i + 1) % n]

            ux1, uy1 = sommets_principal[i]
            ux2, uy2 = sommets_principal[(i + 1) % n]
            longueur = math.hypot(ux2 - ux1, uy2 - uy1)

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            norm = math.hypot(dx, dy) or 1
            nvx, nvy = -dy / norm, dx / norm
            vers_centre_x, vers_centre_y = centre_x - mx, centre_y - my
            if nvx * vers_centre_x + nvy * vers_centre_y > 0:
                nvx, nvy = -nvx, -nvy
            decalage = 26
            draw.text(
                (mx + nvx * decalage, my + nvy * decalage),
                "{:.2f}".format(longueur),
                fill=(140, 10, 10), font=police_cote, anchor="mm",
            )

            draw.ellipse([x1 - 4, y1 - 4, x1 + 4, y1 + 4], fill=(192, 20, 20))
            bx, by = x1 + nvx * 18 - (dx / norm) * 18, y1 + nvy * 18 - (dy / norm) * 18
            draw.text((bx, by), "B{}".format(i + 1), fill=(192, 20, 20), font=police_label, anchor="mm")

        xs_p = [p[0] for p in pts_px]
        ys_p = [p[1] for p in pts_px]
        taille_police_p = max(10, min(max(xs_p) - min(xs_p), max(ys_p) - min(ys_p)) * 0.3)
        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")
        draw.text(
            (centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15),
            font=_police_adaptee(taille_police_p), anchor="mm",
        )

    # Fleche du Nord.
    nx0 = taille_px - marge_cadre - 60
    ny0 = marge_cadre + 70
    draw.line([(nx0, ny0 + 46), (nx0, ny0 - 26)], fill=(20, 20, 20), width=4)
    draw.polygon([(nx0, ny0 - 42), (nx0 - 13, ny0 - 16), (nx0 + 13, ny0 - 16)], fill=(20, 20, 20))
    draw.text((nx0, ny0 - 56), "N", fill=(20, 20, 20), font=police_nord, anchor="mm")

    tampon = io_module.BytesIO()
    img.save(tampon, format="PNG")
    tampon.seek(0)

    denominateurs_usuels = [100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000]
    denominateur_brut = (etendue * 1000) / 180
    echelle_texte = "1 / {}e".format(next(
        (d for d in denominateurs_usuels if d >= denominateur_brut), denominateurs_usuels[-1]
    ))

    return tampon, echelle_texte
'''

NOUVELLE_FONCTION = '''def _generer_image_plan_type_officiel(parcelle, voisines, taille_px_cible=1700):
    """Dessine le plan de situation sur le modele d'un extrait de plan
    cadastral officiel : parcelles voisines en trait fin avec leur
    numero, parcelle principale en rouge avec cotes (longueur de chaque
    cote) et reperes B1..Bn a chaque sommet, fleche du Nord -- sans
    grille de coordonnees (absente du modele officiel). Le cadre du
    dessin epouse la vraie forme (largeur/hauteur) du nuage de
    parcelles trouvees, sans etre force a un carre, pour ne jamais
    laisser de grandes zones blanches inutiles. Renvoie
    (buffer_png, texte_echelle, largeur_px, hauteur_px)."""
    import io as io_module
    import math
    from PIL import Image, ImageDraw, ImageFont

    sommets_principal = _sommets_parcelle_utm(parcelle)

    polygones_voisins = []
    for voisine in voisines:
        try:
            pts = _anneau_exterieur_utm(voisine.geom[0])
        except Exception:
            continue
        if pts:
            polygones_voisins.append((voisine, pts))

    tous_points = list(sommets_principal)
    for _, pts in polygones_voisins:
        tous_points.extend(pts)

    xs = [p[0] for p in tous_points]
    ys = [p[1] for p in tous_points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # Emprise reelle des donnees : chaque axe garde sa propre etendue
    # (pas de carre impose), avec une marge de securite minime -- le
    # cadre du dessin epouse ainsi la vraie forme du nuage de parcelles.
    etendue_brute_x = max(xmax - xmin, 10.0)
    etendue_brute_y = max(ymax - ymin, 10.0)
    marge_m_x = etendue_brute_x * 0.04 + 2
    marge_m_y = etendue_brute_y * 0.04 + 2
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    etendue_x = etendue_brute_x + 2 * marge_m_x
    etendue_y = etendue_brute_y + 2 * marge_m_y
    xmin, xmax = cx - etendue_x / 2, cx + etendue_x / 2
    ymin, ymax = cy - etendue_y / 2, cy + etendue_y / 2

    echelle_px_par_m = taille_px_cible / max(etendue_x, etendue_y)
    taille_px_x = max(220, int(etendue_x * echelle_px_par_m))
    taille_px_y = max(220, int(etendue_y * echelle_px_par_m))

    def vers_px(point_x, point_y):
        px = (point_x - xmin) * echelle_px_par_m
        py = taille_px_y - (point_y - ymin) * echelle_px_par_m
        return (px, py)

    img = Image.new("RGB", (taille_px_x, taille_px_y), "white")
    draw = ImageDraw.Draw(img)

    try:
        police_num = ImageFont.load_default(size=26)
        police_label = ImageFont.load_default(size=20)
        police_cote = ImageFont.load_default(size=18)
        police_nord = ImageFont.load_default(size=24)
    except TypeError:
        police_num = police_label = police_cote = police_nord = ImageFont.load_default()

    # Parcelles voisines : trait fin noir + numero au centre, avec une
    # taille de police adaptee a la taille reelle de chaque parcelle a
    # l'ecran (pour ne jamais deborder), et pas de numero du tout si la
    # parcelle est trop petite pour l'accueillir proprement.
    cache_polices = {}

    def _police_adaptee(taille_cible):
        taille_cible = max(6, min(26, int(taille_cible)))
        if taille_cible not in cache_polices:
            try:
                cache_polices[taille_cible] = ImageFont.load_default(size=taille_cible)
            except TypeError:
                cache_polices[taille_cible] = ImageFont.load_default()
        return cache_polices[taille_cible]

    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, outline=(40, 40, 40), width=2)
            xs_v = [p[0] for p in pts_px]
            ys_v = [p[1] for p in pts_px]
            largeur_bbox = max(xs_v) - min(xs_v)
            hauteur_bbox = max(ys_v) - min(ys_v)
            centre_x = sum(xs_v) / len(pts_px)
            centre_y = sum(ys_v) / len(pts_px)
            taille_police_v = min(largeur_bbox, hauteur_bbox) * 0.32
            if taille_police_v >= 7:
                etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else "?")
                draw.text(
                    (centre_x, centre_y), str(etiquette), fill=(30, 30, 30),
                    font=_police_adaptee(taille_police_v), anchor="mm",
                )

    # Parcelle principale : contour rouge epais, cotes et reperes B1..Bn.
    pts_px = [vers_px(px, py) for px, py in sommets_principal]
    if len(pts_px) >= 2:
        draw.polygon(pts_px, outline=(192, 20, 20), width=6)

        centre_x = sum(p[0] for p in pts_px) / len(pts_px)
        centre_y = sum(p[1] for p in pts_px) / len(pts_px)

        n = len(pts_px)
        for i in range(n):
            x1, y1 = pts_px[i]
            x2, y2 = pts_px[(i + 1) % n]

            ux1, uy1 = sommets_principal[i]
            ux2, uy2 = sommets_principal[(i + 1) % n]
            longueur = math.hypot(ux2 - ux1, uy2 - uy1)

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            norm = math.hypot(dx, dy) or 1
            nvx, nvy = -dy / norm, dx / norm
            vers_centre_x, vers_centre_y = centre_x - mx, centre_y - my
            if nvx * vers_centre_x + nvy * vers_centre_y > 0:
                nvx, nvy = -nvx, -nvy
            decalage = 26
            draw.text(
                (mx + nvx * decalage, my + nvy * decalage),
                "{:.2f}".format(longueur),
                fill=(140, 10, 10), font=police_cote, anchor="mm",
            )

            draw.ellipse([x1 - 4, y1 - 4, x1 + 4, y1 + 4], fill=(192, 20, 20))
            bx, by = x1 + nvx * 18 - (dx / norm) * 18, y1 + nvy * 18 - (dy / norm) * 18
            draw.text((bx, by), "B{}".format(i + 1), fill=(192, 20, 20), font=police_label, anchor="mm")

        xs_p = [p[0] for p in pts_px]
        ys_p = [p[1] for p in pts_px]
        taille_police_p = max(10, min(max(xs_p) - min(xs_p), max(ys_p) - min(ys_p)) * 0.3)
        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")
        draw.text(
            (centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15),
            font=_police_adaptee(taille_police_p), anchor="mm",
        )

    # Fleche du Nord (coin haut droit).
    nx0 = taille_px_x - 70
    ny0 = 90
    draw.line([(nx0, ny0 + 46), (nx0, ny0 - 26)], fill=(20, 20, 20), width=4)
    draw.polygon([(nx0, ny0 - 42), (nx0 - 13, ny0 - 16), (nx0 + 13, ny0 - 16)], fill=(20, 20, 20))
    draw.text((nx0, ny0 - 56), "N", fill=(20, 20, 20), font=police_nord, anchor="mm")

    tampon = io_module.BytesIO()
    img.save(tampon, format="PNG")
    tampon.seek(0)

    denominateurs_usuels = [100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000]
    denominateur_brut = (max(etendue_x, etendue_y) * 1000) / 180
    echelle_texte = "1 / {}e".format(next(
        (d for d in denominateurs_usuels if d >= denominateur_brut), denominateurs_usuels[-1]
    ))

    return tampon, echelle_texte, taille_px_x, taille_px_y
'''

ANCIEN_APPEL = '''    taille_plan = min(largeur - 2 * marge, 148 * mm)
    echelle_texte = "-"
    try:
        voisines = _voisines_parcelle(parcelle, max_resultats=160)
        image_plan, echelle_texte = _generer_image_plan_type_officiel(parcelle, voisines)
        x_plan = (largeur - taille_plan) / 2
        c.drawImage(
            ImageReader(image_plan), x_plan, y - taille_plan,
            width=taille_plan, height=taille_plan,
            preserveAspectRatio=True, mask="auto",
        )
    except Exception:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(largeur / 2, y - taille_plan / 2, "Plan non disponible pour cette parcelle.")

    y -= taille_plan + 8 * mm
'''

NOUVEL_APPEL = '''    dispo_largeur = largeur - 2 * marge
    dispo_hauteur = max(70 * mm, y - 47 * mm)
    echelle_texte = "-"
    hauteur_plan_reelle = dispo_hauteur
    try:
        voisines = _voisines_parcelle(parcelle, max_resultats=220)
        image_plan, echelle_texte, largeur_px, hauteur_px = _generer_image_plan_type_officiel(parcelle, voisines)
        ratio_image = hauteur_px / largeur_px
        if dispo_largeur * ratio_image <= dispo_hauteur:
            largeur_plan_reelle = dispo_largeur
            hauteur_plan_reelle = dispo_largeur * ratio_image
        else:
            hauteur_plan_reelle = dispo_hauteur
            largeur_plan_reelle = dispo_hauteur / ratio_image
        x_plan = marge + (dispo_largeur - largeur_plan_reelle) / 2
        c.drawImage(
            ImageReader(image_plan), x_plan, y - hauteur_plan_reelle,
            width=largeur_plan_reelle, height=hauteur_plan_reelle,
            preserveAspectRatio=True, mask="auto",
        )
    except Exception:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(largeur / 2, y - dispo_hauteur / 2, "Plan non disponible pour cette parcelle.")

    y -= hauteur_plan_reelle + 8 * mm
'''

erreurs = []
for nom, ancre in (("fonction de dessin du plan", ANCIENNE_FONCTION), ("appel/placement dans le PDF", ANCIEN_APPEL)):
    if ancre not in contenu:
        erreurs.append(f"- ancre introuvable pour « {nom} »")
    elif contenu.count(ancre) != 1:
        erreurs.append(f"- ancre « {nom} » trouvee {contenu.count(ancre)} fois (attendu 1)")

if erreurs:
    print("ERREUR : certains blocs n'ont pas pu etre localises tels quels :")
    for e in erreurs:
        print(e)
    raise SystemExit("Aucun fichier n'a ete modifie (securite : tout ou rien).")

contenu = contenu.replace(ANCIENNE_FONCTION, NOUVELLE_FONCTION)
contenu = contenu.replace(ANCIEN_APPEL, NOUVEL_APPEL)

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : le plan epouse maintenant sa vraie forme et occupe l'espace reellement disponible.")