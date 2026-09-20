import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.auth.models import User
from foncier.models import Taxation, ProfilCitoyen
from citoyens.models import Citoyen


def main():
    if User.objects.filter(username="citoyen4").exists():
        print("DEJA PRESENT : le compte 'citoyen4' existe deja, rien a faire.")
        return

    ids_contribuables_deja_lies = set(
        ProfilCitoyen.objects.values_list("contribuable_id", flat=True)
    )

    taxation = (
        Taxation.objects.filter(simulation_fiscale=True)
        .exclude(contribuable_id__in=ids_contribuables_deja_lies)
        .select_related("contribuable", "parcelle")
        .order_by("?")
        .first()
    )

    if taxation is None:
        print("ERREUR : aucune taxation simulee disponible (non deja liee a un compte).")
        return

    contribuable = taxation.contribuable
    contribuable.nom = "Contribuable Demo 4"
    contribuable.prenom = ""
    contribuable.save(update_fields=["nom", "prenom"])

    user = User.objects.create_user(
        username="citoyen4",
        password="1234",
        email="citoyen4@demo.local",
        first_name="Citoyen",
        last_name="Demo 4",
    )

    nicad = taxation.parcelle.nicad if taxation.parcelle_id else ""

    Citoyen.objects.create(
        user=user,
        telephone="",
        numero_fiscal=contribuable.numero_fiscal,
        numero_foncier=nicad,
        statut=Citoyen.STATUT_VALIDE,
    )

    ProfilCitoyen.objects.create(user=user, contribuable=contribuable, actif=True)

    print("=== IDENTIFIANTS - A NOTER ===\n")
    print("Identifiant : citoyen4")
    print("Mot de passe : 1234")
    print(f"Email : citoyen4@demo.local")
    print(f"Numero fiscal : {contribuable.numero_fiscal}")
    print(f"Numero foncier (NICAD) : {nicad}")
    print(f"Taxation liee : {taxation.montant_du} FCFA")


if __name__ == "__main__":
    main()