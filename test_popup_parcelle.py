import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
import django
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")

from django.test import Client

client = Client()
resp = client.get("/geoportail/")
print("Status : " + str(resp.status_code))
if resp.status_code == 200:
    contenu = resp.content.decode("utf-8")
    for marqueur in ["fp-stripe", "fp-head-icon", "fp-stats", "fp-infra-tags", "fp-btn-primary", "fpOccupationInfo"]:
        print(marqueur + " present : " + str(marqueur in contenu))
else:
    print(resp.content.decode("utf-8")[:1500])
