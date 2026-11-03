# -*- coding: utf-8 -*-
"""
Les numeros de parcelles debordaient encore un peu : l'ancienne methode
estimait la taille de police a partir d'un simple facteur sur la boite
de la parcelle (sans tenir compte du nombre de chiffres du numero), ce
qui pouvait deborder pour les numeros a 5 chiffres. On mesure
maintenant la taille REELLE du texte rendu (draw.textbbox) et on
cherche la plus grande police qui tient vraiment dans la parcelle,
chiffre par chiffre.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_texte_mesure.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "_ajuster_texte_dans_boite"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

PATCHES = []

# 1) Ajoute la fonction de mesure juste apres _police_adaptee.
PATCHES.append((
    "ajout de la fonction de mesure du texte",
    '    def _police_adaptee(taille_cible):\n'
    '        taille_cible = max(6, min(26, int(taille_cible)))\n'
    '        if taille_cible not in cache_polices:\n'
    '            try:\n'
    '                cache_polices[taille_cible] = ImageFont.load_default(size=taille_cible)\n'
    '            except TypeError:\n'
    '                cache_polices[taille_cible] = ImageFont.load_default()\n'
    '        return cache_polices[taille_cible]\n',
    '    def _police_adaptee(taille_cible):\n'
    '        taille_cible = max(6, min(26, int(taille_cible)))\n'
    '        if taille_cible not in cache_polices:\n'
    '            try:\n'
    '                cache_polices[taille_cible] = ImageFont.load_default(size=taille_cible)\n'
    '            except TypeError:\n'
    '                cache_polices[taille_cible] = ImageFont.load_default()\n'
    '        return cache_polices[taille_cible]\n'
    '\n'
    '    def _ajuster_texte_dans_boite(texte, largeur_max, hauteur_max, taille_min=7, taille_max=26):\n'
    '        """Cherche la plus grande taille de police (mesuree reellement,\n'
    '        pas estimee) qui fait tenir `texte` dans une boite de\n'
    '        largeur_max x hauteur_max px, avec une petite marge de securite.\n'
    '        Renvoie None si meme la plus petite taille deborde encore."""\n'
    '        largeur_cible = largeur_max * 0.86\n'
    '        hauteur_cible = hauteur_max * 0.86\n'
    '        for taille in range(taille_max, taille_min - 1, -1):\n'
    '            police = _police_adaptee(taille)\n'
    '            boite = draw.textbbox((0, 0), texte, font=police)\n'
    '            larg = boite[2] - boite[0]\n'
    '            haut = boite[3] - boite[1]\n'
    '            if larg <= largeur_cible and haut <= hauteur_cible:\n'
    '                return police\n'
    '        return None\n',
))

# 2) Numeros des parcelles voisines : utiliser la mesure reelle.
PATCHES.append((
    "numeros des parcelles voisines mesures",
    '            taille_police_v = min(largeur_bbox, hauteur_bbox) * 0.32\n'
    '            if taille_police_v >= 7:\n'
    '                etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else "?")\n'
    '                draw.text(\n'
    '                    (centre_x, centre_y), str(etiquette), fill=(30, 30, 30),\n'
    '                    font=_police_adaptee(taille_police_v), anchor="mm",\n'
    '                )\n',
    '            etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else "?")\n'
    '            police_voisine = _ajuster_texte_dans_boite(str(etiquette), largeur_bbox, hauteur_bbox)\n'
    '            if police_voisine is not None:\n'
    '                draw.text(\n'
    '                    (centre_x, centre_y), str(etiquette), fill=(30, 30, 30),\n'
    '                    font=police_voisine, anchor="mm",\n'
    '                )\n',
))

# 3) Numero de la parcelle principale : idem.
PATCHES.append((
    "numero de la parcelle principale mesure",
    '        xs_p = [p[0] for p in pts_px]\n'
    '        ys_p = [p[1] for p in pts_px]\n'
    '        taille_police_p = max(10, min(max(xs_p) - min(xs_p), max(ys_p) - min(ys_p)) * 0.3)\n'
    '        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")\n'
    '        draw.text(\n'
    '            (centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15),\n'
    '            font=_police_adaptee(taille_police_p), anchor="mm",\n'
    '        )\n',
    '        xs_p = [p[0] for p in pts_px]\n'
    '        ys_p = [p[1] for p in pts_px]\n'
    '        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")\n'
    '        police_principale = _ajuster_texte_dans_boite(\n'
    '            str(etiquette_principale), max(xs_p) - min(xs_p), max(ys_p) - min(ys_p),\n'
    '            taille_min=8, taille_max=28,\n'
    '        ) or _police_adaptee(8)\n'
    '        draw.text(\n'
    '            (centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15),\n'
    '            font=police_principale, anchor="mm",\n'
    '        )\n',
))

erreurs = []
for nom, ancre, remplacement in PATCHES:
    if ancre not in contenu:
        erreurs.append(f"- ancre introuvable pour « {nom} »")
        continue
    if contenu.count(ancre) != 1:
        erreurs.append(f"- ancre « {nom} » trouvee {contenu.count(ancre)} fois (attendu 1)")
        continue
    contenu = contenu.replace(ancre, remplacement)

if erreurs:
    print("ERREUR : certains blocs n'ont pas pu etre localises tels quels :")
    for e in erreurs:
        print(e)
    raise SystemExit("Aucun fichier n'a ete modifie (securite : tout ou rien).")

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : les numeros de parcelles sont maintenant mesures reellement avant d'etre dessines.")