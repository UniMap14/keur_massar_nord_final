import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
import django
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")

from django.test import Client
from django.contrib.auth.models import User

for username in ["chef_cadastre", "chef_fiscalite"]:
    u = User.objects.get(username=username)
    u.set_password("test_temp_12345")
    u.save()

    client = Client()
    ok = client.login(username=username, password="test_temp_12345")
    print(username + " - connexion : " + str(ok))

    resp = client.get("/gestion/")
    contenu = resp.content.decode("utf-8")
    print(username + " - lien 'Activite de mes agents' present : " + str("Activite de mes agents" in contenu))

    resp2 = client.get("/gestion/journal-audit/")
    print(username + " - page journal-audit : status " + str(resp2.status_code))

    client.logout()

print()
print("=== Verification du contenu de la vue (pas d'erreur serveur) ===")
client = Client()
client.login(username="chef_cadastre", password="test_temp_12345")
resp3 = client.get("/gestion/journal-audit/")
if resp3.status_code != 200:
    print("ERREUR : status " + str(resp3.status_code))
    print(resp3.content.decode("utf-8")[:2000])
else:
    print("OK : page chargee normalement pour chef_cadastre, status 200")
