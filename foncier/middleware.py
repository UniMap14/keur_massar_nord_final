# ============================================================
# foncier/middleware.py
#
# Les signaux Django (pre_save, post_save...) n'ont pas accès à la
# requête HTTP en cours, donc pas moyen de savoir "qui" a fait le
# changement directement. Ce middleware garde une trace légère
# (thread-local) de l'utilisateur et de l'adresse IP de la requête en
# cours, que foncier/audit.py va lire au moment d'écrire dans le
# journal d'audit.
# ============================================================

import threading

_local = threading.local()


def get_utilisateur_courant():
    return getattr(_local, "utilisateur", None)


def get_ip_courante():
    return getattr(_local, "ip", None)


def _adresse_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.utilisateur = getattr(request, "user", None)
        _local.ip = _adresse_ip(request)
        try:
            return self.get_response(request)
        finally:
            _local.utilisateur = None
            _local.ip = None
