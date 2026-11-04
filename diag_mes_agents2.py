import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
import django
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")

from django.test import Client
from django.contrib.auth.models import User

u = User.objects.get(username="chef_cadastre")
print("Groupes de chef_cadastre : " + str(list(u.groups.values_list("name", flat=True))))
print("is_active : " + str(u.is_active))

# On reinitialise le mot de passe pour etre certain du test
u.set_password("test_temp_12345")
u.save()

client = Client()
ok = client.login(username="chef_cadastre", password="test_temp_12345")
print("Connexion reussie : " + str(ok))

resp = client.get("/gestion/")
print("Page d'accueil dashboard : status " + str(resp.status_code))
if resp.status_code == 302:
    print("Redirige vers : " + str(resp.url))
contenu = resp.content.decode("utf-8")
print("Lien 'Mes agents' present dans la sidebar : " + str("Mes agents" in contenu))
print("Texte 'Mon equipe' present : " + str("Mon equipe" in contenu))

resp2 = client.get("/gestion/mes-agents/")
print("Page /gestion/mes-agents/ : status " + str(resp2.status_code))
if resp2.status_code == 302:
    print("Redirige vers : " + str(resp2.url))
else:
    contenu2 = resp2.content.decode("utf-8")
    print("Bouton 'Creer un agent' present : " + str("Creer un agent" in contenu2))
