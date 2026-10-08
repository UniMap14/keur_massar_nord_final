CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_public = '''        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .select_related("zone")
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "occupation_sol", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier",
                "zone__nom",
            )
            .order_by("id")
        )'''

nouveau_public = '''        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .filter(parcelle_active=True)
            .select_related("zone")
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "occupation_sol", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier",
                "zone__nom",
            )
            .order_by("id")
        )'''

if nouveau_public in contenu:
    print("DEJA FAIT : vue publique deja filtree.")
elif ancien_public in contenu:
    contenu = contenu.replace(ancien_public, nouveau_public, 1)
    changements += 1
    print("OK : vue publique filtree sur parcelle_active=True.")
else:
    print("ERREUR : bloc vue publique introuvable.")

ancien_admin = '''        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .select_related("zone", "proprietaire")
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))'''

nouveau_admin = '''        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .filter(parcelle_active=True)
            .select_related("zone", "proprietaire")
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))'''

if nouveau_admin in contenu:
    print("DEJA FAIT : vue admin deja filtree.")
elif ancien_admin in contenu:
    contenu = contenu.replace(ancien_admin, nouveau_admin, 1)
    changements += 1
    print("OK : vue admin filtree sur parcelle_active=True.")
else:
    print("ERREUR : bloc vue admin introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")