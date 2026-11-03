# -*- coding: utf-8 -*-
"""
Remplace entierement extrait_cadastral_pdf_view (et ajoute les fonctions
utilitaires necessaires juste avant) dans foncier/views.py, pour produire
un extrait de plan foncier avec un vrai plan de situation (geometrie
PostGIS), un tableau de coordonnees UTM Zone 28N et une legende -- sur
le modele d'un extrait de plan cadastral officiel.

Idempotent : si le marqueur _wgs84_to_utm28n est deja present, ne fait
rien.
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "_wgs84_to_utm28n"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    ancre = "def extrait_cadastral_pdf_view(request, pk):"
    idx = contenu.find(ancre)
    if idx == -1:
        raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")

    idx_ligne = contenu.rfind("\n", 0, idx) + 1
    avant = contenu[:idx_ligne]
    lignes_avant = avant.splitlines(keepends=True)
    if lignes_avant and lignes_avant[-1].strip() == "@login_required":
        avant = "".join(lignes_avant[:-1])

    nouveau_bloc = '''def _wgs84_to_utm28n(lon, lat):
    """Convertit des coordonnees WGS84 (degres) en coordonnees UTM Zone
    28N (metres), la projection utilisee au Senegal. Formule standard
    de Snyder, implementee ici pour ne pas dependre de pyproj/GDAL."""
    import math

    a = 6378137.0
    f = 1 / 298.257223563
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    k0 = 0.9996
    lon0 = math.radians(-15.0)

    phi = math.radians(lat)
    lam = math.radians(lon)

    n = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
    t = math.tan(phi) ** 2
    cc = ep2 * math.cos(phi) ** 2
    aa = math.cos(phi) * (lam - lon0)

    m = a * (
        (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256) * phi
        - (3 * e2 / 8 + 3 * e2 ** 2 / 32 + 45 * e2 ** 3 / 1024) * math.sin(2 * phi)
        + (15 * e2 ** 2 / 256 + 45 * e2 ** 3 / 1024) * math.sin(4 * phi)
        - (35 * e2 ** 3 / 3072) * math.sin(6 * phi)
    )

    x = k0 * n * (
        aa + (1 - t + cc) * aa ** 3 / 6
        + (5 - 18 * t + t ** 2 + 72 * cc - 58 * ep2) * aa ** 5 / 120
    ) + 500000.0

    y = k0 * (
        m + n * math.tan(phi) * (
            aa ** 2 / 2 + (5 - t + 9 * cc + 4 * cc ** 2) * aa ** 4 / 24
            + (61 - 58 * t + t ** 2 + 600 * cc - 330 * ep2) * aa ** 6 / 720
        )
    )
    return x, y


def _anneau_exterieur_utm(polygone):
    """Sommets (x, y) en UTM 28N de l'anneau exterieur d'un Polygon
    GEOS, sans le point de fermeture duplique."""
    coords = list(polygone.exterior_ring.coords)
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    return [_wgs84_to_utm28n(lon, lat) for lon, lat in coords]


def _sommets_parcelle_utm(parcelle):
    polygone = parcelle.geom[0]
    return _anneau_exterieur_utm(polygone)


def _voisines_parcelle(parcelle, rayon_m=70, max_resultats=25):
    """Parcelles dont l'emprise est proche de celle de `parcelle`, pour
    dessiner le plan de situation : comparaison de boites englobantes
    en Python pur (via .extent, deja calcule par GEOS), sans dependre
    de fonctions spatiales avancees ni d'index particulier."""
    import math
    from .models import Parcelle

    xmin, ymin, xmax, ymax = parcelle.geom.extent
    lat_centre = (ymin + ymax) / 2
    tampon_lat = rayon_m / 111320.0
    tampon_lon = rayon_m / (111320.0 * max(math.cos(math.radians(lat_centre)), 0.15))

    zxmin, zxmax = xmin - tampon_lon, xmax + tampon_lon
    zymin, zymax = ymin - tampon_lat, ymax + tampon_lat

    if parcelle.zone_id:
        candidats = Parcelle.objects.filter(zone_id=parcelle.zone_id).exclude(pk=parcelle.pk)
    else:
        candidats = Parcelle.objects.exclude(pk=parcelle.pk)
    candidats = candidats.only("id", "nicad", "numero_parcelle", "geom")[:600]

    voisines = []
    for cand in candidats:
        try:
            cxmin, cymin, cxmax, cymax = cand.geom.extent
        except Exception:
            continue
        chevauche = not (
            cxmax < zxmin or cxmin > zxmax or cymax < zymin or cymin > zymax
        )
        if chevauche:
            voisines.append(cand)
        if len(voisines) >= max_resultats:
            break
    return voisines


def _pas_grille_adapte(etendue_m):
    for pas in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if etendue_m / pas <= 8:
            return pas
    return 2000


def _generer_image_plan_situation(parcelle, voisines, taille_px=1200):
    """Dessine le plan de situation (parcelle + voisines + grille +
    fleche nord) en PNG via Pillow et renvoie un buffer pret a etre
    insere dans le PDF."""
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
    marge_m = etendue_brute * 0.18 + 4
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    etendue = etendue_brute + 2 * marge_m
    xmin, xmax = cx - etendue / 2, cx + etendue / 2
    ymin, ymax = cy - etendue / 2, cy + etendue / 2

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


def _dessiner_cadre_titre(c, x, y_haut, largeur, hauteur, titre, couleur_texte, couleur_bordure, couleur_bandeau):
    """Cadre avec bandeau de titre en haut (comme les rubriques d'un
    extrait cadastral officiel). Renvoie le y de depart du contenu."""
    from reportlab.lib.units import mm

    bandeau = 6 * mm
    c.setStrokeColor(couleur_bordure)
    c.setLineWidth(0.6)
    c.rect(x, y_haut - hauteur, largeur, hauteur, fill=False, stroke=True)
    c.setFillColor(couleur_bandeau)
    c.rect(x, y_haut - bandeau, largeur, bandeau, fill=True, stroke=False)
    c.setStrokeColor(couleur_bordure)
    c.line(x, y_haut - bandeau, x + largeur, y_haut - bandeau)
    c.setFillColor(couleur_texte)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2 * mm, y_haut - bandeau + 1.8 * mm, titre)
    return y_haut - bandeau - 5 * mm


@login_required
def extrait_cadastral_pdf_view(request, pk):
    """
    Genere l'extrait de plan foncier officiel en PDF pour une demande de
    service PRETE et payee (si payante) : localisation, proprietaire,
    identification du titre, plan de situation avec grille de
    coordonnees UTM Zone 28N, tableau des sommets et legende.
    """
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from .models import DemandeService

    demande = get_object_or_404(DemandeService, pk=pk, demandeur=request.user)

    if demande.statut != "PRETE":
        messages.error(request, "Ce document n'est pas encore pret.")
        return redirect("citoyen_demande_detail", pk=pk)

    if demande.type_demande.tarif and demande.type_demande.tarif > 0 and demande.statut_paiement != "CONFIRME":
        messages.error(
            request,
            "Le paiement de cette demarche doit d'abord etre valide avant de pouvoir telecharger le document."
        )
        return redirect("citoyen_demande_detail", pk=pk)

    parcelle = demande.parcelle
    if parcelle is None:
        messages.error(request, "Aucune parcelle n'est associee a cette demarche.")
        return redirect("citoyen_demande_detail", pk=pk)

    numero_doc = "EPF-{}".format(demande.numero_dossier)
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "EXTRAIT DE PLAN FONCIER", numero_doc
    )

    largeur_contenu = largeur - 2 * marge
    BANDEAU_CLAIR = HexColor("#f2ede1")

    titre_foncier = parcelle.numero_titre_foncier or parcelle.nicad
    section_label = parcelle.section_cadastrale or "-"
    parcelle_label = parcelle.numero_parcelle or parcelle.nicad

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, "TITRE / REFERENCE : {}".format(titre_foncier))
    c.setFont("Helvetica", 9)
    c.drawRightString(
        largeur - marge, y,
        "Section : {}    Parcelle : {}".format(section_label, parcelle_label)
    )
    y -= 6 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 7 * mm

    largeur_col = (largeur_contenu - 6 * mm) / 2
    hauteur_rangee1 = 32 * mm
    x_gauche = marge
    x_droite = marge + largeur_col + 6 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_col, hauteur_rangee1,
        "LOCALISATION DE LA PARCELLE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    quartier = parcelle.adresse_parcelle or (parcelle.zone.nom if parcelle.zone_id else "-")
    champs_localisation = [
        ("Region", "DAKAR"),
        ("Departement", "KEUR MASSAR"),
        ("Commune", "KEUR MASSAR NORD"),
        ("Quartier / Secteur", quartier),
    ]
    yc = y_contenu
    for label, valeur in champs_localisation:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_gauche + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_gauche + largeur_col - 2 * mm, yc, str(valeur)[:40])
        yc -= 5.2 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_droite, y, largeur_col, hauteur_rangee1,
        "PROPRIETAIRE(S)", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    if parcelle.proprietaire_id:
        nom_complet = "{} {}".format(parcelle.proprietaire.nom, parcelle.proprietaire.prenom)
        cni = parcelle.proprietaire.ni_cni or "-"
        domicile = parcelle.proprietaire.adresse or "-"
    else:
        nom_complet = "Non renseigne"
        cni = "-"
        domicile = "-"
    champs_proprietaire = [
        ("Nom et prenoms", nom_complet),
        ("N de CNI", cni),
        ("Domicile", domicile),
    ]
    yc = y_contenu
    for label, valeur in champs_proprietaire:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_droite + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_droite + largeur_col - 2 * mm, yc, str(valeur)[:36])
        yc -= 5.2 * mm

    y -= hauteur_rangee1 + 4 * mm

    hauteur_rangee2 = 32 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_col, hauteur_rangee2,
        "IDENTIFICATION DU TITRE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    champs_identification = [
        ("Titre foncier n", titre_foncier),
        ("Section cadastrale", section_label),
        ("N de parcelle", parcelle_label),
        ("Contenance", "{:,.0f} m2".format(parcelle.superficie).replace(",", " ") if parcelle.superficie else "-"),
    ]
    yc = y_contenu
    for label, valeur in champs_identification:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_gauche + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_gauche + largeur_col - 2 * mm, yc, str(valeur)[:40])
        yc -= 5.2 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_droite, y, largeur_col, hauteur_rangee2,
        "NATURE DE LA PROPRIETE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    champs_nature = [
        ("Nature du document", parcelle.get_type_document_display()),
        ("Usage / Occupation", parcelle.occupation_sol or "-"),
        ("Statut fiscal", parcelle.get_statut_fiscal_display()),
        ("Zone", parcelle.zone.nom if parcelle.zone_id else "-"),
    ]
    yc = y_contenu
    for label, valeur in champs_nature:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_droite + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_droite + largeur_col - 2 * mm, yc, str(valeur)[:36])
        yc -= 5.2 * mm

    y -= hauteur_rangee2 + 4 * mm

    hauteur_plan = 95 * mm
    largeur_plan = 100 * mm
    largeur_colonne_droite = largeur_contenu - largeur_plan - 6 * mm
    x_colonne_droite = marge + largeur_plan + 6 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_plan, hauteur_plan,
        "PLAN DE SITUATION", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )

    sommets = []
    try:
        voisines = _voisines_parcelle(parcelle)
        image_plan = _generer_image_plan_situation(parcelle, voisines)
        taille_image = min(largeur_plan - 4 * mm, hauteur_plan - 9 * mm)
        c.drawImage(
            ImageReader(image_plan),
            x_gauche + (largeur_plan - taille_image) / 2,
            y - 4 * mm - taille_image,
            width=taille_image, height=taille_image,
            preserveAspectRatio=True, mask="auto",
        )
        sommets = _sommets_parcelle_utm(parcelle)
    except Exception:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(x_gauche + largeur_plan / 2, y - 40 * mm, "Plan non disponible pour cette parcelle.")

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Oblique", 6.5)
    c.drawCentredString(x_gauche + largeur_plan / 2, y - hauteur_plan + 3 * mm, "Systeme : WGS 84 / UTM Zone 28N - echelle approximative")

    hauteur_coord = 56 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_colonne_droite, y, largeur_colonne_droite, hauteur_coord,
        "COORDONNEES (UTM 28N)", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_colonne_droite + 2 * mm, y_contenu, "Sommet")
    c.drawRightString(x_colonne_droite + largeur_colonne_droite * 0.6, y_contenu, "X (m)")
    c.drawRightString(x_colonne_droite + largeur_colonne_droite - 2 * mm, y_contenu, "Y (m)")
    yc = y_contenu - 4.5 * mm
    sommets_affiches = sommets[:8]
    for indice, (sx, sy) in enumerate(sommets_affiches, 1):
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica", 7.2)
        c.drawString(x_colonne_droite + 2 * mm, yc, "P{}".format(indice))
        c.drawRightString(x_colonne_droite + largeur_colonne_droite * 0.6, yc, "{:,.2f}".format(sx).replace(",", " "))
        c.drawRightString(x_colonne_droite + largeur_colonne_droite - 2 * mm, yc, "{:,.2f}".format(sy).replace(",", " "))
        yc -= 4.6 * mm
    if len(sommets) > 8:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(x_colonne_droite + 2 * mm, yc, "+ {} sommet(s) supplementaire(s)".format(len(sommets) - 8))

    y_legende = y - hauteur_coord - 4 * mm
    hauteur_legende = hauteur_plan - hauteur_coord - 4 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_colonne_droite, y_legende, largeur_colonne_droite, hauteur_legende,
        "LEGENDE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    yc = y_contenu
    c.setStrokeColor(HexColor("#c31e1e"))
    c.setLineWidth(2)
    c.rect(x_colonne_droite + 2 * mm, yc - 2.2 * mm, 6 * mm, 3 * mm, fill=False, stroke=True)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 7)
    c.drawString(x_colonne_droite + 10 * mm, yc - 2 * mm, "Limite de la parcelle")
    yc -= 6 * mm
    c.setStrokeColor(HexColor("#5a5a5a"))
    c.setLineWidth(1)
    c.rect(x_colonne_droite + 2 * mm, yc - 2.2 * mm, 6 * mm, 3 * mm, fill=False, stroke=True)
    c.setFillColor(VERT_FONCE)
    c.drawString(x_colonne_droite + 10 * mm, yc - 2 * mm, "Limite de parcelle voisine")
    yc -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.drawString(x_colonne_droite + 2 * mm, yc - 2 * mm, "N = orientation Nord (haut du plan)")

    y -= hauteur_plan + 4 * mm

    hauteur_notes = 20 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_contenu, hauteur_notes,
        "NOTES", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    notes = [
        "- Ce plan est un extrait du plan cadastral. Il ne constitue pas, a lui seul, un titre de propriete.",
        "- Les limites de la parcelle figurant sur ce plan sont donnees a titre indicatif.",
        "- Toute modification doit faire l'objet d'une mise a jour aupres du service du Cadastre de la commune.",
    ]
    yc = y_contenu
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 7.5)
    for ligne in notes:
        c.drawString(x_gauche + 2 * mm, yc, ligne)
        yc -= 4.3 * mm

    y -= hauteur_notes + 6 * mm

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_gauche, y, "LE CHEF DU SERVICE DU CADASTRE")
    c.drawString(x_droite, y, "VU ET CERTIFIE CONFORME")
    y -= 10 * mm
    c.setStrokeColor(BORDURE)
    c.setFont("Helvetica", 7)
    c.setFillColor(GRIS)
    c.line(x_gauche, y, x_gauche + largeur_col - 10 * mm, y)
    c.line(x_droite, y, x_droite + largeur_col - 10 * mm, y)
    c.drawString(x_gauche, y - 4 * mm, "Nom, date et signature")
    c.drawString(x_droite, y - 4 * mm, "Le Directeur du Cadastre")

    _pied_de_page_document(
        c, marge, hauteur,
        "Extrait de plan foncier delivre a titre informatif. Son authenticite peut etre "
        "verifiee aupres des services du cadastre de la commune de Keur Massar Nord."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="extrait_plan_foncier_{}.pdf"'.format(parcelle.nicad)
    return response
'''

    nouveau_contenu = avant + nouveau_bloc
    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(nouveau_contenu)
    print("Patch applique avec succes.")
    print("Nouvelle longueur du fichier :", len(nouveau_contenu), "caracteres")