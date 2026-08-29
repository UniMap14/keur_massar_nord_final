# ============================================================
# foncier/audit.py
#
# Journal d'audit automatique : à chaque création, modification ou
# suppression d'un objet parmi les modèles listés dans TRACKED_MODELS,
# une entrée est écrite dans JournalAudit, avec qui a fait le
# changement (via foncier/middleware.py) et quels champs ont changé.
#
# Pour ajouter un modèle à surveiller, ajoutez-le simplement dans
# TRACKED_MODELS ci-dessous avec la liste des champs à suivre.
# ============================================================

import logging

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .middleware import get_utilisateur_courant, get_ip_courante

logger = logging.getLogger(__name__)

# Modèle -> liste des champs dont on veut suivre les changements.
# (on ne suit pas TOUS les champs pour ne pas noyer le journal sous du
# bruit sans intérêt, ex: date_maj qui change à chaque sauvegarde)
TRACKED_MODELS = {
    "Parcelle": [
        "nicad", "statut_fiscal", "montant_taxe_annuelle", "valeur_locative",
        "type_document", "reference_arrete", "occupation_sol",
        "adresse_parcelle", "proprietaire_id", "zone_id",
    ],
    "Taxation": ["montant_du"],
    "Paiement": ["statut_paiement", "montant"],
    "Contribuable": ["nom", "prenom", "telephone", "numero_fiscal", "proprietaire_id"],
    "Signalement": ["statut", "agent_assigne_id", "commentaire_agent"],
    "DemandeService": ["statut", "agent_traitant_id", "commentaire_agent"],
}


def _valeur_lisible(valeur):
    """Convertit une valeur de champ en texte lisible pour le journal
    (les Decimal/date s'affichent mal tels quels en JSON)."""
    if valeur is None:
        return None
    return str(valeur)


def _creer_entree(action, instance, champs_modifies=None):
    from .models import JournalAudit  # import local : évite les imports circulaires

    try:
        JournalAudit.objects.create(
            utilisateur=get_utilisateur_courant() if get_utilisateur_courant() and get_utilisateur_courant().is_authenticated else None,
            action=action,
            modele=instance.__class__.__name__,
            objet_id=str(instance.pk),
            objet_repr=str(instance)[:255],
            champs_modifies=champs_modifies,
            adresse_ip=get_ip_courante(),
        )
    except Exception:
        # Le journal d'audit ne doit JAMAIS faire planter une sauvegarde
        # métier — en cas de souci (ex: table pas encore migrée), on
        # journalise l'erreur côté serveur et on continue.
        logger.exception("Échec de l'écriture dans le journal d'audit pour %s", instance)


@receiver(pre_save)
def _capturer_avant_modification(sender, instance, **kwargs):
    nom_modele = sender.__name__
    if nom_modele not in TRACKED_MODELS or not instance.pk:
        return  # modèle non suivi, ou création (rien à comparer)

    try:
        ancien = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    diff = {}
    for champ in TRACKED_MODELS[nom_modele]:
        ancienne_valeur = getattr(ancien, champ, None)
        nouvelle_valeur = getattr(instance, champ, None)
        if ancienne_valeur != nouvelle_valeur:
            diff[champ] = [_valeur_lisible(ancienne_valeur), _valeur_lisible(nouvelle_valeur)]

    # Stocké temporairement sur l'instance, lu par le signal post_save
    # juste après (qui sait si la sauvegarde a réussi).
    instance._diff_audit = diff


@receiver(post_save)
def _journaliser_sauvegarde(sender, instance, created, **kwargs):
    nom_modele = sender.__name__
    if nom_modele not in TRACKED_MODELS:
        return

    if created:
        _creer_entree("CREATION", instance)
        return

    diff = getattr(instance, "_diff_audit", None)
    if diff:  # rien à journaliser si aucun champ suivi n'a changé
        _creer_entree("MODIFICATION", instance, champs_modifies=diff)


@receiver(post_delete)
def _journaliser_suppression(sender, instance, **kwargs):
    nom_modele = sender.__name__
    if nom_modele not in TRACKED_MODELS:
        return
    _creer_entree("SUPPRESSION", instance)
