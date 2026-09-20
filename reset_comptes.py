import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.auth.models import User

NOUVEAU_MDP = "1234"

RENOMMAGES = {
    "maire": "maire",
    "chef_cadastre": "chef_cadastre",
    "chef_fiscalite": "chef_fiscalite",
    "demo_citoyen_1": "citoyen1",
    "demo_citoyen_2": "citoyen2",
    "demo_citoyen_3": "citoyen3",
}


def main():
    for ancien_username, nouveau_username in RENOMMAGES.items():
        try:
            user = User.objects.get(username=ancien_username)
        except User.DoesNotExist:
            print(f"INTROUVABLE : {ancien_username} (deja renomme, ou jamais cree)")
            continue

        if ancien_username != nouveau_username:
            if User.objects.filter(username=nouveau_username).exclude(pk=user.pk).exists():
                print(f"IMPOSSIBLE : le nom '{nouveau_username}' est deja pris par un autre compte.")
                continue
            user.username = nouveau_username

        user.set_password(NOUVEAU_MDP)
        user.save()
        print(f"OK : {ancien_username} -> identifiant={nouveau_username}, mot de passe={NOUVEAU_MDP}")


if __name__ == "__main__":
    main()