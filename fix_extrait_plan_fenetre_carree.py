# -*- coding: utf-8 -*-
"""
Corrige la cause reelle des coins vides dans le plan : _voisines_parcelle
cherchait les parcelles dans un CERCLE (parcelle.geom.buffer(...)) autour
de la parcelle, alors que le plan est dessine dans un CARRE -- les 4
coins du carre sont donc mecaniquement vides (le cercle ne les touche
pas), meme s'il y a de vraies parcelles a ces endroits. On remplace le
cercle par une vraie fenetre carree (bbox etendue), et on augmente un
peu la densite.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_fenetre_carree.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

PATCHES.append((
    "fenetre de recherche carree au lieu d'un cercle",
    "    try:\n"
    "        from django.contrib.gis.db.models.functions import Distance as _DistanceVoisines\n"
    "        zone_recherche = parcelle.geom.buffer(tampon_deg)\n"
    "        voisines = list(\n",
    "    try:\n"
    "        from django.contrib.gis.db.models.functions import Distance as _DistanceVoisines\n"
    "        from django.contrib.gis.geos import Polygon as _PolygonVoisines\n"
    "        _xmin, _ymin, _xmax, _ymax = parcelle.geom.extent\n"
    "        zone_recherche = _PolygonVoisines.from_bbox((\n"
    "            _xmin - tampon_deg, _ymin - tampon_deg,\n"
    "            _xmax + tampon_deg, _ymax + tampon_deg,\n"
    "        ))\n"
    "        zone_recherche.srid = parcelle.geom.srid\n"
    "        voisines = list(\n",
))

PATCHES.append((
    "un peu plus de densite, la fenetre carree remplit mieux les coins",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=120)\n",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=160)\n",
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
print("OK : recherche en fenetre carree (plus de coins vides) + densite augmentee.")