# -*- coding: utf-8 -*-
import io

# ============================================================
# 1) foncier/dashboard_views.py : remplace le reset par lien
#    (templates manquants, jamais fonctionnel) par un reset par
#    code a 6 chiffres envoye par email (meme principe que l'OTP
#    des citoyens).
# ============================================================
chemin_views = "foncier/dashboard_views.py"
with io.open(chemin_views, "r", encoding="utf-8") as f:
    contenu_views = f.read()

marqueur_debut = "# MOT DE PASSE OUBLIÉ"
marqueur_fin = "# ------------------------------------------------------------\n# TABLEAU DE BORD (accueil)"

nb_debut = contenu_views.count(marqueur_debut)
nb_fin = contenu_views.count(marqueur_fin)
if nb_debut != 1 or nb_fin != 1:
    raise SystemExit(
        f"ARRET : marqueur debut trouve {nb_debut} fois, marqueur fin trouve {nb_fin} fois "
        f"(attendu 1 chacun) dans dashboard_views.py. Rien n'a ete modifie."
    )

idx_debut = contenu_views.index(marqueur_debut)
idx_fin = contenu_views.index(marqueur_fin)
if idx_fin <= idx_debut:
    raise SystemExit("ARRET : ordre des marqueurs incoherent. Rien n'a ete modifie.")

nouveau_bloc = '''# MOT DE PASSE OUBLIÉ (code par email, 2 étapes)
#
# 1. dashboard_password_reset_demande  -> saisie de l'email, envoi du code
# 2. dashboard_password_reset_code     -> saisie du code + nouveau mdp
#
# Même principe que le code OTP de connexion des citoyens (voir
# citoyens/views.py : _generer_otp / _envoyer_otp), mais pour les
# comptes agents (is_staff=True) qui ont oublié leur mot de passe.
# Le code est stocké en session (pas en base), valable 10 minutes,
# avec un maximum de 5 tentatives avant de devoir recommencer.
# ------------------------------------------------------------

def dashboard_password_reset_demande(request):
    """Étape 1 : saisie de l'email. Si un compte agent (is_staff) a cet
    email, génère un code à 6 chiffres et l'envoie par email."""
    import random
    import time
    from django.core.mail import send_mail
    from django.conf import settings

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        compte = User.objects.filter(email__iexact=email, is_staff=True).first()

        if compte is not None:
            code = str(random.randint(100000, 999999))
            request.session["reset_user_id"] = compte.pk
            request.session["reset_code"] = code
            request.session["reset_expire"] = time.time() + 600
            request.session["reset_tentatives"] = 0
            try:
                send_mail(
                    subject="[KEUR MASSAR NORD] Code de réinitialisation du mot de passe",
                    message=(
                        "Bonjour,\\n\\n"
                        f"Voici votre code de réinitialisation de mot de passe : {code}\\n"
                        "Ce code est valable 10 minutes.\\n\\n"
                        "Si vous n'avez pas demandé cette réinitialisation, ignorez cet email."
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[compte.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            return redirect("dashboard_password_reset_code")

        # Email inconnu ou compte non-agent : même message, pour ne pas
        # révéler quels emails existent (anti-énumération de comptes).
        messages.info(
            request,
            "Si cet email correspond à un compte agent, un code de "
            "réinitialisation vient d'être envoyé.",
        )

    return render(request, "registration/password_reset_form.html")


def dashboard_password_reset_code(request):
    """Étape 2 : saisie du code reçu par email + nouveau mot de passe."""
    import time
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError as DjangoValidationError

    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("dashboard_password_reset")

    erreur = None

    if request.method == "POST":
        code_saisi = request.POST.get("code", "").strip()
        mdp1 = request.POST.get("new_password1", "")
        mdp2 = request.POST.get("new_password2", "")
        expire = request.session.get("reset_expire", 0)
        tentatives = request.session.get("reset_tentatives", 0)

        cles_session = ["reset_user_id", "reset_code", "reset_expire", "reset_tentatives"]

        if time.time() > expire:
            erreur = "Ce code a expiré. Veuillez recommencer."
            for cle in cles_session:
                request.session.pop(cle, None)
        elif tentatives >= 5:
            erreur = "Trop de tentatives incorrectes. Veuillez recommencer."
            for cle in cles_session:
                request.session.pop(cle, None)
        elif not code_saisi or code_saisi != request.session.get("reset_code"):
            request.session["reset_tentatives"] = tentatives + 1
            erreur = "Code incorrect."
        elif not mdp1 or mdp1 != mdp2:
            erreur = "Les deux mots de passe ne correspondent pas."
        else:
            try:
                validate_password(mdp1)
            except DjangoValidationError as exc:
                erreur = " ".join(exc.messages)

            if not erreur:
                compte = User.objects.get(pk=user_id)
                compte.set_password(mdp1)
                compte.save(update_fields=["password"])
                for cle in cles_session:
                    request.session.pop(cle, None)
                messages.success(
                    request,
                    "Votre mot de passe a été réinitialisé. Vous pouvez vous connecter.",
                )
                return redirect("dashboard_login")

    return render(request, "registration/password_reset_code.html", {"erreur": erreur})


def dashboard_password_reset_renvoyer(request):
    """Renvoie un nouveau code (invalide l'ancien)."""
    import random
    import time
    from django.core.mail import send_mail
    from django.conf import settings

    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("dashboard_password_reset")

    compte = User.objects.get(pk=user_id)
    code = str(random.randint(100000, 999999))
    request.session["reset_code"] = code
    request.session["reset_expire"] = time.time() + 600
    request.session["reset_tentatives"] = 0
    try:
        send_mail(
            subject="[KEUR MASSAR NORD] Nouveau code de réinitialisation",
            message=(
                "Bonjour,\\n\\n"
                f"Voici votre nouveau code de réinitialisation : {code}\\n"
                "Ce code est valable 10 minutes."
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[compte.email],
            fail_silently=True,
        )
    except Exception:
        pass
    messages.info(request, "Un nouveau code vous a été envoyé.")
    return redirect("dashboard_password_reset_code")


'''

contenu_views = contenu_views[:idx_debut] + nouveau_bloc + contenu_views[idx_fin:]

with io.open(chemin_views, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_views)

# ============================================================
# 2) foncier/dashboard_urls.py : nouvelles routes (2 etapes au
#    lieu de 4).
# ============================================================
chemin_urls = "foncier/dashboard_urls.py"
with io.open(chemin_urls, "r", encoding="utf-8") as f:
    contenu_urls = f.read()

ancien_bloc_urls = '''    # --- Mot de passe oublié (4 étapes) ---
    path(
        "mot-de-passe-oublie/",
        views.DashboardPasswordResetView.as_view(),
        name="dashboard_password_reset",
    ),
    path(
        "mot-de-passe-oublie/envoye/",
        views.DashboardPasswordResetDoneView.as_view(),
        name="dashboard_password_reset_done",
    ),
    path(
        "reinitialiser/<uidb64>/<token>/",
        views.DashboardPasswordResetConfirmView.as_view(),
        name="dashboard_password_reset_confirm",
    ),
    path(
        "reinitialiser/termine/",
        views.DashboardPasswordResetCompleteView.as_view(),
        name="dashboard_password_reset_complete",
    ),'''

nouveau_bloc_urls = '''    # --- Mot de passe oublié (code par email, 2 étapes) ---
    path(
        "mot-de-passe-oublie/",
        views.dashboard_password_reset_demande,
        name="dashboard_password_reset",
    ),
    path(
        "mot-de-passe-oublie/code/",
        views.dashboard_password_reset_code,
        name="dashboard_password_reset_code",
    ),
    path(
        "mot-de-passe-oublie/renvoyer/",
        views.dashboard_password_reset_renvoyer,
        name="dashboard_password_reset_renvoyer",
    ),'''

nb = contenu_urls.count(ancien_bloc_urls)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre des routes mot de passe oublie trouvee {nb} fois (attendu 1) "
        f"dans dashboard_urls.py. Rien n'a ete modifie."
    )
contenu_urls = contenu_urls.replace(ancien_bloc_urls, nouveau_bloc_urls)

with io.open(chemin_urls, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_urls)

# ============================================================
# 3) Nouveaux templates (meme charte visuelle sombre/doree que
#    dashboard/login.html).
# ============================================================
import os
os.makedirs("foncier/templates/registration", exist_ok=True)

template_form = '''{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="robots" content="noindex, nofollow">
  <title>Mot de passe oublié · KEUR MASSAR NORD Admin</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    :root { --gold-primary:#eab308; --gold-hover:#ca8a04; --card-bg:#141414; --input-bg:#1e1e20; --border-soft:#333336; --text-white:#ffffff; --text-muted:#a1a1aa; }
    * { box-sizing:border-box; margin:0; padding:0; }
    body { font-family:'Inter', sans-serif; color:var(--text-white); background:#0d0d0d; }
    .login-shell { min-height:100dvh; display:flex; align-items:center; justify-content:center; padding:24px 16px; }
    .login-card { width:100%; max-width:460px; background:var(--card-bg); border-radius:28px; padding:40px 36px; box-shadow:0 30px 60px -12px rgba(0,0,0,.9); border:1px solid rgba(255,255,255,.08); }
    h1 { font-size:22px; font-weight:600; text-align:center; margin-bottom:10px; }
    p.sub { text-align:center; color:var(--text-muted); font-size:13.5px; margin-bottom:28px; }
    .form-field { margin-bottom:18px; }
    .field-input-wrap { position:relative; display:flex; align-items:center; }
    .field-input-wrap input { width:100%; background:var(--input-bg); border:1px solid var(--border-soft); border-radius:12px; padding:14px 16px 14px 46px; font-size:15px; color:var(--text-white); }
    .field-input-wrap input:focus { outline:none; border-color:var(--gold-primary); box-shadow:0 0 0 3px rgba(234,179,8,.18); }
    .field-input-wrap .field-icon { position:absolute; left:16px; color:var(--gold-primary); font-size:15px; }
    .btn-submit { width:100%; border:none; border-radius:12px; background:var(--gold-primary); color:#000; font-weight:700; font-size:15px; padding:15px; cursor:pointer; margin-top:8px; }
    .btn-submit:hover { background:var(--gold-hover); }
    .back-link { display:block; text-align:center; margin-top:22px; color:var(--text-muted); font-size:13.5px; text-decoration:none; }
    .back-link:hover { color:var(--gold-primary); }
    .msg { background:rgba(234,179,8,.12); border:1px solid var(--gold-primary); color:#fde68a; font-size:13.5px; border-radius:12px; padding:12px 16px; margin-bottom:20px; }
  </style>
</head>
<body>
<div class="login-shell">
  <div class="login-card">
    <h1>Mot de passe oublié</h1>
    <p class="sub">Entrez l'adresse email de votre compte agent. Un code à 6 chiffres vous sera envoyé.</p>

    {% if messages %}
      {% for message in messages %}<div class="msg">{{ message }}</div>{% endfor %}
    {% endif %}

    <form method="post" novalidate>
      {% csrf_token %}
      <div class="form-field">
        <div class="field-input-wrap">
          <i class="fa-solid fa-envelope field-icon"></i>
          <input type="email" name="email" placeholder="Email" required autofocus>
        </div>
      </div>
      <button type="submit" class="btn-submit">Envoyer le code</button>
    </form>
    <a href="{% url 'dashboard_login' %}" class="back-link"><i class="fa-solid fa-arrow-left"></i> Retour à la connexion</a>
  </div>
</div>
</body>
</html>
'''

template_code = '''{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="robots" content="noindex, nofollow">
  <title>Réinitialiser le mot de passe · KEUR MASSAR NORD Admin</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    :root { --gold-primary:#eab308; --gold-hover:#ca8a04; --card-bg:#141414; --input-bg:#1e1e20; --border-soft:#333336; --text-white:#ffffff; --text-muted:#a1a1aa; --error:#ef4444; }
    * { box-sizing:border-box; margin:0; padding:0; }
    body { font-family:'Inter', sans-serif; color:var(--text-white); background:#0d0d0d; }
    .login-shell { min-height:100dvh; display:flex; align-items:center; justify-content:center; padding:24px 16px; }
    .login-card { width:100%; max-width:460px; background:var(--card-bg); border-radius:28px; padding:40px 36px; box-shadow:0 30px 60px -12px rgba(0,0,0,.9); border:1px solid rgba(255,255,255,.08); }
    h1 { font-size:22px; font-weight:600; text-align:center; margin-bottom:10px; }
    p.sub { text-align:center; color:var(--text-muted); font-size:13.5px; margin-bottom:26px; }
    .form-field { margin-bottom:16px; }
    .field-input-wrap { position:relative; display:flex; align-items:center; }
    .field-input-wrap input { width:100%; background:var(--input-bg); border:1px solid var(--border-soft); border-radius:12px; padding:14px 16px 14px 46px; font-size:15px; color:var(--text-white); }
    .field-input-wrap input:focus { outline:none; border-color:var(--gold-primary); box-shadow:0 0 0 3px rgba(234,179,8,.18); }
    .field-input-wrap .field-icon { position:absolute; left:16px; color:var(--gold-primary); font-size:15px; }
    .btn-submit { width:100%; border:none; border-radius:12px; background:var(--gold-primary); color:#000; font-weight:700; font-size:15px; padding:15px; cursor:pointer; margin-top:8px; }
    .btn-submit:hover { background:var(--gold-hover); }
    .back-link, .resend-link { display:block; text-align:center; margin-top:16px; color:var(--text-muted); font-size:13.5px; text-decoration:none; }
    .back-link:hover, .resend-link:hover { color:var(--gold-primary); }
    .flash-error { background:rgba(239,68,68,.15); border:1px solid var(--error); color:#fca5a5; font-size:13.5px; border-radius:12px; padding:12px 16px; margin-bottom:20px; }
  </style>
</head>
<body>
<div class="login-shell">
  <div class="login-card">
    <h1>Réinitialiser le mot de passe</h1>
    <p class="sub">Entrez le code à 6 chiffres reçu par email, puis votre nouveau mot de passe.</p>

    {% if erreur %}<div class="flash-error">{{ erreur }}</div>{% endif %}

    <form method="post" novalidate>
      {% csrf_token %}
      <div class="form-field">
        <div class="field-input-wrap">
          <i class="fa-solid fa-key field-icon"></i>
          <input type="text" name="code" placeholder="Code à 6 chiffres" required autofocus maxlength="6" inputmode="numeric">
        </div>
      </div>
      <div class="form-field">
        <div class="field-input-wrap">
          <i class="fa-solid fa-lock field-icon"></i>
          <input type="password" name="new_password1" placeholder="Nouveau mot de passe" required autocomplete="new-password">
        </div>
      </div>
      <div class="form-field">
        <div class="field-input-wrap">
          <i class="fa-solid fa-lock field-icon"></i>
          <input type="password" name="new_password2" placeholder="Confirmer le mot de passe" required autocomplete="new-password">
        </div>
      </div>
      <button type="submit" class="btn-submit">Réinitialiser le mot de passe</button>
    </form>
    <a href="{% url 'dashboard_password_reset_renvoyer' %}" class="resend-link">Je n'ai pas reçu de code — renvoyer</a>
    <a href="{% url 'dashboard_login' %}" class="back-link"><i class="fa-solid fa-arrow-left"></i> Retour à la connexion</a>
  </div>
</div>
</body>
</html>
'''

with io.open("foncier/templates/registration/password_reset_form.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(template_form)

with io.open("foncier/templates/registration/password_reset_code.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(template_code)

print("OK : dashboard_views.py, dashboard_urls.py et les 2 templates ont ete mis a jour/crees.")