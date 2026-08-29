# ============================================================
# rattacher_proprietaires_candidats.py
#
# Crée un Propriétaire "provisoire" pour chacun des 355 candidats
# fiables listés dans parcelles_candidats_proprietaire_a_verifier.csv
# (généré lors de l'import du shapefile), et le rattache à sa parcelle.
#
# IMPORTANT — CE QUE CE SCRIPT NE FAIT PAS :
#   - Il n'assigne JAMAIS un statut fiscal ni ne crée de Contribuable /
#     Taxation : établir une obligation fiscale reste une décision
#     humaine, pas quelque chose à automatiser.
#   - Il n'écrase JAMAIS un propriétaire déjà renseigné manuellement
#     sur une parcelle (si parcelle.proprietaire est déjà défini, la
#     ligne est simplement ignorée).
#   - Il n'invente AUCUN numéro de CNI réel : le shapefile n'en
#     contient pas. Un identifiant provisoire, clairement marqué
#     "AVERIFIER-...", est utilisé à la place. Ces fiches sont donc
#     immédiatement repérables (recherchez "AVERIFIER" dans
#     Propriétaires) et NE DOIVENT PAS être considérées comme une
#     preuve légale de propriété tant qu'un agent n'a pas vérifié et
#     corrigé le vrai numéro de CNI.
#
# UTILISATION :  python rattacher_proprietaires_candidats.py
# ============================================================

import csv
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from foncier.models import Parcelle, Propriétaire

CHEMIN_CSV = "parcelles_candidats_proprietaire_a_verifier.csv"


def decouper_nom(nom_complet):
    """Découpage best-effort 'Prénom(s) Nom' -> (prenom, nom).
    Le dernier mot est pris comme nom de famille, le reste comme
    prénom(s) — convention la plus courante, à corriger manuellement
    si besoin dans les cas particuliers."""
    mots = nom_complet.strip().split()
    if len(mots) == 1:
        return "", mots[0]
    return " ".join(mots[:-1]), mots[-1]


def main():
    if not os.path.exists(CHEMIN_CSV):
        print(f"ERREUR : fichier introuvable : {CHEMIN_CSV}")
        print("Ce fichier est généré automatiquement lors de l'import du shapefile.")
        return

    n_crees = 0
    n_lies = 0
    n_deja_assignes = 0
    n_introuvables = 0
    n_sans_nom = 0

    with open(CHEMIN_CSV, encoding="utf-8-sig") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        lignes = list(lecteur)

    print(f"{len(lignes)} candidat(s) trouvé(s) dans le rapport.\n")

    for ligne in lignes:
        id_shp = ligne.get("id_shp", "").strip()
        titulaire = (ligne.get("titulaire_matrice") or "").strip()

        if not titulaire:
            n_sans_nom += 1
            continue

        try:
            parcelle = Parcelle.objects.get(id_shp=id_shp)
        except Parcelle.DoesNotExist:
            n_introuvables += 1
            continue

        if parcelle.proprietaire_id:
            n_deja_assignes += 1
            continue  # déjà rattachée manuellement : on ne touche à rien

        prenom, nom = decouper_nom(titulaire)
        cni_provisoire = f"AVERIFIER-{id_shp}"

        proprietaire, cree = Propriétaire.objects.get_or_create(
            ni_cni=cni_provisoire,
            defaults={
                "nom": nom,
                "prenom": prenom,
                "adresse": (
                    "⚠️ Rattachement automatique depuis la matrice cadastrale "
                    "(import shapefile) — CNI provisoire à vérifier et corriger "
                    "avant tout usage officiel."
                ),
            },
        )
        if cree:
            n_crees += 1

        parcelle.proprietaire = proprietaire
        parcelle.save(update_fields=["proprietaire"])
        n_lies += 1

    print("=== Résumé ===")
    print(f"  Propriétaires créés (provisoires) : {n_crees}")
    print(f"  Parcelles rattachées               : {n_lies}")
    print(f"  Déjà assignées manuellement (ignorées) : {n_deja_assignes}")
    print(f"  Parcelles introuvables (id_shp)     : {n_introuvables}")
    print(f"  Lignes sans nom de titulaire         : {n_sans_nom}")
    print()
    print("Pour retrouver et vérifier ces fiches provisoires : dashboard")
    print("-> Propriétaires -> recherche \"AVERIFIER\".")


if __name__ == "__main__":
    main()
