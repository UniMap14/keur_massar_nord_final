# ============================================================
# foncier/sms.py
#
# Envoi de SMS, avec un système de "backend" interchangeable — même
# principe que EMAIL_BACKEND dans Django.
#
#   - En développement (par défaut) : le SMS s'affiche dans la
#     console au lieu d'être réellement envoyé, comme pour les emails.
#   - En production : brancher un vrai fournisseur en définissant
#     SMS_BACKEND dans .env. Un backend pour l'API Orange SMS Sénégal
#     est fourni ci-dessous à titre de point de départ (voir
#     OrangeSMSBackend), mais N'A PAS PU ÊTRE TESTÉ ici faute d'un
#     compte Orange Developer réel — vérifiez le format exact de
#     l'API dans leur documentation avant la mise en production :
#     https://developer.orange.com/apis/sms-sn
#
# UTILISATION dans le reste du code :
#
#     from foncier.sms import envoyer_sms
#     envoyer_sms("+221771234567", "Votre signalement est résolu.")
#
# La fonction ne lève jamais d'exception en cas d'échec d'envoi (un
# SMS qui ne part pas ne doit jamais faire planter une page) : elle
# retourne simplement True/False et journalise l'erreur.
# ============================================================

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class ConsoleSMSBackend:
    """Backend de développement : affiche le SMS dans la console/les logs
    au lieu de l'envoyer réellement (équivalent SMS du EmailBackend console
    de Django)."""

    def envoyer(self, numero, message):
        print(f"\n[SMS - mode console, aucun envoi réel]\nÀ : {numero}\nMessage : {message}\n")
        return True


class OrangeSMSBackend:
    """
    Backend pour l'API Orange SMS Sénégal (Orange Developer).

    ⚠️ Point de départ non testé (aucun identifiant Orange Developer
    disponible dans cet environnement). Avant la mise en production :
      1. Créer un compte sur https://developer.orange.com
      2. Souscrire à l'API "SMS Sénégal", récupérer client_id/client_secret
         et le numéro expéditeur autorisé.
      3. Vérifier le format exact des requêtes dans leur documentation
         (l'authentification OAuth2 et le endpoint peuvent évoluer).
      4. Renseigner les variables SMS_ORANGE_* dans .env.
    """

    TOKEN_URL = "https://api.orange.com/oauth/v3/token"
    SEND_URL_TEMPLATE = "https://api.orange.com/smsmessaging/v1/outbound/{sender}/requests"

    def __init__(self):
        self.client_id = getattr(settings, "SMS_ORANGE_CLIENT_ID", "")
        self.client_secret = getattr(settings, "SMS_ORANGE_CLIENT_SECRET", "")
        self.sender = getattr(settings, "SMS_ORANGE_SENDER", "")

    def _obtenir_token(self):
        import base64
        import json
        import urllib.request
        import urllib.error

        identifiants = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        requete = urllib.request.Request(
            self.TOKEN_URL,
            data=b"grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {identifiants}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(requete, timeout=10) as reponse:
            donnees = json.loads(reponse.read().decode())
            return donnees.get("access_token")

    def envoyer(self, numero, message):
        import json
        import urllib.request
        import urllib.error

        if not (self.client_id and self.client_secret and self.sender):
            logger.warning(
                "SMS non envoyé : identifiants Orange (SMS_ORANGE_CLIENT_ID / "
                "SMS_ORANGE_CLIENT_SECRET / SMS_ORANGE_SENDER) non configurés dans .env."
            )
            return False

        try:
            token = self._obtenir_token()
            url = self.SEND_URL_TEMPLATE.format(sender=self.sender)
            corps = json.dumps({
                "outboundSMSMessageRequest": {
                    "address": f"tel:{numero}",
                    "senderAddress": f"tel:{self.sender}",
                    "outboundSMSTextMessage": {"message": message},
                }
            }).encode()

            requete = urllib.request.Request(
                url,
                data=corps,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(requete, timeout=10) as reponse:
                return 200 <= reponse.status < 300
        except Exception:
            logger.exception("Échec de l'envoi du SMS via l'API Orange à %s", numero)
            return False


BACKENDS = {
    "console": ConsoleSMSBackend,
    "orange": OrangeSMSBackend,
}


def envoyer_sms(numero, message):
    """Envoie un SMS via le backend configuré dans settings.SMS_BACKEND
    ('console' par défaut). Ne lève jamais d'exception : retourne True/False.
    Ne fait rien (retourne False) si numero est vide."""
    if not numero:
        return False

    nom_backend = getattr(settings, "SMS_BACKEND", "console")
    backend_cls = BACKENDS.get(nom_backend, ConsoleSMSBackend)

    try:
        return backend_cls().envoyer(numero, message)
    except Exception:
        logger.exception("Échec de l'envoi du SMS à %s", numero)
        return False
