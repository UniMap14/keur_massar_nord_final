# -*- coding: utf-8 -*-
"""
Remplace _voisines_parcelle par une vraie requete spatiale PostGIS
(intersection reelle, rayon adapte a la taille de la parcelle) au lieu
de l'approximation par 600 premieres parcelles triees par ID -- qui
ratait les vrais voisins sur une base a ~40 000 parcelles.

Ajoute aussi _texte_pdf, qui nettoie les valeurs avant de les ecrire
dans le PDF (evite les caracteres corrompus issus de donnees importees
du shapefile), et l'applique aux champs textuels des encadres.

Idempotent.
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

if "geom__intersects" in contenu and "_texte_pdf" in contenu:
    print("Deja applique, rien a faire.")
else:
    ancre_debut = "def _voisines_parcelle(parcelle, rayon_m=70, max_resultats=25):"
    ancre_fin = "def _pas_grille_adapte(etendue_m):"
    i1 = contenu.find(ancre_debut)
    i2 = contenu.find(ancre_fin)
    if i1 == -1 or i2 == -1 or i2 < i1:
        raise SystemExit("ANCRES INTROUVABLES - abandon, rien n'a ete modifie.")

    nouveau_bloc = '''def _voisines_parcelle(parcelle, max_resultats=30):
    """Vraies parcelles voisines de `parcelle`, trouvees par
    intersection spatiale reelle via PostGIS (index spatial, donc
    rapide meme sur des dizaines de milliers de parcelles). Le rayon
    de recherche s'adapte a la taille de la parcelle : une tres grande
    parcelle regarde plus loin pour trouver du contexte autour d'elle."""
    from .models import Parcelle

    xmin, ymin, xmax, ymax = parcelle.geom.extent
    x1, y1 = _wgs84_to_utm28n(xmin, ymin)
    x2, y2 = _wgs84_to_utm28n(xmax, ymax)
    largeur_m = abs(x2 - x1)
    hauteur_m = abs(y2 - y1)
    rayon_m = max(60.0, 0.55 * max(largeur_m, hauteur_m))
    rayon_m = min(rayon_m, 350.0)
    tampon_deg = rayon_m / 111320.0

    try:
        zone_recherche = parcelle.geom.buffer(tampon_deg)
        voisines = list(
            Parcelle.objects.filter(geom__intersects=zone_recherche)
            .exclude(pk=parcelle.pk)
            .only("id", "nicad", "numero_parcelle", "geom")[:max_resultats]
        )
    except Exception:
        voisines = []
    return voisines


def _texte_pdf(valeur, max_longueur=60):
    """Nettoie une valeur avant de l'ecrire dans le PDF : retire les
    caracteres non imprimables issus de donnees importees (shapefile,
    saisie libre) qui corrompraient l'affichage."""
    if valeur in (None, ""):
        return "-"
    texte = str(valeur)
    accents_ok = "\\u00e0\\u00e2\\u00e4\\u00e9\\u00e8\\u00ea\\u00eb\\u00ee\\u00ef\\u00f4\\u00f6\\u00f9\\u00fb\\u00fc\\u00e7\\u00c0\\u00c2\\u00c4\\u00c9\\u00c8\\u00ca\\u00cb\\u00ce\\u00cf\\u00d4\\u00d6\\u00d9\\u00db\\u00dc\\u00c7\\u00b0\\u00b2"
    propre = []
    for ch in texte:
        if 32 <= ord(ch) <= 126 or ch in accents_ok:
            propre.append(ch)
    texte = "".join(propre).strip()
    return texte[:max_longueur] if texte else "-"


'''
    contenu = contenu[:i1] + nouveau_bloc + contenu[i2:]

    contenu = contenu.replace(
        "c.drawRightString(x_gauche + largeur_col - 2 * mm, yc, str(valeur)[:40])",
        "c.drawRightString(x_gauche + largeur_col - 2 * mm, yc, _texte_pdf(valeur, 40))",
    )
    contenu = contenu.replace(
        "c.drawRightString(x_droite + largeur_col - 2 * mm, yc, str(valeur)[:36])",
        "c.drawRightString(x_droite + largeur_col - 2 * mm, yc, _texte_pdf(valeur, 36))",
    )

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")
    print("Nouvelle longueur du fichier :", len(contenu), "caracteres")