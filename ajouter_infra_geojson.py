CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_public = '''        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "numero_parcelle": parcelle.numero_parcelle,
                    "numero_lot": parcelle.numero_lot,
                    "section_cadastrale": parcelle.section_cadastrale,
                    "numero_titre_foncier": parcelle.numero_titre_foncier,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "occupation_sol": parcelle.occupation_sol,
                    "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                },
            }'''

nouveau_public = '''        infra_par_parcelle = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle.setdefault(infra.parcelle_id, []).append(
                {"nom": infra.nom, "categorie": infra.categorie.label}
            )

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "numero_parcelle": parcelle.numero_parcelle,
                    "numero_lot": parcelle.numero_lot,
                    "section_cadastrale": parcelle.section_cadastrale,
                    "numero_titre_foncier": parcelle.numero_titre_foncier,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "occupation_sol": parcelle.occupation_sol,
                    "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                    "infrastructures": infra_par_parcelle.get(parcelle.id, []),
                },
            }'''

if "infra_par_parcelle" in contenu.split("def api_parcelles_toutes_geojson_admin")[0]:
    print("DEJA FAIT : vue publique deja modifiee.")
elif ancien_public in contenu:
    contenu = contenu.replace(ancien_public, nouveau_public, 1)
    changements += 1
    print("OK : infrastructures ajoutees a la vue publique.")
else:
    print("ERREUR : bloc de la vue publique introuvable.")

ancien_admin = '''        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "id": parcelle.id,
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                    "valeur_locative": float(parcelle.valeur_locative),
                    "statut_fiscal": parcelle.statut_fiscal,
                    "type_document": parcelle.type_document,
                    "reference_arrete": parcelle.reference_arrete,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
                    "occupation_sol": parcelle.occupation_sol,'''

nouveau_admin = '''        infra_par_parcelle_admin = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append(
                {"nom": infra.nom, "categorie": infra.categorie.label}
            )

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "id": parcelle.id,
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                    "valeur_locative": float(parcelle.valeur_locative),
                    "statut_fiscal": parcelle.statut_fiscal,
                    "type_document": parcelle.type_document,
                    "reference_arrete": parcelle.reference_arrete,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
                    "occupation_sol": parcelle.occupation_sol,
                    "infrastructures": infra_par_parcelle_admin.get(parcelle.id, []),'''

if "infra_par_parcelle_admin" in contenu:
    print("DEJA FAIT : vue admin deja modifiee.")
elif ancien_admin in contenu:
    contenu = contenu.replace(ancien_admin, nouveau_admin, 1)
    changements += 1
    print("OK : infrastructures ajoutees a la vue admin.")
else:
    print("ERREUR : bloc de la vue admin introuvable.")

if "from .models import (" in contenu and "Infrastructure," not in contenu.split("from .models import (")[1].split(")")[0]:
    contenu = contenu.replace(
        "    Actualite,\n)",
        "    Actualite,\n    Infrastructure,\n)",
        1,
    )
    changements += 1
    print("OK : import Infrastructure ajoute.")
else:
    print("Import Infrastructure : deja present ou non necessaire.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")