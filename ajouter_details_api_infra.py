CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_public = '''        infra_par_parcelle = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle.setdefault(infra.parcelle_id, []).append({
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
            })'''

nouveau_public = '''        infra_par_parcelle = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle.setdefault(infra.parcelle_id, []).append({
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            })'''

if nouveau_public in contenu:
    print("DEJA FAIT : vue publique deja mise a jour.")
elif ancien_public in contenu:
    contenu = contenu.replace(ancien_public, nouveau_public, 1)
    changements += 1
    print("OK : sous_type et details ajoutes a la vue publique.")
else:
    print("ERREUR : bloc vue publique introuvable.")

ancien_admin = '''        infra_par_parcelle_admin = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append({
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
            })'''

nouveau_admin = '''        infra_par_parcelle_admin = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
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

if nouveau_admin in contenu:
    print("DEJA FAIT : vue admin deja mise a jour.")
elif ancien_admin in contenu:
    contenu = contenu.replace(ancien_admin, nouveau_admin, 1)
    changements += 1
    print("OK : sous_type et details ajoutes a la vue admin.")
else:
    print("ERREUR : bloc vue admin introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")