# -*- coding: utf-8 -*-
import io

# ============================================================
# 1) kmsn/settings.py : ajouter les secrets de verification des
#    webhooks (Wave : signature HMAC officielle ; Orange : jeton
#    secret dans l'URL, faute de signature publique documentee).
# ============================================================
chemin_settings = "kmsn/settings.py"
with io.open(chemin_settings, "r", encoding="utf-8") as f:
    contenu_settings = f.read()

ancienne_ligne_settings = "PAIEMENT_WAVE_API_KEY = os.environ.get('PAIEMENT_WAVE_API_KEY', '')"

nouvelle_ligne_settings = """PAIEMENT_WAVE_API_KEY = os.environ.get('PAIEMENT_WAVE_API_KEY', '')
# Secret du webhook Wave (different de la cle API ci-dessus). Genere dans
# le Business Portal Wave > Developers > Webhooks, affiche une seule fois.
# Sert a verifier l'en-tete "Wave-Signature" (voir docs.wave.com/webhook).
PAIEMENT_WAVE_WEBHOOK_SECRET = os.environ.get('PAIEMENT_WAVE_WEBHOOK_SECRET', '')
# Orange Money ne fournit pas de signature cryptographique publique et
# documentee pour cette integration. A la place, on protege l'URL du
# webhook par un jeton secret choisi ici : il doit etre recopie dans
# l'URL de notification configuree cote Orange (back-office marchand),
# sous la forme /paiements/webhook/orange/<CE_JETON>/.
PAIEMENT_ORANGE_WEBHOOK_TOKEN = os.environ.get('PAIEMENT_ORANGE_WEBHOOK_TOKEN', '')"""

nb = contenu_settings.count(ancienne_ligne_settings)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre PAIEMENT_WAVE_API_KEY trouvee {nb} fois (attendu 1) "
        f"dans settings.py. Rien n'a ete modifie."
    )
contenu_settings = contenu_settings.replace(ancienne_ligne_settings, nouvelle_ligne_settings)

with io.open(chemin_settings, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_settings)

# ============================================================
# 2) foncier/urls.py : l'URL du webhook Orange porte maintenant
#    le jeton secret en tant que segment d'URL.
# ============================================================
chemin_urls = "foncier/urls.py"
with io.open(chemin_urls, "r", encoding="utf-8") as f:
    contenu_urls = f.read()

ancienne_route = "    path('paiements/webhook/orange/', views.paiement_webhook_orange, name='paiement_webhook_orange'),"
nouvelle_route = "    path('paiements/webhook/orange/<str:jeton_secret>/', views.paiement_webhook_orange, name='paiement_webhook_orange'),"

nb = contenu_urls.count(ancienne_route)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre de route Orange trouvee {nb} fois (attendu 1) dans urls.py. "
        f"Rien n'a ete modifie."
    )
contenu_urls = contenu_urls.replace(ancienne_route, nouvelle_route)

with io.open(chemin_urls, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_urls)

# ============================================================
# 3) foncier/views.py : verification reelle des deux webhooks.
# ============================================================
chemin_views = "foncier/views.py"
with io.open(chemin_views, "r", encoding="utf-8") as f:
    contenu_views = f.read()

ancien_bloc = """# ⚠️ Les deux vues ci-dessous n'ont pas pu être testées contre de vrais
# appels Orange Money / Wave (aucun compte marchand disponible ici).
# La vérification de signature/authenticité du webhook — INDISPENSABLE
# en production pour empêcher quiconque de "confirmer" un faux paiement
# en appelant cette URL directement — doit être ajoutée en suivant la
# documentation officielle de chaque opérateur avant la mise en ligne.
# ============================================================

@csrf_exempt
@require_POST
def paiement_webhook_orange(request):
    return _traiter_webhook_paiement(request, "OM-")


@csrf_exempt
@require_POST
def paiement_webhook_wave(request):
    return _traiter_webhook_paiement(request, "WAVE-")


def _traiter_webhook_paiement(request, prefixe_attendu):
    try:
        donnees = json.loads(request.body.decode() or "{}")
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    # TODO : vérifier ici la signature/authenticité du webhook selon la
    # documentation de l'opérateur avant de faire confiance à "donnees".

    reference = donnees.get("order_id") or donnees.get("client_reference") or ""
    statut_recu = str(donnees.get("status", "")).upper()

    if not reference.startswith(prefixe_attendu):
        return HttpResponse(status=400)

    paiement = None
    try:
        paiement = Paiement.objects.get(reference_transaction=reference)
    except Paiement.DoesNotExist:
        return HttpResponse(status=404)

    if paiement.statut_paiement != 'EN_ATTENTE':
        # Déjà traité (webhook rejoué) : on répond OK sans rien refaire.
        return HttpResponse(status=200)

    if statut_recu in ("SUCCESS", "SUCCESSFUL", "CONFIRME", "PAID"):
        paiement.statut_paiement = 'CONFIRME'
    else:
        paiement.statut_paiement = 'ECHEC'
    paiement.save(update_fields=["statut_paiement"])

    return HttpResponse(status=200)"""

nouveau_bloc = """# ⚠️ Vérification de l'authenticité des webhooks de paiement :
#
# - Wave documente officiellement un en-tête "Wave-Signature" (voir
#   https://docs.wave.com/webhook) : HMAC-SHA256(secret, horodatage +
#   corps_brut), avec rejet des requêtes trop anciennes (> 5 minutes).
#   C'est ce que _verifier_signature_wave() implémente ci-dessous.
#
# - Orange Money ne fournit pas de signature cryptographique publique
#   et documentée pour l'intégration utilisée ici. Pour ne pas inventer
#   un mécanisme de vérification non confirmé, l'URL du webhook Orange
#   est à la place protégée par un jeton secret inclus dans l'URL elle-
#   même (PAIEMENT_ORANGE_WEBHOOK_TOKEN) : seule la personne qui
#   configure l'URL de notification dans le back-office Orange connaît
#   cette URL. Si Orange publie un jour un mécanisme de signature
#   documenté pour ce produit, remplacer cette vérification par la
#   leur sera simple (un seul endroit à changer : paiement_webhook_orange).
#
# Aucun des deux mécanismes n'a pu être testé contre de vrais appels
# (aucun compte marchand réel disponible ici) : à vérifier en conditions
# réelles avant la mise en production.
# ============================================================

@csrf_exempt
@require_POST
def paiement_webhook_orange(request, jeton_secret):
    import hmac

    jeton_attendu = getattr(settings, 'PAIEMENT_ORANGE_WEBHOOK_TOKEN', '') or ''
    if not jeton_attendu or not hmac.compare_digest(jeton_secret, jeton_attendu):
        # Jeton absent de la configuration, ou jeton incorrect dans l'URL
        # appelée : on refuse plutôt que de faire confiance au corps de la
        # requête, Orange Money ne fournissant pas de signature vérifiable
        # pour cette intégration.
        return HttpResponse(status=403)
    return _traiter_webhook_paiement(request, "OM-")


@csrf_exempt
@require_POST
def paiement_webhook_wave(request):
    if not _verifier_signature_wave(request):
        return HttpResponse(status=403)
    return _traiter_webhook_paiement(request, "WAVE-")


def _verifier_signature_wave(request):
    \"\"\"Vérifie l'en-tête Wave-Signature selon la documentation officielle
    (https://docs.wave.com/webhook) :
      - format "t=<horodatage>,v1=<signature hex>[,v1=<autre signature>...]"
      - signature attendue = HMAC-SHA256(secret, horodatage + corps_brut),
        encodée en hexadécimal
      - requête refusée si l'horodatage a plus de 5 minutes (anti-rejeu)
    \"\"\"
    import hmac
    import hashlib
    import time

    secret = getattr(settings, 'PAIEMENT_WAVE_WEBHOOK_SECRET', '') or ''
    if not secret:
        return False

    en_tete = request.META.get('HTTP_WAVE_SIGNATURE', '')
    if not en_tete:
        return False

    horodatage = None
    signatures_recues = []
    for partie in en_tete.split(','):
        partie = partie.strip()
        if partie.startswith('t='):
            horodatage = partie[2:]
        elif partie.startswith('v1='):
            signatures_recues.append(partie[3:])

    if not horodatage or not signatures_recues:
        return False

    try:
        horodatage_int = int(horodatage)
    except ValueError:
        return False

    if abs(time.time() - horodatage_int) > 300:
        # Horodatage de plus de 5 minutes : requête trop ancienne, on
        # refuse par précaution contre une attaque par rejeu.
        return False

    corps_brut = request.body or b""
    message = (horodatage + corps_brut.decode('utf-8', errors='replace')).encode('utf-8')
    signature_calculee = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

    for signature in signatures_recues:
        if hmac.compare_digest(signature_calculee, signature):
            return True
    return False


def _traiter_webhook_paiement(request, prefixe_attendu):
    try:
        donnees = json.loads(request.body.decode() or "{}")
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    reference = donnees.get("order_id") or donnees.get("client_reference") or ""
    statut_recu = str(donnees.get("status", "")).upper()

    if not reference.startswith(prefixe_attendu):
        return HttpResponse(status=400)

    paiement = None
    try:
        paiement = Paiement.objects.get(reference_transaction=reference)
    except Paiement.DoesNotExist:
        return HttpResponse(status=404)

    if paiement.statut_paiement != 'EN_ATTENTE':
        # Déjà traité (webhook rejoué) : on répond OK sans rien refaire.
        return HttpResponse(status=200)

    if statut_recu in ("SUCCESS", "SUCCESSFUL", "CONFIRME", "PAID"):
        paiement.statut_paiement = 'CONFIRME'
    else:
        paiement.statut_paiement = 'ECHEC'
    paiement.save(update_fields=["statut_paiement"])

    return HttpResponse(status=200)"""

nb = contenu_views.count(ancien_bloc)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre des webhooks trouvee {nb} fois (attendu 1) dans views.py. "
        f"Rien n'a ete modifie."
    )
contenu_views = contenu_views.replace(ancien_bloc, nouveau_bloc)

with io.open(chemin_views, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_views)

# ============================================================
# 4) foncier/paiement_gateway.py : l'URL de notification envoyee
#    a Orange doit maintenant inclure le jeton secret.
# ============================================================
chemin_gateway = "foncier/paiement_gateway.py"
with io.open(chemin_gateway, "r", encoding="utf-8") as f:
    contenu_gateway = f.read()

ancienne_ligne_gateway = '            notif_url = request.build_absolute_uri(reverse("paiement_webhook_orange"))\n'
nouvelle_ligne_gateway = (
    '            notif_url = request.build_absolute_uri(\n'
    '                reverse("paiement_webhook_orange", args=[settings.PAIEMENT_ORANGE_WEBHOOK_TOKEN])\n'
    '            )\n'
)

nb = contenu_gateway.count(ancienne_ligne_gateway)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre notif_url trouvee {nb} fois (attendu 1) dans paiement_gateway.py. "
        f"Rien n'a ete modifie."
    )
contenu_gateway = contenu_gateway.replace(ancienne_ligne_gateway, nouvelle_ligne_gateway)

with io.open(chemin_gateway, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_gateway)

print("OK : settings.py, urls.py, views.py et paiement_gateway.py ont ete mis a jour.")