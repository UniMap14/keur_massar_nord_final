CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_1 = '''        infra_par_parcelle = {}
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

nouveau_1 = '''        infra_par_parcelle = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            details_publics = {k: v for k, v in (infra.details or {}).items() if k != "Nombre d'employés"}
            infra_par_parcelle.setdefault(infra.parcelle_id, []).append({
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": details_publics,
            })'''

if nouveau_1 in contenu:
    print("DEJA FAIT : bloc 1 (infra_par_parcelle) deja corrige.")
elif ancien_1 in contenu:
    contenu = contenu.replace(ancien_1, nouveau_1, 1)
    changements += 1
    print("OK : nombre d'employes masque dans infra_par_parcelle (public).")
else:
    print("ERREUR : ancre bloc 1 introuvable.")

ancien_2 = '''        infra_sans_parcelle = [
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

nouveau_2 = '''        infra_sans_parcelle = [
            {
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": {k: v for k, v in (infra.details or {}).items() if k != "Nombre d'employés"},
            }
            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True).select_related("categorie")
        ]'''

if nouveau_2 in contenu:
    print("DEJA FAIT : bloc 2 (infra_sans_parcelle) deja corrige.")
elif ancien_2 in contenu:
    contenu = contenu.replace(ancien_2, nouveau_2, 1)
    changements += 1
    print("OK : nombre d'employes masque dans infra_sans_parcelle (public).")
else:
    print("ERREUR : ancre bloc 2 introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")