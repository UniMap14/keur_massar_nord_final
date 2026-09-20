CHEMIN = "foncier/management/commands/emettre_role_annuel.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''                deja_emise = Taxation.objects.filter(
                    contribuable_id=entree['contribuable_id'],
                    type_taxe_id=entree['type_taxe_id'],
                    parcelle_id=entree['parcelle_id'],
                    annee_fiscale=annee_cible,
                ).exists()

                if deja_emise:
                    n_deja_present += 1
                    continue'''

nouveau = '''                deja_emise = Taxation.objects.filter(
                    contribuable_id=entree['contribuable_id'],
                    type_taxe_id=entree['type_taxe_id'],
                    parcelle_id=entree['parcelle_id'],
                    annee_fiscale=annee_cible,
                ).exists()

                if deja_emise:
                    n_deja_present += 1
                    continue

                if entree['parcelle_id'] is not None:
                    parcelle_exoneree = Parcelle.objects.filter(
                        pk=entree['parcelle_id'], statut_fiscal='EXONERE'
                    ).exists()
                    if parcelle_exoneree:
                        n_exonerees += 1
                        continue'''

if "n_exonerees" in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)

    contenu = contenu.replace(
        "from foncier.models import Taxation",
        "from foncier.models import Taxation, Parcelle",
        1,
    )
    contenu = contenu.replace(
        "n_ignores = 0",
        "n_ignores = 0\n        n_exonerees = 0",
        1,
    )
    contenu = contenu.replace(
        '''        self.stdout.write(self.style.SUCCESS(
            f"Role {annee_cible} emis : {n_crees} nouvelle(s) taxation(s) creee(s), "
            f"{n_deja_present} deja existante(s) (ignorees)."
        ))''',
        '''        self.stdout.write(self.style.SUCCESS(
            f"Role {annee_cible} emis : {n_crees} nouvelle(s) taxation(s) creee(s), "
            f"{n_deja_present} deja existante(s) (ignorees), "
            f"{n_exonerees} parcelle(s) exoneree(s) (sautees)."
        ))''',
        1,
    )

    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : emettre_role_annuel saute maintenant les parcelles exonerees.")
else:
    print("ERREUR : bloc exact introuvable.")