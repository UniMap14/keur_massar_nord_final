CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_form_valid = '''            form.add_error(None, message)
            return self.form_invalid(form)

        return super().form_valid(form)'''

nouveau_form_valid = '''            form.add_error(None, message)
            return self.form_invalid(form)

        # Ne connecte pas encore : genere un code a usage unique (OTP)
        # envoye par SMS/email, et redirige vers sa verification -- la
        # connexion Django elle-meme n'a lieu qu'une fois le bon code
        # saisi (voir otp_verify_view).
        import time
        code = _generer_otp()
        self.request.session["otp_user_id"] = user.pk
        self.request.session["otp_code"] = code
        self.request.session["otp_expire"] = time.time() + 300
        self.request.session["otp_next"] = self.get_success_url()
        _envoyer_otp(user, code)

        return redirect("citoyen_otp_verify")'''

if nouveau_form_valid in contenu:
    print("DEJA FAIT : form_valid deja modifie.")
elif ancre_form_valid in contenu:
    contenu = contenu.replace(ancre_form_valid, nouveau_form_valid, 1)
    changements += 1
    print("OK : form_valid modifie pour declencher l'OTP.")
else:
    print("ERREUR : bloc form_valid exact introuvable.")

AJOUT = '''

# ============================================================
# CONNEXION SECURISEE — code a usage unique (OTP)
#
# Apres identifiant/mot de passe corrects, un code a 6 chiffres est
# envoye par SMS (si telephone connu) et par email, valable 5 minutes.
# La connexion Django n'a lieu qu'une fois ce code saisi correctement.
# Stockage temporaire du code en session (pas de nouveau modele/table).
# ============================================================

import random


def _generer_otp():
    return str(random.randint(100000, 999999))


def _envoyer_otp(user, code):
    from django.core.mail import send_mail
    from django.conf import settings
    from foncier.sms import envoyer_sms

    message = f"KEUR MASSAR NORD : votre code de connexion est {code}. Valable 5 minutes."

    citoyen = getattr(user, "citoyen", None)
    if citoyen is not None and citoyen.telephone:
        try:
            envoyer_sms(citoyen.telephone, message)
        except Exception:
            pass

    if user.email:
        try:
            send_mail(
                subject="[KEUR MASSAR NORD] Code de connexion",
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass


def otp_verify_view(request):
    """Page de saisie du code recu par SMS/email pour terminer la connexion."""
    import time
    from django.contrib.auth import login

    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("citoyen_login")

    erreur = None

    if request.method == "POST":
        code_saisi = request.POST.get("code", "").strip()
        expire = request.session.get("otp_expire", 0)

        if time.time() > expire:
            erreur = "Ce code a expiré. Veuillez vous reconnecter."
            for cle in ["otp_user_id", "otp_code", "otp_expire", "otp_next"]:
                request.session.pop(cle, None)
        elif code_saisi and code_saisi == request.session.get("otp_code"):
            user = User.objects.get(pk=user_id)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            next_url = request.session.pop("otp_next", None) or reverse("citoyen_espace")
            for cle in ["otp_user_id", "otp_code", "otp_expire"]:
                request.session.pop(cle, None)
            return redirect(next_url)
        else:
            erreur = "Code incorrect. Réessayez."

    return render(request, "citoyens/otp_verify.html", {"erreur": erreur})


def otp_resend_view(request):
    """Renvoie un nouveau code OTP (invalide l'ancien)."""
    import time

    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("citoyen_login")

    user = User.objects.get(pk=user_id)
    code = _generer_otp()
    request.session["otp_code"] = code
    request.session["otp_expire"] = time.time() + 300
    _envoyer_otp(user, code)
    messages.info(request, "Un nouveau code vous a été envoyé.")
    return redirect("citoyen_otp_verify")
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def otp_verify_view" in contenu_a_jour:
    print("DEJA FAIT : vues OTP deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vues OTP (generer/envoyer/verifier/renvoyer) ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")