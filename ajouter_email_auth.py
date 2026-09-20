import re

CHEMIN = "citoyens/views.py"

FORME = '''
class EmailAuthenticationForm(AuthenticationForm):
    """
    Le champ visible dit "Email" (voir dashboard/login.html), mais
    AuthenticationForm attend un nom d'utilisateur : on traduit ici
    l'email saisi vers le vrai username avant que Django ne verifie
    le mot de passe.
    """
    def clean_username(self):
        saisi = self.cleaned_data.get('username', '')
        try:
            user = User.objects.get(email__iexact=saisi)
            return user.username
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return saisi

'''

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "class EmailAuthenticationForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    if "from django.contrib.auth.forms import AuthenticationForm" not in contenu:
        contenu = contenu.replace(
            "from django.contrib.auth.views import LoginView",
            "from django.contrib.auth.views import LoginView\nfrom django.contrib.auth.forms import AuthenticationForm",
            1,
        )
    if "from django.contrib.auth.models import User" not in contenu:
        contenu = contenu.replace(
            "from django.contrib.auth.forms import AuthenticationForm",
            "from django.contrib.auth.forms import AuthenticationForm\nfrom django.contrib.auth.models import User",
            1,
        )

    ancre = "class CitoyenLoginView(LoginView):"
    if ancre not in contenu:
        print("ERREUR : ancre 'class CitoyenLoginView(LoginView):' introuvable.")
    else:
        contenu = contenu.replace(ancre, FORME + ancre, 1)
        contenu = contenu.replace(
            'template_name = "dashboard/login.html"\n    redirect_authenticated_user = False',
            'template_name = "dashboard/login.html"\n    form_class = EmailAuthenticationForm\n    redirect_authenticated_user = False',
            1,
        )
        with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
            f.write(contenu)
        print("OK : EmailAuthenticationForm ajoute et branche sur CitoyenLoginView.")