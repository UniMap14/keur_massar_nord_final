import os
import secrets
import string
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.auth.models import User
from foncier.models import Taxation, Paiement, ProfilCitoyen


def generer_mot_de_passe():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(10))


def main():
    ids_contribuables_deja_lies = set(
        ProfilCitoyen.objects.values_list("contribuable_id", flat=True)
    )
    ids_taxations_payees = set(
        Paiement.objects.values_list("taxation_id", flat=True)
    )

    qs_base = (
        Taxation.objects.filter(simulation_fiscale=True)
        .exclude(contribuable_id__in=ids_contribuables_deja_lies)
        .select_related("contribuable", "parcelle")
    )

    taxation_payee = (
        qs_base.filter(id__in=ids_taxations_payees).order_by("-montant_du").first()
    )
    taxation_en_retard = (
        qs_base.exclude(id__in=ids_taxations_payees).order_by("-montant_du").first()
    )
    deja_choisies = {t.pk for t in [taxation_payee, taxation_en_retard] if t}
    taxation_montant_eleve = (
        qs_base.exclude(pk__in=deja_choisies).order_by("-montant_du").first()
    )

    scenarios = [
        ("demo_citoyen_1", taxation_en_retard, "Demo - taxation en retard"),
        ("demo_citoyen_2", taxation_payee, "Demo - taxation deja payee"),
        ("demo_citoyen_3", taxation_montant_eleve, "Demo - montant eleve (terrain nu)"),
    ]

    print("=== IDENTIFIANTS - A NOTER MAINTENANT ===\n")

    for username, taxation, description in scenarios:
        if taxation is None:
            print(f"Aucune taxation disponible pour le scenario {description}.")
            continue

        if User.objects.filter(username=username).exists():
            print(f"Le compte '{username}' existe deja - non recree.")
            continue

        mot_de_passe = generer_mot_de_passe()
        user = User.objects.create_user(
            username=username,
            password=mot_de_passe,
            first_name="Citoyen",
            last_name=f"Demo {username[-1]}",
        )

        contribuable = taxation.contribuable
        contribuable.nom = f"Contribuable Demo {username[-1]}"
        contribuable.prenom = ""
        contribuable.save(update_fields=["nom", "prenom"])

        ProfilCitoyen.objects.create(user=user, contribuable=contribuable, actif=True)

        print(f"{description}")
        print(f"  Identifiant : {username}")
        print(f"  Mot de passe : {mot_de_passe}")
        montant = taxation.montant_du
        nicad = taxation.parcelle.nicad if taxation.parcelle_id else "-"
        print(f"  Taxation liee : {montant} FCFA ({nicad})")
        print()

    print("Ces comptes sont clairement identifies comme des comptes de demonstration.")


if __name__ == "__main__":
    main()