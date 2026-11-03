# -*- coding: utf-8 -*-
"""
Remplace le pictogramme "batiment" dessine a la main par le vrai logo
DGID deja present dans le projet (foncier/static/foncier/img/logo-dgid.png),
le meme que celui utilise dans le footer du site public.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_vrai_logo_dgid.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "logo-dgid.png"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

ancre = '''    MARRON_DGID = HexColor("#8b1a1a")
    taille_logo = 5 * mm
    x_logo = marge
    y_logo = y - 15.3 * mm
    c.saveState()
    c.setFillColor(MARRON_DGID)
    chemin_toit = c.beginPath()
    chemin_toit.moveTo(x_logo, y_logo)
    chemin_toit.lineTo(x_logo + taille_logo / 2, y_logo + taille_logo * 0.65)
    chemin_toit.lineTo(x_logo + taille_logo, y_logo)
    chemin_toit.close()
    c.drawPath(chemin_toit, fill=1, stroke=0)
    c.rect(
        x_logo + taille_logo * 0.1, y_logo - taille_logo * 0.55,
        taille_logo * 0.8, taille_logo * 0.55, fill=1, stroke=0,
    )
    c.setFillColor(HexColor("#ffffff"))
    c.rect(
        x_logo + taille_logo * 0.4, y_logo - taille_logo * 0.4,
        taille_logo * 0.2, taille_logo * 0.3, fill=1, stroke=0,
    )
    c.restoreState()

    c.setFillColor(MARRON_DGID)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(marge + taille_logo + 1.5 * mm, y - 12.2 * mm, "DIRECTION GENERALE")
    c.drawString(marge + taille_logo + 1.5 * mm, y - 15 * mm, "DES IMPOTS ET DES DOMAINES")'''

remplacement = '''    taille_logo = 6.5 * mm
    x_logo = marge
    y_logo = y - 15.3 * mm
    try:
        from django.contrib.staticfiles import finders
        chemin_logo = finders.find("foncier/img/logo-dgid.png")
        if chemin_logo:
            logo_img = ImageReader(chemin_logo)
            largeur_logo_native, hauteur_logo_native = logo_img.getSize()
            largeur_logo = taille_logo * (largeur_logo_native / hauteur_logo_native)
            c.drawImage(
                logo_img, x_logo, y_logo - taille_logo * 0.55,
                width=largeur_logo, height=taille_logo,
                preserveAspectRatio=True, mask="auto",
            )
        else:
            largeur_logo = 0
    except Exception:
        largeur_logo = 0

    c.setFillColor(NOIR)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(marge + largeur_logo + (2 * mm if largeur_logo else 0), y - 12.2 * mm, "DIRECTION GENERALE")
    c.drawString(marge + largeur_logo + (2 * mm if largeur_logo else 0), y - 15 * mm, "DES IMPOTS ET DES DOMAINES")'''

if ancre not in contenu:
    raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")
if contenu.count(ancre) != 1:
    raise SystemExit("ANCRE trouvee plusieurs fois - abandon par securite.")

contenu = contenu.replace(ancre, remplacement)

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : vrai logo DGID (logo-dgid.png) utilise dans l'en-tete de l'extrait de plan.")