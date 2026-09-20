# ============================================================
# foncier/paiement_gateway.py
#
# Paiement en ligne d'une taxation, avec un système de "backend"
# interchangeable — même principe que foncier/sms.py.
#
#   - 'manuel' (par défaut) : simule un paiement immédiatement confirmé,
#     sans aucun appel réseau. Permet de tester tout le parcours citoyen
#     (choisir une taxation, "payer", recevoir un reçu) sans compte
#     marchand réel.
#   - 'orange_money' / 'wave' : points de départ pour les vraies API,
#     fournis à titre indicatif. ⚠️ NON TESTÉS ici faute d'un compte
#     marchand Orange Money / Wave réel — vérifiez le format exact des
#     requêtes dans leur documentation avant la mise en production :
#       Orange Money : https://developer.orange.com/apis/om-webpay-sn
#       Wave         : https://docs.wave.com/business
#
# FONCTIONNEMENT GÉNÉRAL (paiement en ligne réel) :
#   1. Le citoyen choisit une taxation à payer et un opérateur.
#   2. initier_paiement() crée un Paiement en base avec
#      statut_paiement='EN_ATTENTE', et retourne une URL vers laquelle
#      rediriger le citoyen (la page de paiement hébergée par
#      Orange/Wave).
#   3. Le citoyen paie sur le site de l'opérateur (hors de notre site).
#   4. L'opérateur notifie notre serveur via un "webhook" (voir
#      foncier/views.py : paiement_webhook_orange / paiement_webhook_wave)
#      qui marque le Paiement comme 'CONFIRME' ou 'ECHEC'.
#   5. Le citoyen est aussi redirigé vers une page de retour sur notre
#      site, qui affiche le statut actuel (utile s'il ferme l'onglet
#      avant la notification).
#
# UTILISATION dans le reste du code :
#
#     from foncier.paiement_gateway import initier_paiement
#     resultat = initier_paiement(taxation, montant, telephone, request)
#     if resultat["redirect_url"]:
#         return redirect(resultat["redirect_url"])
#     else:
#         # backend 'manuel' : déjà confirmé, pas de redirection externe
#         return redirect("citoyen_paiement_retour", pk=resultat["paiement"].pk)
# ============================================================

import logging
import uuid

from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class ManuelBackend:
    """Backend de développement/démonstration : confirme le paiement
    instantanément, sans aucun appel réseau ni compte marchand."""

    nom_affiche = "Paiement de démonstration"

    def initier(self, taxation, montant, telephone, request):
        from .models import Paiement  # import local pour éviter les imports circulaires

        paiement = Paiement.objects.create(
            taxation=taxation,
            montant=montant,
            mode_paiement='MOBILE',
            statut_paiement='EN_ATTENTE',
            reference_transaction=f"DEMO-{uuid.uuid4().hex[:10].upper()}",
        )
        return {"ok": True, "redirect_url": None, "paiement": paiement, "erreur": None}


class OrangeMoneyBackend:
    """
    Point de départ pour Orange Money Sénégal (Web Payment API).

    ⚠️ Non testé (aucun compte marchand Orange Money disponible dans cet
    environnement). Avant la mise en production :
      1. Souscrire à l'API Orange Money Web Payment sur
         https://developer.orange.com
      2. Récupérer merchant_key, client_id/client_secret et l'URL exacte
         de paiement (elle varie selon le pays/contrat).
      3. Renseigner PAIEMENT_ORANGE_* dans .env.
      4. Adapter le format de la requête ci-dessous à la documentation
         officielle reçue avec le compte marchand (les champs exacts
         peuvent différer de ce squelette).
    """

    nom_affiche = "Orange Money"

    def __init__(self):
        self.merchant_key = getattr(settings, "PAIEMENT_ORANGE_MERCHANT_KEY", "")
        self.client_id = getattr(settings, "PAIEMENT_ORANGE_CLIENT_ID", "")
        self.client_secret = getattr(settings, "PAIEMENT_ORANGE_CLIENT_SECRET", "")

    def initier(self, taxation, montant, telephone, request):
        from .models import Paiement

        if not (self.merchant_key and self.client_id and self.client_secret):
            return {
                "ok": False, "redirect_url": None, "paiement": None,
                "erreur": "Orange Money non configuré (identifiants manquants dans .env).",
            }

        paiement = Paiement.objects.create(
            taxation=taxation,
            montant=montant,
            mode_paiement='MOBILE',
            statut_paiement='EN_ATTENTE',
            reference_transaction=f"OM-{uuid.uuid4().hex[:10].upper()}",
        )

        try:
            # --- Squelette d'appel API, à adapter à la doc réelle Orange ---
            import json
            import urllib.request

            retour_url = request.build_absolute_uri(
                reverse("citoyen_paiement_retour", args=[paiement.pk])
            )
            notif_url = request.build_absolute_uri(reverse("paiement_webhook_orange"))

            corps = json.dumps({
                "merchant_key": self.merchant_key,
                "order_id": paiement.reference_transaction,
                "amount": str(montant),
                "currency": "XOF",
                "return_url": retour_url,
                "cancel_url": retour_url,
                "notif_url": notif_url,
            }).encode()

            requete = urllib.request.Request(
                "https://api.orange.com/orange-money-webpay/sn/v1/webpayment",
                data=corps,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(requete, timeout=10) as reponse:
                donnees = json.loads(reponse.read().decode())
                url_paiement = donnees.get("payment_url")

            if not url_paiement:
                raise ValueError("Réponse Orange Money sans payment_url.")

            return {"ok": True, "redirect_url": url_paiement, "paiement": paiement, "erreur": None}

        except Exception:
            logger.exception("Échec de l'initiation du paiement Orange Money (taxation #%s)", taxation.pk)
            paiement.statut_paiement = 'ECHEC'
            paiement.save(update_fields=["statut_paiement"])
            return {
                "ok": False, "redirect_url": None, "paiement": paiement,
                "erreur": "Le service Orange Money n'a pas répondu. Réessayez plus tard.",
            }


class WaveBackend:
    """
    Point de départ pour Wave Sénégal (Checkout API).

    ⚠️ Non testé (aucun compte marchand Wave disponible dans cet
    environnement). Avant la mise en production :
      1. Créer un compte Wave Business et récupérer une clé API sur
         https://www.wave.com/business
      2. Renseigner PAIEMENT_WAVE_API_KEY dans .env.
      3. Adapter le format de la requête à la documentation officielle
         (https://docs.wave.com/business) — ce squelette suit leur
         schéma "Checkout Sessions" tel que documenté publiquement, mais
         n'a pas pu être exécuté contre un vrai compte.
    """

    nom_affiche = "Wave"

    def __init__(self):
        self.api_key = getattr(settings, "PAIEMENT_WAVE_API_KEY", "")

    def initier(self, taxation, montant, telephone, request):
        from .models import Paiement

        if not self.api_key:
            return {
                "ok": False, "redirect_url": None, "paiement": None,
                "erreur": "Wave non configuré (clé API manquante dans .env).",
            }

        paiement = Paiement.objects.create(
            taxation=taxation,
            montant=montant,
            mode_paiement='MOBILE',
            statut_paiement='EN_ATTENTE',
            reference_transaction=f"WAVE-{uuid.uuid4().hex[:10].upper()}",
        )

        try:
            import json
            import urllib.request

            retour_url = request.build_absolute_uri(
                reverse("citoyen_paiement_retour", args=[paiement.pk])
            )

            corps = json.dumps({
                "amount": str(int(montant)),
                "currency": "XOF",
                "error_url": retour_url,
                "success_url": retour_url,
                "client_reference": paiement.reference_transaction,
            }).encode()

            requete = urllib.request.Request(
                "https://api.wave.com/v1/checkout/sessions",
                data=corps,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(requete, timeout=10) as reponse:
                donnees = json.loads(reponse.read().decode())
                url_paiement = donnees.get("wave_launch_url")

            if not url_paiement:
                raise ValueError("Réponse Wave sans wave_launch_url.")

            return {"ok": True, "redirect_url": url_paiement, "paiement": paiement, "erreur": None}

        except Exception:
            logger.exception("Échec de l'initiation du paiement Wave (taxation #%s)", taxation.pk)
            paiement.statut_paiement = 'ECHEC'
            paiement.save(update_fields=["statut_paiement"])
            return {
                "ok": False, "redirect_url": None, "paiement": paiement,
                "erreur": "Le service Wave n'a pas répondu. Réessayez plus tard.",
            }


BACKENDS = {
    "manuel": ManuelBackend,
    "orange_money": OrangeMoneyBackend,
    "wave": WaveBackend,
}


def get_backend(nom=None):
    backend_global = getattr(settings, "PAIEMENT_BACKEND", "manuel")
    if backend_global == "manuel":
        # Mode demo : simule TOUJOURS un paiement confirme, quel que soit
        # l'operateur choisi par le citoyen (Orange Money/Wave), pour ne
        # jamais exiger de vraies cles API tant que le projet est en
        # developpement/demonstration.
        return ManuelBackend()
    nom = nom or backend_global
    return BACKENDS.get(nom, ManuelBackend)()


def initier_paiement(taxation, montant, telephone, request, backend=None):
    """Point d'entrée principal : initie un paiement pour une taxation via
    le backend demandé (ou celui configuré dans settings.PAIEMENT_BACKEND
    par défaut). Retourne un dict {ok, redirect_url, paiement, erreur}."""
    return get_backend(backend).initier(taxation, montant, telephone, request)
