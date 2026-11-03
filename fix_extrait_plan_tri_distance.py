# -*- coding: utf-8 -*-
"""
Corrige _voisines_parcelle : quand il y a beaucoup de parcelles dans le
rayon de recherche (ex: 975 a 500m), le decoupage [:max_resultats] sans
tri prenait un sous-ensemble arbitraire (ordre de la base), pas
forcement les plus proches -- d'ou un plan avec des "trous" et des
parcelles eparpillees de maniere incoherente. On trie maintenant par
distance reelle a la parcelle, pour garder toujours les plus proches.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_tri_distance.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "from django.contrib.gis.db.models.functions import Distance as _DistanceVoisines"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

PATCHES = []

PATCHES.append((
    "rayon : revenir a un plafond raisonnable, le tri par distance fait le reste",
    "    rayon_m = max(140.0, 0.9 * max(largeur_m, hauteur_m))\n"
    "    rayon_m = min(rayon_m, 650.0)\n",
    "    rayon_m = max(140.0, 0.9 * max(largeur_m, hauteur_m))\n"
    "    rayon_m = min(rayon_m, 500.0)\n",
))

PATCHES.append((
    "tri par distance reelle avant de couper a max_resultats",
    "    try:\n"
    "        zone_recherche = parcelle.geom.buffer(tampon_deg)\n"
    "        voisines = list(\n"
    "            Parcelle.objects.filter(geom__intersects=zone_recherche)\n"
    "            .exclude(pk=parcelle.pk)\n"
    "            .only(\"id\", \"nicad\", \"numero_parcelle\", \"geom\")[:max_resultats]\n"
    "        )\n"
    "    except Exception:\n"
    "        voisines = []\n"
    "    return voisines",
    "    try:\n"
    "        from django.contrib.gis.db.models.functions import Distance as _DistanceVoisines\n"
    "        zone_recherche = parcelle.geom.buffer(tampon_deg)\n"
    "        voisines = list(\n"
    "            Parcelle.objects.filter(geom__intersects=zone_recherche)\n"
    "            .exclude(pk=parcelle.pk)\n"
    "            .annotate(_distance_voisine=_DistanceVoisines(\"geom\", parcelle.geom))\n"
    "            .order_by(\"_distance_voisine\")\n"
    "            .only(\"id\", \"nicad\", \"numero_parcelle\", \"geom\")[:max_resultats]\n"
    "        )\n"
    "    except Exception:\n"
    "        voisines = []\n"
    "    return voisines",
))

PATCHES.append((
    "nombre de voisines demande par l'extrait de plan : revenir a une valeur lisible",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=320)\n",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=180)\n",
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
print("OK : parcelles voisines triees par distance reelle + densite ajustee.")