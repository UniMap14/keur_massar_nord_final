import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from foncier.models import TypeDemande

TARIF = 5000  # FCFA

candidats = TypeDemande.objects.filter(
    categorie="CADASTRE", libelle__icontains="extrait"
)

if candidats.exists():
    n = candidats.update(tarif=TARIF, necessite_parcelle=True)
    print(f"OK : tarif de {TARIF} FCFA applique a {n} type(s) de demande existant(s) :")
    for t in candidats:
        print(f"  - {t.libelle}")
else:
    t = TypeDemande.objects.create(
        libelle="Extrait cadastral",
        categorie="CADASTRE",
        description="Document officiel attestant des caractéristiques cadastrales d'une parcelle (superficie, numéro de titre foncier, occupation du sol...).",
        pieces_requises="Aucune pièce requise (démarche en ligne).",
        delai_indicatif_jours=3,
        necessite_parcelle=True,
        tarif=TARIF,
        actif=True,
    )
    print(f"OK : nouveau type de demande 'Extrait cadastral' cree avec un tarif de {TARIF} FCFA.")