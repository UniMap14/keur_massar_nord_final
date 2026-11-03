# -*- coding: utf-8 -*-
"""
Le logo DGID contient deja le texte "Direction Generale des Impots et
des Domaines" integre dans l'image -- le texte redessine a cote faisait
donc doublon. On le supprime et on agrandit le logo a la place.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_logo_sans_texte.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "y_logo_haut"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

ancre = '''    taille_logo = 6.5 * mm
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

remplacement = '''    # Le logo contient deja le texte "Direction Generale des Impots et
    # des Domaines" -- pas besoin de le redessiner a cote.
    taille_logo = 11 * mm
    x_logo = marge
    y_logo_haut = y - 10.5 * mm
    try:
        from django.contrib.staticfiles import finders
        chemin_logo = finders.find("foncier/img/logo-dgid.png")
        if chemin_logo:
            logo_img = ImageReader(chemin_logo)
            largeur_logo_native, hauteur_logo_native = logo_img.getSize()
            largeur_logo = taille_logo * (largeur_logo_native / hauteur_logo_native)
            c.drawImage(
                logo_img, x_logo, y_logo_haut - taille_logo,
                width=largeur_logo, height=taille_logo,
                preserveAspectRatio=True, mask="auto",
            )
    except Exception:
        pass'''

if ancre not in contenu:
    raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")
if contenu.count(ancre) != 1:
    raise SystemExit("ANCRE trouvee plusieurs fois - abandon par securite.")

contenu = contenu.replace(ancre, remplacement)

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : texte en double supprime, logo agrandi.")