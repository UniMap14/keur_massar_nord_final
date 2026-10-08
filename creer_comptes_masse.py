# ============================================================
# creer_comptes_masse.py
#
# Cree en masse :
#   1. citoyen5 a citoyen200 (196 comptes, mdp 1234) -- 160 "a jour",
#      36 "en retard", avec mise a jour du statut_fiscal de leur
#      parcelle en consequence (vert/rouge sur le geoportail admin).
#   2. exoneration1 a exoneration300 (300 comptes, mdp 1234) -- chacun
#      avec une DemandeExoneration : la plupart deja VALIDEE (parcelle
#      passee en EXONERE), le reste encore SOUMISE (en attente de
#      traitement par un agent).
#
# Reexecutable sans risque : si un compte existe deja (meme username),
# il est ignore sans erreur.
#
# UTILISATION :  python creer_comptes_masse.py
# ============================================================

import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone

from foncier.models import Taxation, Paiement, ProfilCitoyen, DemandeExoneration
from citoyens.models import Citoyen

MOT_DE_PASSE = "1234"


def pool_taxations_disponibles(n):
    """Renvoie jusqu'a n Taxation simulees, UNE SEULE par contribuable
    distinct (un contribuable peut avoir plusieurs taxations -- 2026
    ET 2027 par exemple, suite a l'emission du role annuel), et dont
    le contribuable n'est ni deja lie a un compte citoyen (ProfilCitoyen),
    ni deja associe a une fiche Citoyen existante (creee par un script
    anterieur, ex: creer_fiches_citoyen.py, sans forcement de compte lie)."""
    deja_lies = set(ProfilCitoyen.objects.values_list("contribuable_id", flat=True))
    numeros_fiscaux_pris = set(Citoyen.objects.values_list("numero_fiscal", flat=True))

    contribuable_ids = list(
        Taxation.objects.filter(simulation_fiscale=True)
        .exclude(contribuable_id__in=deja_lies)
        .exclude(contribuable__numero_fiscal__in=numeros_fiscaux_pris)
        .values_list("contribuable_id", flat=True)
        .distinct()
        .order_by("?")[:n]
    )

    resultat = []
    for cid in contribuable_ids:
        taxation = (
            Taxation.objects.filter(contribuable_id=cid, simulation_fiscale=True)
            .select_related("contribuable", "parcelle")
            .order_by("-annee_fiscale")
            .first()
        )
        if taxation:
            resultat.append(taxation)
    return resultat


def lier_compte(username, taxation, suffixe_nom):
    """Cree User + Citoyen + ProfilCitoyen pour une taxation donnee.
    Renvoie le contribuable lie (ou None si le username existe deja)."""
    if User.objects.filter(username=username).exists():
        return None

    contribuable = taxation.contribuable

    if Citoyen.objects.filter(numero_fiscal=contribuable.numero_fiscal).exists():
        return None
    contribuable.nom = f"Contribuable Demo {suffixe_nom}"
    contribuable.prenom = ""
    contribuable.save(update_fields=["nom", "prenom"])

    user = User.objects.create_user(
        username=username,
        password=MOT_DE_PASSE,
        email=f"{username}@demo.local",
        first_name="Citoyen",
        last_name=f"Demo {suffixe_nom}",
    )

    nicad = taxation.parcelle.nicad if taxation.parcelle_id else ""
    Citoyen.objects.create(
        user=user,
        telephone="",
        numero_fiscal=contribuable.numero_fiscal,
        numero_foncier=nicad,
        statut=Citoyen.STATUT_VALIDE,
    )
    ProfilCitoyen.objects.create(user=user, contribuable=contribuable, actif=True)

    return contribuable


def forcer_statut_contribuable(contribuable, a_jour):
    """S'assure que TOUTES les taxations de ce contribuable (2026 ET
    2027 le cas echeant) refletent bien le statut voulu, et met a jour
    le statut_fiscal de leurs parcelles en consequence."""
    taxations = Taxation.objects.filter(contribuable=contribuable).select_related("parcelle")

    for taxation in taxations:
        Paiement.objects.filter(taxation=taxation).delete()

        if a_jour:
            Paiement.objects.create(
                taxation=taxation,
                montant=taxation.montant_du,
                mode_paiement="MOBILE",
                statut_paiement="CONFIRME",
            )
            nouveau_statut = "A_JOUR"
        else:
            nouveau_statut = "EN_RETARD"

        if taxation.parcelle_id:
            taxation.parcelle.statut_fiscal = nouveau_statut
            taxation.parcelle.save(update_fields=["statut_fiscal"])


def creer_piece_jointe_factice(nom_fichier):
    return ContentFile(
        b"Document justificatif (donnee de demonstration academique).",
        name=nom_fichier,
    )


def nettoyer_comptes_orphelins():
    """Supprime les User 'citoyenN'/'exonerationN' crees lors d'une
    execution precedente interrompue en cours de route (User existe
    mais pas de Citoyen associe -- compte inutilisable)."""
    candidats = User.objects.filter(
        username__regex=r'^(citoyen[5-9]$|citoyen[1-9][0-9]$|citoyen1[0-9]{2}$|citoyen200$|exoneration[1-9][0-9]{0,2}$)'
    )
    n = 0
    for user in candidats:
        if not hasattr(user, "citoyen"):
            user.delete()
            n += 1
    if n:
        print(f"Nettoyage : {n} compte(s) orphelin(s) (execution precedente interrompue) supprime(s).\n")


def main():
    nettoyer_comptes_orphelins()

    NOMBRE_CITOYENS = 196
    NOMBRE_A_JOUR = 160

    taxations_citoyens = pool_taxations_disponibles(NOMBRE_CITOYENS)
    print(f"[Citoyens] {len(taxations_citoyens)} taxation(s) disponible(s) pour {NOMBRE_CITOYENS} demande(s).")

    indices_a_jour = set(random.sample(range(len(taxations_citoyens)), min(NOMBRE_A_JOUR, len(taxations_citoyens))))

    n_citoyens_crees = 0
    n_citoyens_deja_presents = 0
    n_a_jour = 0
    n_en_retard = 0

    for i, taxation in enumerate(taxations_citoyens):
        numero = i + 5
        username = f"citoyen{numero}"

        contribuable = lier_compte(username, taxation, str(numero))
        if contribuable is None:
            n_citoyens_deja_presents += 1
            continue

        a_jour = i in indices_a_jour
        forcer_statut_contribuable(contribuable, a_jour)

        if a_jour:
            n_a_jour += 1
        else:
            n_en_retard += 1
        n_citoyens_crees += 1

    print(f"[Citoyens] {n_citoyens_crees} compte(s) cree(s) ({n_a_jour} a jour, {n_en_retard} en retard).")
    print(f"[Citoyens] {n_citoyens_deja_presents} deja present(s) (ignore(s)).")
    print()

    NOMBRE_EXONERATIONS = 300
    NOMBRE_DEJA_VALIDEES = 230

    taxations_exo = pool_taxations_disponibles(NOMBRE_EXONERATIONS)
    print(f"[Exonérations] {len(taxations_exo)} taxation(s) disponible(s) pour {NOMBRE_EXONERATIONS} demande(s).")

    indices_validees = set(random.sample(range(len(taxations_exo)), min(NOMBRE_DEJA_VALIDEES, len(taxations_exo))))
    motifs = [
        DemandeExoneration.MOTIF_RELIGIEUX,
        DemandeExoneration.MOTIF_PUBLIC,
        DemandeExoneration.MOTIF_AUTRE,
    ]

    agent_traitant = User.objects.filter(is_staff=True).first()

    n_exo_crees = 0
    n_exo_deja_presents = 0
    n_validees = 0
    n_en_attente = 0

    for i, taxation in enumerate(taxations_exo):
        numero = i + 1
        username = f"exoneration{numero}"

        contribuable = lier_compte(username, taxation, f"Exo{numero}")
        if contribuable is None:
            n_exo_deja_presents += 1
            continue

        parcelle = taxation.parcelle
        est_validee = i in indices_validees

        demande = DemandeExoneration.objects.create(
            contribuable=contribuable,
            parcelle=parcelle,
            motif=random.choice(motifs),
            description="Demande generee automatiquement (donnee de demonstration academique).",
            piece_jointe=creer_piece_jointe_factice(f"justificatif_exoneration_{numero}.txt"),
            statut=DemandeExoneration.STATUT_VALIDEE if est_validee else DemandeExoneration.STATUT_SOUMISE,
        )

        if est_validee:
            demande.traite_par = agent_traitant
            demande.date_traitement = timezone.now()
            demande.save(update_fields=["traite_par", "date_traitement"])

            if parcelle:
                parcelle.statut_fiscal = "EXONERE"
                parcelle.save(update_fields=["statut_fiscal"])
            n_validees += 1
        else:
            n_en_attente += 1

        n_exo_crees += 1

    print(f"[Exonérations] {n_exo_crees} compte(s) cree(s) ({n_validees} deja validee(s), {n_en_attente} en attente).")
    print(f"[Exonérations] {n_exo_deja_presents} deja present(s) (ignore(s)).")


if __name__ == "__main__":
    main()