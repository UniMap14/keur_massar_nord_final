# -*- coding: utf-8 -*-
"""
Remplace _pas_grille_adapte / _generer_image_plan_situation /
_dessiner_cadre_titre / extrait_cadastral_pdf_view (fin du fichier
foncier/views.py) par une nouvelle version de l'extrait de plan calquee
sur le modele officiel du Bureau du Cadastre (en-tete administratif
complet, cartouche NICAD/titre/lot/superficie, encadre Region/
Departement/Commune, plan avec cotes des cotes et reperes B1..Bn,
bande de certification "Le Chef du Bureau du Cadastre" / "Ce plan ne
constitue pas un titre de propriete").

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_modele_officiel.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "_generer_image_plan_type_officiel"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

ancre_debut = "def _pas_grille_adapte(etendue_m):"
idx_debut = contenu.find(ancre_debut)
if idx_debut == -1:
    raise SystemExit("ANCRE DE DEBUT INTROUVABLE - abandon, rien n'a ete modifie.")
if contenu.count(ancre_debut) != 1:
    raise SystemExit("ANCRE DE DEBUT trouvee plusieurs fois - abandon par securite.")

fin_attendue = 'response["Content-Disposition"] = \'attachment; filename="extrait_plan_foncier_{}.pdf"\'.format(parcelle.nicad)\n    return response\n'
if not contenu.rstrip().endswith(fin_attendue.strip()):
    raise SystemExit(
        "La fin du fichier ne correspond pas a ce qui est attendu "
        "(le fichier a peut-etre change depuis) - abandon par securite, rien n'a ete modifie."
    )

avant = contenu[:idx_debut]

nouveau_bloc = '''def _format_superficie_are_ca(superficie_m2):
    """Formate une superficie en m2 au format cadastral senegalais
    "Xa YYca" (1 are = 100 m2, 1 centiare = 1 m2), ex: 162 m2 -> "1a 62ca"."""
    if not superficie_m2:
        return "-"
    total_ca = int(round(float(superficie_m2)))
    ares = total_ca // 100
    centiares = total_ca % 100
    return "{}a {:02d}ca".format(ares, centiares)


def _generer_image_plan_type_officiel(parcelle, voisines, taille_px=1400):
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
    marge_m = etendue_brute * 0.22 + 6
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

    # Parcelles voisines : trait fin noir + numero au centre.
    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, outline=(40, 40, 40), width=2)
            centre_x = sum(p[0] for p in pts_px) / len(pts_px)
            centre_y = sum(p[1] for p in pts_px) / len(pts_px)
            etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else "?")
            draw.text((centre_x, centre_y), str(etiquette), fill=(30, 30, 30), font=police_label, anchor="mm")

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

        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")
        draw.text((centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15), font=police_num, anchor="mm")

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


@login_required
def extrait_cadastral_pdf_view(request, pk):
    """
    Genere l'extrait de plan foncier (PLAN POUR AUTORISATION DE CONSTRUIRE)
    en PDF, calque sur le modele exact d'un extrait de plan cadastral
    officiel delivre par le Bureau du Cadastre : en-tete administratif
    complet (Republique du Senegal, Ministere, DGID, Centre des Services
    Fiscaux, Bureau du Cadastre), encadre Region/Departement/Commune,
    cartouche NICAD/titre/lot/superficie, plan de situation avec cotes
    et reperes B1..Bn, et bande de certification en bas de page.
    """
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from django.utils import timezone
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

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4
    marge = 16 * mm
    NOIR = HexColor("#111111")
    GRIS = HexColor("#444444")

    y = hauteur - 14 * mm

    # ----- En-tete administratif, sur le modele du document officiel -----
    c.setFillColor(NOIR)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(marge, y, "REPUBLIQUE DU SENEGAL")
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(marge, y - 4 * mm, "Un Peuple - Un But - Une Foi")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(marge, y - 9 * mm, "MINISTERE DE L'ECONOMIE, DES FINANCES ET DU PLAN")
    c.setFont("Helvetica", 7)
    c.drawString(marge, y - 13 * mm, "DIRECTION GENERALE DES IMPOTS ET DES DOMAINES")
    c.setFillColor(GRIS)
    c.drawString(marge, y - 17 * mm, "Centre des Services Fiscaux de Keur Massar")
    c.drawString(marge, y - 21 * mm, "Bureau du Cadastre")

    largeur_boite = 55 * mm
    hauteur_boite = 20 * mm
    x_boite = largeur - marge - largeur_boite
    y_boite = y + 2 * mm
    c.setStrokeColor(NOIR)
    c.setLineWidth(0.6)
    c.rect(x_boite, y_boite - hauteur_boite, largeur_boite, hauteur_boite, fill=False, stroke=True)
    lignes_boite = [
        ("Region", "Dakar"),
        ("Departement", "Keur Massar"),
        ("Commune", "Keur Massar Nord"),
    ]
    yc = y_boite - 5 * mm
    c.setFont("Helvetica", 7.5)
    for label, valeur in lignes_boite:
        c.setFillColor(GRIS)
        c.drawString(x_boite + 2 * mm, yc, "{} :".format(label))
        c.setFillColor(NOIR)
        c.drawString(x_boite + 22 * mm, yc, valeur)
        yc -= 5.5 * mm

    y -= 27 * mm

    c.setStrokeColor(NOIR)
    c.setLineWidth(1.2)
    cx_nord = largeur / 2
    c.line(cx_nord, y, cx_nord, y - 5 * mm)
    c.line(cx_nord, y, cx_nord - 1.8 * mm, y - 2.2 * mm)
    c.line(cx_nord, y, cx_nord + 1.8 * mm, y - 2.2 * mm)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(NOIR)
    c.drawCentredString(cx_nord, y + 1.5 * mm, "N")
    y -= 9 * mm

    titre_foncier = parcelle.numero_titre_foncier or "-"
    parcelle_label = parcelle.numero_parcelle or parcelle.nicad
    zone_label = parcelle.zone.nom if parcelle.zone_id else ""

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largeur / 2, y, "PLAN POUR AUTORISATION DE CONSTRUIRE")
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    c.drawCentredString(largeur / 2, y, "Mt du Titre Foncier {}/DP".format(titre_foncier))
    y -= 5 * mm
    libelle_lot = "Lot n° {}".format(parcelle_label)
    if zone_label:
        libelle_lot += " ({})".format(zone_label)
    c.drawCentredString(largeur / 2, y, libelle_lot)
    y -= 5 * mm
    c.drawCentredString(largeur / 2, y, "Superficie = {}".format(_format_superficie_are_ca(parcelle.superficie)))
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(largeur / 2, y, "NICAD : {}".format(parcelle.nicad))
    y -= 8 * mm

    c.setStrokeColor(GRIS)
    c.setLineWidth(0.4)
    c.line(marge, y, largeur - marge, y)
    y -= 6 * mm

    taille_plan = min(largeur - 2 * marge, 135 * mm)
    echelle_texte = "-"
    try:
        voisines = _voisines_parcelle(parcelle)
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

    c.setFont("Helvetica", 8.5)
    c.setFillColor(NOIR)
    c.drawString(marge, y, "A Keur Massar Nord, le {}".format(timezone.now().strftime("%d/%m/%Y")))
    y -= 5 * mm
    c.drawString(marge, y, "Numéro : {}/{}".format(numero_doc, timezone.now().strftime("%d-%m-%Y")))

    c.setFont("Helvetica", 8.5)
    c.drawRightString(largeur - marge, y + 5 * mm, "Echelle = {}".format(echelle_texte))

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(largeur - marge, y, "Le Chef du Bureau du Cadastre")
    y -= 14 * mm
    c.setStrokeColor(GRIS)
    c.setLineWidth(0.4)
    c.line(largeur - marge - 55 * mm, y, largeur - marge, y)
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(GRIS)
    c.drawRightString(largeur - marge, y - 4 * mm, "Cachet et signature")

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NOIR)
    c.drawCentredString(largeur / 2, y, "Ce plan ne constitue pas un titre de propriété")

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
print("OK : extrait de plan foncier refait sur le modele officiel (en-tete, encadre, cotes, reperes B1..Bn).")
print("-> Rechargez la page et retelechargez le PDF pour voir le resultat.")