CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_pub = '''        data = {"type": "FeatureCollection", "features": features}
        cache.set(CACHE_KEY_PUBLIC, data, None)  # pas d'expiration : invalidé par le signal'''

nouveau_pub = '''        infra_sans_parcelle = [
            {
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            }
            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True).select_related("categorie")
        ]

        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle}
        cache.set(CACHE_KEY_PUBLIC, data, None)  # pas d'expiration : invalidé par le signal'''

if "infra_sans_parcelle = [" in contenu:
    print("DEJA FAIT : vue publique deja mise a jour.")
elif ancien_pub in contenu:
    contenu = contenu.replace(ancien_pub, nouveau_pub, 1)
    changements += 1
    print("OK : infrastructures sans parcelle ajoutees a la vue publique.")
else:
    print("ERREUR : bloc vue publique introuvable.")

ancien_admin = '''        data = {"type": "FeatureCollection", "features": features}
        cache.set(CACHE_KEY_ADMIN, data, None)'''

nouveau_admin = '''        infra_sans_parcelle_admin = [
            {
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            }
            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True).select_related("categorie")
        ]

        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle_admin}
        cache.set(CACHE_KEY_ADMIN, data, None)'''

if "infra_sans_parcelle_admin = [" in contenu:
    print("DEJA FAIT : vue admin deja mise a jour.")
elif ancien_admin in contenu:
    contenu = contenu.replace(ancien_admin, nouveau_admin, 1)
    changements += 1
    print("OK : infrastructures sans parcelle ajoutees a la vue admin.")
else:
    print("ERREUR : bloc vue admin introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")