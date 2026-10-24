import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
import django
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")

from django.test import Client
from django.contrib.auth.models import User

client = Client()
for username in ["chef_cadastre", "chef_fiscalite"]:
    u = User.objects.get(username=username)
    u.set_password("test_temp_12345")
    u.save()
    client.login(username=username, password="test_temp_12345")
    resp = client.get("/gestion/mes-agents/")
    print(username + " -> /gestion/mes-agents/ : status " + str(resp.status_code))
    resp2 = client.get("/gestion/mes-agents/creer/")
    print(username + " -> /gestion/mes-agents/creer/ : status " + str(resp2.status_code))
    client.logout()
