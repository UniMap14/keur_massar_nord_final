# ============================================================
# simuler_fiscalite_fonciere.py
#
# Génère une SIMULATION de la fiscalité foncière (CFPB/CFPNB) sur les
# vraies parcelles déjà importées, faute de données fiscales réelles
# communicables (trop sensibles — voir enquête de terrain, chapitre
# méthodologie du mémoire).
#
# CHAQUE parcelle simulée est marquée simulation_fiscale=True, pour ne
# JAMAIS confondre ces montants avec une déclaration ou un calcul réel
# — ni dans la base, ni dans l'interface admin, ni dans le mémoire.
#
# MÉTHODE ET SOURCES (voir mémoire, chapitre méthodologie, pour le détail) :
#
#   Taux légaux (Code Général des Impôts, publics) :
#     - CFPB (bâti)      : 5% de la valeur locative annuelle
#     - Abattement RP    : 1 500 000 FCFA déduits avant application du taux
#     - CFPNB (non bâti) : 5% de la valeur vénale
#     - Surtaxe terrain non bâti : 1 à 3% (simplifiée ici à 2% flat,
#       faute de données de zonage plus fines)
#
#   Valeurs au m² (faute de barème DGID public spécifique à Keur Massar
#   Nord — vérifié : l'arrêté ministériel n°2781-MEF-DGID de 2010 ne
#   couvre que le centre de Dakar et Saint-Louis) :
#     - Bâtis          : 14 000 FCFA/m²/an (valeur locative) — moyenne
#       d'annonces de location réelles à Keur Massar (150 000 à
#       200 000 FCFA/mois pour 120-150 m²)
#     - Terrain Nu      : 100 000 FCFA/m² (valeur vénale) — moyenne
#       d'annonces de vente réelles à Keur Massar (53 000 à 133 000
#       FCFA/m² selon les cités)
#     - Zone de culture : 35 000 FCFA/m² (valeur vénale) — ESTIMATION
#       FAIBLEMENT SOURCÉE, faute de référence de marché spécifique ;
#       ne concerne que 3 parcelles sur 40 588, impact négligeable
#       sur les totaux.
#
# Ne touche JAMAIS aux parcelles dont montant_taxe_annuelle a déjà été
# saisi manuellement par un agent (valeur non nulle) : la simulation
# ne s'applique qu'aux parcelles encore à 0, pour ne jamais écraser
# une vraie donnée entrée à la main.
#
# Réexécutable sans risque : les parcelles déjà simulées (simulation_
# fiscale=True) sont ignorées lors d'un nouveau passage.
#
# UTILISATION :  python simuler_fiscalite_fonciere.py
# ============================================================

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from foncier.models import Parcelle

# --- Taux légaux (CGI, publics) ---
TAUX_CFPB = Decimal("0.05")
TAUX_CFPNB = Decimal("0.05")
TAUX_SURTAXE_NON_BATI = Decimal("0.02")  # simplification de l'échelle 1-3%
ABATTEMENT_RESIDENCE_PRINCIPALE = Decimal("1500000")

# --- Valeurs au m², sourcées (voir en-tête du fichier) ---
VALEUR_M2 = {
    "Batis": Decimal("14000"),           # FCFA/m²/an, valeur locative
    "Terrain Nu": Decimal("100000"),     # FCFA/m², valeur vénale
    "Zone de culture": Decimal("35000"), # FCFA/m², valeur vénale — faiblement sourcé
}


def arrondi(valeur):
    return valeur.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def calculer_batis(superficie):
    """Retourne (valeur_locative_annuelle, montant_cfpb)."""
    valeur_locative = superficie * VALEUR_M2["Batis"]
    base_imposable = max(Decimal("0"), valeur_locative - ABATTEMENT_RESIDENCE_PRINCIPALE)
    montant = base_imposable * TAUX_CFPB
    return arrondi(valeur_locative), arrondi(montant)


def calculer_non_bati(superficie, cle_valeur):
    """Retourne (0, montant_cfpnb[+surtaxe]) — pas de 'valeur locative'
    pour du non-bâti, on ne remplit donc pas ce champ.
    La surtaxe (prévue pour dissuader les terrains laissés vacants/
    spéculatifs) ne s'applique qu'au Terrain Nu, pas à une parcelle
    activement cultivée."""
    valeur_venale = superficie * VALEUR_M2[cle_valeur]
    taux = TAUX_CFPNB + (TAUX_SURTAXE_NON_BATI if cle_valeur == "Terrain Nu" else Decimal("0"))
    montant = valeur_venale * taux
    return Decimal("0"), arrondi(montant)


def main():
    qs = (
        Parcelle.objects
        .filter(occupation_sol__in=list(VALEUR_M2.keys()))
        .filter(montant_taxe_annuelle=0)
        .filter(simulation_fiscale=False)
    )

    total_candidates = qs.count()
    print(f"{total_candidates} parcelle(s) éligibles à la simulation "
          f"(occupation du sol connue, montant encore à 0, pas déjà simulées).\n")

    compteurs = {cle: 0 for cle in VALEUR_M2}
    total_recettes_potentielles = Decimal("0")

    with transaction.atomic():
        parcelles_a_maj = []
        for parcelle in qs.iterator():
            superficie = Decimal(str(parcelle.superficie or 0))
            if parcelle.occupation_sol == "Batis":
                valeur_locative, montant = calculer_batis(superficie)
            else:
                valeur_locative, montant = calculer_non_bati(
                    superficie, parcelle.occupation_sol
                )

            parcelle.valeur_locative = valeur_locative
            parcelle.montant_taxe_annuelle = montant
            parcelle.simulation_fiscale = True
            parcelles_a_maj.append(parcelle)

            compteurs[parcelle.occupation_sol] += 1
            total_recettes_potentielles += montant

        Parcelle.objects.bulk_update(
            parcelles_a_maj,
            ["valeur_locative", "montant_taxe_annuelle", "simulation_fiscale"],
            batch_size=1000,
        )

    print("=== Résumé de la simulation ===")
    for cle, n in compteurs.items():
        print(f"  {cle} : {n} parcelle(s) simulée(s)")
    print()
    print(f"Recettes fiscales potentielles simulées (total) : "
          f"{total_recettes_potentielles:,.0f} FCFA".replace(",", " "))
    if sum(compteurs.values()):
        moyenne = total_recettes_potentielles / sum(compteurs.values())
        print(f"Montant moyen simulé par parcelle : {moyenne:,.0f} FCFA".replace(",", " "))
    print()
    print("⚠️  Rappel : ces montants sont une SIMULATION académique (occupation_sol x")
    print("   valeur au m² estimée depuis de vraies annonces immobilières), pas des")
    print("   données fiscales réelles. Chaque parcelle concernée a simulation_fiscale=True.")


if __name__ == "__main__":
    main()