# -*- coding: utf-8 -*-
"""
Modifie carte_geoportail pour transmettre la/les parcelle(s) du
citoyen connecte (si son compte est relie a un NICAD existant), afin
que "Me geolocaliser" puisse l'afficher et calculer la distance.

Idempotent.
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "mes_parcelles_geojson"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    ancien = '''def carte_geoportail(request):
    """Affiche la page publique du g\u00e9oportail (aucune donn\u00e9e fiscale)."""
    return render(request, "foncier/geoportail.html")'''

    if ancien not in contenu:
        raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau = '''def carte_geoportail(request):
    """Affiche la page publique du geoportail (aucune donnee fiscale).
    Si le visiteur est un citoyen connecte dont le compte est relie a
    une parcelle (NICAD existant), celle-ci est transmise au template
    pour que "Me geolocaliser" puisse indiquer sa zone et la distance
    jusqu'a sa propre parcelle."""
    import json
    from .models import Parcelle

    mes_parcelles_geojson = None
    citoyen = getattr(request.user, "citoyen", None) if request.user.is_authenticated else None
    if citoyen is not None and citoyen.numero_foncier:
        parcelles = Parcelle.objects.filter(nicad=citoyen.numero_foncier)
        features = []
        for p in parcelles:
            try:
                geometrie = json.loads(p.geom.geojson)
            except Exception:
                continue
            features.append({
                "type": "Feature",
                "geometry": geometrie,
                "properties": {"nicad": p.nicad, "adresse": p.adresse_parcelle},
            })
        if features:
            mes_parcelles_geojson = json.dumps({"type": "FeatureCollection", "features": features})

    return render(request, "foncier/geoportail.html", {
        "mes_parcelles_geojson": mes_parcelles_geojson,
    })'''

    contenu = contenu.replace(ancien, nouveau)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")