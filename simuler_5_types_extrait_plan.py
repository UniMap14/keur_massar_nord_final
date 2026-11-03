# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('simuler_5_types_extrait_plan.py', encoding='utf-8').read())"

Cree (ou reutilise) un compte citoyen de test, puis cree une
DemandeService PRETE pour chacun des 5 types "Extrait de plan — ..."
(sur de vraies parcelles avec geometrie), pour pouvoir telecharger et
comparer les 5 PDF generes.

Idempotent : si des demandes de test existent deja pour ce compte et ce
motif, elles ne sont pas recreees.
"""
from django.contrib.auth.models import User
import foncier.models as m

EMAIL_TEST = "test.extrait.plan@kmsn.local"
MOT_DE_PASSE_TEST = "TestExtrait2026!"

utilisateur, cree = User.objects.get_or_create(
    username=EMAIL_TEST,
    defaults={"email": EMAIL_TEST, "is_active": True},
)
if cree:
    utilisateur.set_password(MOT_DE_PASSE_TEST)
    utilisateur.save()
    print(f"Compte citoyen de test cree : {EMAIL_TEST} / {MOT_DE_PASSE_TEST}")
else:
    print(f"Compte citoyen de test deja existant : {EMAIL_TEST} (mot de passe inchange)")

# Deux vraies parcelles deja utilisees precedemment pour tester le plan
# (geometrie connue, voisinage dense) -- on les reutilise a tour de role.
nicads_test = ["0152020102300970", "0152020101800086"]
parcelles_test = [m.Parcelle.objects.filter(nicad=n).first() for n in nicads_test]
parcelles_test = [p for p in parcelles_test if p is not None]
if not parcelles_test:
    parcelles_test = list(m.Parcelle.objects.filter(geom__isnull=False)[:2])

types_a_tester = m.TypeDemande.objects.filter(
    libelle__startswith="Extrait de plan —"
).order_by("id")

print()
print(f"{len(types_a_tester)} type(s) de demande a tester, sur {len(parcelles_test)} parcelle(s) de reference.")
print()

for i, type_demande in enumerate(types_a_tester):
    parcelle = parcelles_test[i % len(parcelles_test)]

    demande_existante = m.DemandeService.objects.filter(
        demandeur=utilisateur, type_demande=type_demande, parcelle=parcelle
    ).first()
    if demande_existante:
        demande = demande_existante
        print(f"DEJA PRESENTE : {type_demande.libelle!r} -> demande #{demande.pk} (parcelle {parcelle.nicad})")
    else:
        demande = m.DemandeService.objects.create(
            demandeur=utilisateur,
            type_demande=type_demande,
            parcelle=parcelle,
            objet="Demande de simulation (test des 5 motifs d'extrait de plan).",
            statut=m.DemandeService.STATUT_PRETE,
            statut_paiement=m.DemandeService.STATUT_PAIEMENT_NON_REQUIS,
        )
        print(f"CREEE : {type_demande.libelle!r} -> demande #{demande.pk} (parcelle {parcelle.nicad})")

    print(f"   PDF : /demarches/{demande.pk}/extrait-cadastral.pdf")

print()
print("Pour tester : connectez-vous sur l'espace citoyen avec")
print(f"  identifiant : {EMAIL_TEST}")
print(f"  mot de passe : {MOT_DE_PASSE_TEST}")
print("puis ouvrez chaque lien PDF ci-dessus (ou via 'Mes demandes').")