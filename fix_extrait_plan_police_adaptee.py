# -*- coding: utf-8 -*-
"""
Corrige la lisibilite du plan de l'extrait de plan :
1) Reduit le nombre de parcelles voisines affichees (zoom plus serre,
   comme sur le modele), pour que chaque parcelle soit assez grande.
2) Reduit la marge autour du dessin (moins d'espace perdu).
3) Rend la taille du texte (numero de parcelle) adaptative a la taille
   reelle de chaque parcelle a l'ecran, pour ne plus jamais deborder --
   et n'affiche pas de numero si la parcelle est vraiment trop petite
   pour le contenir proprement (comme sur une vraie carte).

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_police_adaptee.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "_police_adaptee"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

PATCHES = []

# 1) Moins de voisines demandees depuis l'extrait de plan.
PATCHES.append((
    "nombre de voisines demande",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=180)\n",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=70)\n",
))

# 2) Marge plus serree autour du dessin.
PATCHES.append((
    "marge autour du dessin",
    "    etendue_brute = max(xmax - xmin, ymax - ymin, 10.0)\n"
    "    marge_m = etendue_brute * 0.22 + 6\n",
    "    etendue_brute = max(xmax - xmin, ymax - ymin, 10.0)\n"
    "    marge_m = etendue_brute * 0.12 + 4\n",
))

# 3) Numeros des parcelles voisines : taille adaptee a la parcelle, et
#    pas de numero si la parcelle est trop petite a l'echelle du plan.
PATCHES.append((
    "numeros des parcelles voisines adaptatifs",
    "    # Parcelles voisines : trait fin noir + numero au centre.\n"
    "    for voisine, pts in polygones_voisins:\n"
    "        pts_px = [vers_px(px, py) for px, py in pts]\n"
    "        if len(pts_px) >= 2:\n"
    "            draw.polygon(pts_px, outline=(40, 40, 40), width=2)\n"
    "            centre_x = sum(p[0] for p in pts_px) / len(pts_px)\n"
    "            centre_y = sum(p[1] for p in pts_px) / len(pts_px)\n"
    "            etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else \"?\")\n"
    "            draw.text((centre_x, centre_y), str(etiquette), fill=(30, 30, 30), font=police_label, anchor=\"mm\")\n",
    "    # Parcelles voisines : trait fin noir + numero au centre, avec une\n"
    "    # taille de police adaptee a la taille reelle de chaque parcelle a\n"
    "    # l'ecran (pour ne jamais deborder), et pas de numero du tout si la\n"
    "    # parcelle est trop petite pour l'accueillir proprement.\n"
    "    cache_polices = {}\n\n"
    "    def _police_adaptee(taille_cible):\n"
    "        taille_cible = max(6, min(26, int(taille_cible)))\n"
    "        if taille_cible not in cache_polices:\n"
    "            try:\n"
    "                cache_polices[taille_cible] = ImageFont.load_default(size=taille_cible)\n"
    "            except TypeError:\n"
    "                cache_polices[taille_cible] = ImageFont.load_default()\n"
    "        return cache_polices[taille_cible]\n\n"
    "    for voisine, pts in polygones_voisins:\n"
    "        pts_px = [vers_px(px, py) for px, py in pts]\n"
    "        if len(pts_px) >= 2:\n"
    "            draw.polygon(pts_px, outline=(40, 40, 40), width=2)\n"
    "            xs_v = [p[0] for p in pts_px]\n"
    "            ys_v = [p[1] for p in pts_px]\n"
    "            largeur_bbox = max(xs_v) - min(xs_v)\n"
    "            hauteur_bbox = max(ys_v) - min(ys_v)\n"
    "            centre_x = sum(xs_v) / len(pts_px)\n"
    "            centre_y = sum(ys_v) / len(pts_px)\n"
    "            taille_police_v = min(largeur_bbox, hauteur_bbox) * 0.32\n"
    "            if taille_police_v >= 7:\n"
    "                etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else \"?\")\n"
    "                draw.text(\n"
    "                    (centre_x, centre_y), str(etiquette), fill=(30, 30, 30),\n"
    "                    font=_police_adaptee(taille_police_v), anchor=\"mm\",\n"
    "                )\n",
))

# 4) Numero de la parcelle principale : meme logique adaptative.
PATCHES.append((
    "numero de la parcelle principale adaptatif",
    '        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")\n'
    '        draw.text((centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15), font=police_num, anchor="mm")\n',
    '        xs_p = [p[0] for p in pts_px]\n'
    '        ys_p = [p[1] for p in pts_px]\n'
    '        taille_police_p = max(10, min(max(xs_p) - min(xs_p), max(ys_p) - min(ys_p)) * 0.3)\n'
    '        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")\n'
    '        draw.text(\n'
    '            (centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15),\n'
    '            font=_police_adaptee(taille_police_p), anchor="mm",\n'
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
print("OK : plan plus serre + numeros a taille adaptee a chaque parcelle.")