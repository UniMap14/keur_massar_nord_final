# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('creer_5_types_extrait_plan.py', encoding='utf-8').read())"

Cree les 5 types de demande distincts pour les differents motifs
d'extrait de plan, sur le modele du vrai formulaire "Etat de cession"
du Bureau du Cadastre (cases : autorisation de construire, demande de
regularisation, situation, delimitation, autres).

Le tarif de chacun est laisse a 0 pour l'instant (demarche consideree
gratuite tant que la grille tarifaire officielle n'est pas confirmee et
codee) -- IMPORTANT : ne pas activer de paiement avant d'avoir les
vrais montants unitaires confirmes, pour ne pas facturer un montant
invente a un citoyen.

Idempotent : si un type avec le meme libelle existe deja, il n'est pas
recree (juste signale).
"""
import foncier.models as m

NOUVEAUX_TYPES = [
    {
        "libelle": "Extrait de plan — Autorisation de construire",
        "description": (
            "Extrait du plan cadastral demande pour appuyer un dossier de "
            "permis de construire : localisation et limites exactes de la "
            "parcelle avant travaux."
        ),
    },
    {
        "libelle": "Extrait de plan — Demande de régularisation",
        "description": (
            "Extrait du plan cadastral demande pour officialiser une "
            "situation existante (occupation ancienne, construction sans "
            "autorisation prealable...), generalement en reference a un "
            "arrete precis."
        ),
    },
    {
        "libelle": "Extrait de plan — Situation",
        "description": (
            "Extrait du plan cadastral demande pour simplement attester de "
            "la situation actuelle d'une parcelle (localisation, limites)."
        ),
    },
    {
        "libelle": "Extrait de plan — Délimitation",
        "description": (
            "Extrait du plan cadastral demande dans le cadre d'une operation "
            "de delimitation/bornage d'une parcelle."
        ),
    },
    {
        "libelle": "Extrait de plan — Autres",
        "description": (
            "Extrait du plan cadastral demande pour un motif autre que ceux "
            "listes ci-dessus (a preciser dans la demande)."
        ),
    },
]

for donnees in NOUVEAUX_TYPES:
    existe_deja = m.TypeDemande.objects.filter(libelle=donnees["libelle"]).exists()
    if existe_deja:
        print(f"DEJA PRESENT : {donnees['libelle']!r} -- ignore.")
        continue
    td = m.TypeDemande.objects.create(
        libelle=donnees["libelle"],
        categorie="CADASTRE",
        description=donnees["description"],
        pieces_requises="Aucune pièce requise (démarche en ligne).",
        delai_indicatif_jours=3,
        necessite_parcelle=True,
        tarif=0,  # a confirmer : voir grille tarifaire officielle (Arrete N 42092 du 13/12/2021)
        actif=True,
    )
    print(f"CREE : id={td.id} — {td.libelle}")

print()
print("Tarif laisse a 0 pour les 5 nouveaux types -- a mettre a jour une fois")
print("la grille tarifaire officielle confirmee (droit fixe, bornage, leves,")
print("personnel, materiel).")