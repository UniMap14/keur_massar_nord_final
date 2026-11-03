# -*- coding: utf-8 -*-
"""
Pour les 5 premiers citoyens (par ordre de creation) :
  - s'assure que chacun a 5 demandes d'extrait cadastral au total
  - en met 3 sur les 5 au statut "Prete a retirer" + paiement confirme
    (telechargeables), laisse les 2 autres en l'etat (non traitees)
"""
import io
from django.contrib.auth.models import User
from citoyens.models import Citoyen
from foncier.models import TypeDemande, Parcelle, DemandeService

type_extrait = TypeDemande.objects.get(libelle='Extrait cadastral')

citoyens = list(Citoyen.objects.select_related('user').order_by('pk')[:5])

resultats = []

for c in citoyens:
    parcelle = Parcelle.objects.filter(nicad=c.numero_foncier).first()
    if parcelle is None:
        resultats.append((c, None))
        continue

    demandes = list(
        DemandeService.objects.filter(demandeur=c.user, type_demande=type_extrait)
        .order_by('date_demande')
    )

    while len(demandes) < 5:
        nouvelle = DemandeService.objects.create(
            demandeur=c.user,
            type_demande=type_extrait,
            parcelle=parcelle,
            objet="Demande supplementaire d'extrait cadastral.",
        )
        demandes.append(nouvelle)

    a_valider = demandes[:3]
    for d in a_valider:
        d.statut = DemandeService.STATUT_PRETE
        d.statut_paiement = DemandeService.STATUT_PAIEMENT_CONFIRME
        d.montant_paye = type_extrait.tarif
        d.reference_paiement = d.reference_paiement or "DEMO-VALIDE"
        d.commentaire_agent = "Dossier traite, document disponible au telechargement."
        d.save(update_fields=[
            "statut", "statut_paiement", "montant_paye",
            "reference_paiement", "commentaire_agent",
        ])

    resultats.append((c, demandes))

print("=== Resultat ===")
for c, demandes in resultats:
    if demandes is None:
        print(c.user.username, "- AUCUNE PARCELLE TROUVEE, ignore")
        continue
    print()
    print(c.user.get_full_name(), "|", c.user.email, "| NICAD:", c.numero_foncier)
    for i, d in enumerate(demandes, 1):
        telechargeable = "TELECHARGEABLE" if d.statut == "PRETE" and d.statut_paiement == "CONFIRME" else ""
        print("   -", d.numero_dossier, "| statut:", d.statut, "| paiement:", d.statut_paiement, telechargeable)

print()
print("=== Termine ===")