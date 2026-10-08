CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- Bloc 1 : infrastructures rattachees a une parcelle (admin) ---
ancien1 = '''        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append({
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            })'''

nouveau1 = '''        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append({
                "id": infra.id,
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            })'''

if '"id": infra.id,\n                "nom": infra.nom,\n                "categorie": infra.categorie.label,\n                "icone": infra.categorie.icone,\n                "couleur": infra.categorie.couleur,\n                "latitude": infra.latitude,\n                "longitude": infra.longitude,\n                "sous_type": infra.sous_type,\n                "details": infra.details,\n            })' in contenu:
    resultats.append("IGNORE : bloc 1 (avec parcelle) deja mis a jour.")
elif ancien1 in contenu:
    contenu = contenu.replace(ancien1, nouveau1, 1)
    resultats.append("OK : id ajoute au bloc infrastructures avec parcelle (admin).")
else:
    resultats.append("ERREUR : bloc 1 introuvable.")

# --- Bloc 2 : infrastructures sans parcelle (admin) ---
ancien2 = '''        infra_sans_parcelle_admin = [
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
        ]'''

nouveau2 = '''        infra_sans_parcelle_admin = [
            {
                "id": infra.id,
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
        ]'''

if '"id": infra.id,\n                "nom": infra.nom,\n                "categorie": infra.categorie.label,\n                "icone": infra.categorie.icone,\n                "couleur": infra.categorie.couleur,\n                "latitude": infra.latitude,\n                "longitude": infra.longitude,\n                "sous_type": infra.sous_type,\n                "details": infra.details,\n            }\n            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True)' in contenu:
    resultats.append("IGNORE : bloc 2 (sans parcelle) deja mis a jour.")
elif ancien2 in contenu:
    contenu = contenu.replace(ancien2, nouveau2, 1)
    resultats.append("OK : id ajoute au bloc infrastructures sans parcelle (admin).")
else:
    resultats.append("ERREUR : bloc 2 introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))