# -*- coding: utf-8 -*-
"""
Cree les 5 groupes de roles et les 8 comptes gestionnaires de demo,
et reaffecte les comptes chef_cadastre / chef_fiscalite / maire
existants a leurs nouveaux groupes precis.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from django.contrib.auth.models import User, Group
from foncier.permissions import (
    GROUPE_SUPERVISEUR, GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE,
    GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL,
)

# --- 1. Creation des 5 groupes ---
for nom in [GROUPE_SUPERVISEUR, GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE,
            GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL]:
    _, cree = Group.objects.get_or_create(name=nom)
    print(f"{'Cree' if cree else 'Deja present'} : groupe '{nom}'")

groupe_superviseur = Group.objects.get(name=GROUPE_SUPERVISEUR)
groupe_chef_cadastre = Group.objects.get(name=GROUPE_CHEF_TECHNIQUE)
groupe_gestionnaire_cadastre = Group.objects.get(name=GROUPE_GESTIONNAIRE_TECHNIQUE)
groupe_chef_fiscalite = Group.objects.get(name=GROUPE_CHEF_FISCAL)
groupe_gestionnaire_fiscalite = Group.objects.get(name=GROUPE_GESTIONNAIRE_FISCAL)

TOUS_LES_ROLES = [
    groupe_superviseur, groupe_chef_cadastre, groupe_gestionnaire_cadastre,
    groupe_chef_fiscalite, groupe_gestionnaire_fiscalite,
]


def assigner_role(username, groupe_cible):
    """Retire l'utilisateur de tous les groupes de role puis l'ajoute
    au groupe cible. Ne fait rien si l'utilisateur n'existe pas."""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"IGNORE : compte '{username}' introuvable, non reaffecte.")
        return
    user.groups.remove(*TOUS_LES_ROLES)
    user.groups.add(groupe_cible)
    if not user.is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
    print(f"OK : '{username}' -> groupe '{groupe_cible.name}'")


# --- 2. Reaffectation des comptes existants ---
assigner_role("maire", groupe_superviseur)
assigner_role("chef_cadastre", groupe_chef_cadastre)
assigner_role("chef_fiscalite", groupe_chef_fiscalite)


# --- 3. Creation des 8 comptes gestionnaires de demo (mdp 1234) ---
def creer_gestionnaire(username, groupe_cible, prenom, nom):
    user, cree = User.objects.get_or_create(
        username=username,
        defaults={"is_staff": True, "first_name": prenom, "last_name": nom},
    )
    if cree:
        user.set_password("1234")
        user.is_staff = True
        user.first_name = prenom
        user.last_name = nom
        user.save()
        print(f"OK : compte '{username}' cree (mdp 1234).")
    else:
        print(f"DEJA PRESENT : compte '{username}' existait deja (mot de passe non modifie).")
    user.groups.remove(*TOUS_LES_ROLES)
    user.groups.add(groupe_cible)
    print(f"    -> groupe '{groupe_cible.name}'")


for i in range(1, 5):
    creer_gestionnaire(f"cadastre{i}", groupe_gestionnaire_cadastre, "Gestionnaire", f"Cadastre {i}")

for i in range(1, 5):
    creer_gestionnaire(f"fiscale{i}", groupe_gestionnaire_fiscalite, "Gestionnaire", f"Fiscalite {i}")

print("\nTermine.")