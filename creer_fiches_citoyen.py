import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from citoyens.models import Citoyen
from foncier.models import ProfilCitoyen

USERNAMES = ["citoyen1", "citoyen2", "citoyen3"]

for username in USERNAMES:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"INTROUVABLE : {username}")
        continue

    if hasattr(user, "citoyen"):
        print(f"DEJA PRESENT : {username} a deja une fiche Citoyen.")
        continue

    profil = ProfilCitoyen.objects.filter(user=user).select_related("contribuable").first()
    if profil is None:
        print(f"IMPOSSIBLE : {username} n'a pas de ProfilCitoyen lie.")
        continue

    numero_fiscal = profil.contribuable.numero_fiscal

    from foncier.models import Taxation
    taxation = Taxation.objects.filter(contribuable=profil.contribuable, parcelle__isnull=False).select_related("parcelle").first()
    numero_foncier = taxation.parcelle.nicad if taxation else f"NICAD-{username}"

    Citoyen.objects.create(
        user=user,
        numero_fiscal=numero_fiscal,
        numero_foncier=numero_foncier,
        statut=Citoyen.STATUT_VALIDE,
        date_validation=timezone.now(),
    )
    print(f"OK : fiche Citoyen creee pour {username} (statut=Valide, numero_fiscal={numero_fiscal}, numero_foncier={numero_foncier})")