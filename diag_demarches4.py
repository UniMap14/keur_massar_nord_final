# -*- coding: utf-8 -*-
"""
Ce script interroge directement la base de donnees via Django, pour
confirmer l'hypothese : le badge "502" compte TOUTES les demandes
recues/en cours (foncier/context_processors.py, sans filtre de role),
alors que la page "Demarches en ligne" filtre par categorie
(type_demande__categorie == "FISCALITE") pour un Chef Fiscal
(foncier/dashboard_views.py, _filtrer_demandes_service).

A executer depuis la racine du projet (a cote de manage.py) avec :

    python manage.py shell -c "exec(open('diag_demarches4.py', encoding='utf-8').read())"

Copiez-collez toute la sortie ici.
"""
from foncier.models import DemandeService

print("=" * 100)
print("1) Total DemandeService dans la base :", DemandeService.objects.count())
print()

print("2) Statuts presents et leur nombre :")
from django.db.models import Count
for ligne in DemandeService.objects.values("statut").annotate(n=Count("id")).order_by("-n"):
    print(" ", ligne)
print()

print("3) Badge sidebar (nb_demandes_a_traiter) : RECUE + EN_COURS, SANS filtre de categorie :")
print(
    " ",
    DemandeService.objects.filter(
        statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]
    ).count(),
)
print()

print("4) Valeurs de 'categorie' presentes sur type_demande, et nombre de demandes par categorie :")
for ligne in (
    DemandeService.objects.values("type_demande__categorie")
    .annotate(n=Count("id"))
    .order_by("-n")
):
    print(" ", ligne)
print()

print("5) Demandes RECUE/EN_COURS avec categorie == 'FISCALITE' (ce que la page devrait montrer pour un Chef Fiscal) :")
print(
    " ",
    DemandeService.objects.filter(
        statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS],
        type_demande__categorie="FISCALITE",
    ).count(),
)
print()

print("6) Liste des TypeDemandeService et leur categorie exacte (verifier l'orthographe/valeur) :")
from foncier.models import TypeDemandeService
for t in TypeDemandeService.objects.all().order_by("categorie", "libelle"):
    print(f"   id={t.id:<4} categorie={t.categorie!r:<20} libelle={t.libelle}")
print()

print("7) Groupes Django existants et noms exacts (pour comparer a GROUPE_CHEF_FISCAL etc.) :")
from django.contrib.auth.models import Group
for g in Group.objects.all():
    print("  -", repr(g.name))
print()

print("8) Groupes de l'utilisateur actuellement connecte en tant que 'Chef du Service Fiscalite'")
print("   (remplacez 'maimouna' par le username exact si different) :")
from django.contrib.auth.models import User
for u in User.objects.filter(is_staff=True):
    profil = getattr(u, "profil_agent", None)
    fonction = profil.fonction if profil else ""
    if "fiscal" in fonction.lower() or "fiscalit" in fonction.lower():
        print(f"   user={u.username!r} fonction={fonction!r} groupes={list(u.groups.values_list('name', flat=True))}")
print()

print("Script termine. Copiez-collez toute la sortie ci-dessus.")