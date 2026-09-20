import os
import secrets
import string
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.auth.models import User, Group
from foncier.models import ProfilAgent

COMPTES = [
    {
        "username": "maire",
        "first_name": "Adama",
        "last_name": "SARR",
        "fonction": "Maire de Keur Massar Nord",
        "groupe": "Superviseur",
    },
    {
        "username": "chef_cadastre",
        "first_name": "(a completer)",
        "last_name": "(a completer)",
        "fonction": "Chef du Service Cadastre",
        "groupe": "Agent technique",
    },
    {
        "username": "chef_fiscalite",
        "first_name": "(a completer)",
        "last_name": "(a completer)",
        "fonction": "Chef du Service Fiscalite",
        "groupe": "Agent fiscal",
    },
]


def generer_mot_de_passe():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(10))


def main():
    resultats = []

    for infos in COMPTES:
        if User.objects.filter(username=infos["username"]).exists():
            print(f"Le compte '{infos['username']}' existe deja - non recree.")
            continue

        mot_de_passe = generer_mot_de_passe()

        user = User.objects.create_user(
            username=infos["username"],
            password=mot_de_passe,
            first_name=infos["first_name"],
            last_name=infos["last_name"],
            is_staff=True,
        )

        try:
            groupe = Group.objects.get(name=infos["groupe"])
            user.groups.add(groupe)
        except Group.DoesNotExist:
            print(f"Groupe '{infos['groupe']}' introuvable - role non assigne pour {infos['username']}.")

        ProfilAgent.objects.create(user=user, fonction=infos["fonction"])

        resultats.append((infos["username"], mot_de_passe, infos["fonction"]))
        print(f"Compte cree : {infos['username']} ({infos['fonction']})")

    if resultats:
        print()
        print("=== IDENTIFIANTS - A NOTER MAINTENANT, non re-affichables ensuite ===")
        for username, mdp, fonction in resultats:
            print(f"  {fonction}")
            print(f"    Identifiant : {username}")
            print(f"    Mot de passe : {mdp}")
            print()
        print("Changez ces mots de passe des la premiere connexion, via 'Mon Profil'.")


if __name__ == "__main__":
    main()