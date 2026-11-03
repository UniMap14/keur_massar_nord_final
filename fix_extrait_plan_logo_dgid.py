# -*- coding: utf-8 -*-
"""
Ajoute un petit pictogramme (icone de batiment, style generique) a
gauche de "DIRECTION GENERALE DES IMPOTS ET DES DOMAINES" dans l'en-tete
de l'extrait de plan, et colore cette ligne en marron/rouge, comme sur
le modele officiel.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_logo_dgid.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "MARRON_DGID"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

ancre = '''    c.setFont("Helvetica", 7)
    c.drawString(marge, y - 13 * mm, "DIRECTION GENERALE DES IMPOTS ET DES DOMAINES")
    c.setFillColor(GRIS)
    c.drawString(marge, y - 17 * mm, "Centre des Services Fiscaux de Keur Massar")
    c.drawString(marge, y - 21 * mm, "Bureau du Cadastre")'''

remplacement = '''    MARRON_DGID = HexColor("#8b1a1a")
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
    c.drawString(marge + taille_logo + 1.5 * mm, y - 15 * mm, "DES IMPOTS ET DES DOMAINES")
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 7)
    c.drawString(marge, y - 19.5 * mm, "Centre des Services Fiscaux de Keur Massar")
    c.drawString(marge, y - 23.5 * mm, "Bureau du Cadastre")'''

if ancre not in contenu:
    raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")
if contenu.count(ancre) != 1:
    raise SystemExit("ANCRE trouvee plusieurs fois - abandon par securite.")

contenu = contenu.replace(ancre, remplacement)

# Les lignes qui suivaient l'en-tete descendaient de 27mm avant --
# l'en-tete est maintenant un peu plus haut (logo sur 2 lignes), on
# ajuste le decalage vertical d'autant pour ne pas chevaucher la suite.
ancre_decalage = "    y -= 27 * mm\n"
remplacement_decalage = "    y -= 29.5 * mm\n"
if ancre_decalage not in contenu:
    raise SystemExit("ANCRE (decalage) introuvable - abandon, rien n'a ete modifie.")
if contenu.count(ancre_decalage) != 1:
    raise SystemExit("ANCRE (decalage) trouvee plusieurs fois - abandon par securite.")
contenu = contenu.replace(ancre_decalage, remplacement_decalage)

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : logo DGID (pictogramme) ajoute, en-tete colore en marron.")