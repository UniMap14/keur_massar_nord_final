# ============================================================
# foncier/tests/fixtures.py
#
# Fabriques d'objets minimaux mais réalistes, réutilisées dans
# plusieurs fichiers de tests, pour ne pas dupliquer la même
# création de Zone/Parcelle/Contribuable/Taxation partout.
# ============================================================

from decimal import Decimal

from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import MultiPolygon, Polygon

from foncier.models import (
    Zone, Parcelle, Propriétaire, Contribuable, TypeTaxe, Taxation, Paiement,
)


def creer_geometrie_carree(decalage=0.0):
    """Un petit carré (~100m de côté) autour de Keur Massar, pour donner
    une géométrie valide aux Parcelle/Zone de test sans avoir besoin
    d'un vrai shapefile."""
    x, y = -17.31 + decalage, 14.79 + decalage
    d = 0.001
    poly = Polygon(((x, y), (x + d, y), (x + d, y + d), (x, y + d), (x, y)))
    return MultiPolygon(poly)


_compteur_zone = {"n": 0}


def creer_zone(nom="Zone de test"):
    _compteur_zone["n"] += 1
    return Zone.objects.create(
        id_shp=900000 + _compteur_zone["n"],
        nom=nom,
        layer="test",
        path="test.shp",
        geom=creer_geometrie_carree(),
    )


def creer_parcelle(nicad="00001", zone=None, **kwargs):
    valeurs = {
        "nicad": nicad,
        "superficie": 300.0,
        "geom": creer_geometrie_carree(),
        "zone": zone,
    }
    valeurs.update(kwargs)
    return Parcelle.objects.create(**valeurs)


def creer_proprietaire(nom="Diop", prenom="Awa", ni_cni="1234567890123"):
    return Propriétaire.objects.create(nom=nom, prenom=prenom, ni_cni=ni_cni)


def creer_contribuable(numero_fiscal="CTB-0001", nom="Diop", prenom="Awa", **kwargs):
    valeurs = {"numero_fiscal": numero_fiscal, "nom": nom, "prenom": prenom}
    valeurs.update(kwargs)
    return Contribuable.objects.create(**valeurs)


def creer_type_taxe(code="FONCIERE", libelle="Taxe foncière communale"):
    type_taxe, _ = TypeTaxe.objects.get_or_create(code=code, defaults={"libelle": libelle})
    return type_taxe


def creer_taxation(contribuable, type_taxe=None, montant_du=Decimal("50000.00"), annee=2026, parcelle=None):
    return Taxation.objects.create(
        contribuable=contribuable,
        type_taxe=type_taxe or creer_type_taxe(),
        montant_du=montant_du,
        annee_fiscale=annee,
        parcelle=parcelle,
    )


def creer_paiement(taxation, montant=None, statut='CONFIRME'):
    return Paiement.objects.create(
        taxation=taxation,
        montant=montant if montant is not None else taxation.montant_du,
        statut_paiement=statut,
    )


def creer_agent(username="agent_test", role=None, is_superuser=False):
    """Crée un compte staff, éventuellement rattaché à un des 3 groupes
    de rôle (fiscal / technique / superviseur)."""
    user = User.objects.create_user(
        username=username, password="motdepasse123", is_staff=True, is_superuser=is_superuser,
    )
    if role:
        noms = {"fiscal": "Agent fiscal", "technique": "Agent technique", "superviseur": "Superviseur"}
        groupe, _ = Group.objects.get_or_create(name=noms[role])
        user.groups.add(groupe)
    return user


def creer_citoyen(username="citoyen_test", contribuable=None):
    from foncier.models import ProfilCitoyen

    user = User.objects.create_user(username=username, password="motdepasse123", email=f"{username}@example.com")
    if contribuable:
        ProfilCitoyen.objects.create(user=user, contribuable=contribuable)
    return user
