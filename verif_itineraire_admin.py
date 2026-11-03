import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
superviseur = User.objects.filter(is_superuser=True).first()
if not superviseur:
    superviseur = User.objects.filter(is_staff=True).first()

c = Client()
c.force_login(superviseur)
r = c.get("/geoportail/admin/")
html = r.content.decode("utf-8")

print("Connecte en tant que :", superviseur.username)
print("Statut HTTP :", r.status_code)

verifs = [
    "fpRouteBtn",
    "route-pied",
    "route-velo",
    "route-moto",
    "route-voiture",
    "centreItineraire.lat, centreItineraire.lng",
    "routing.openstreetmap.de/routed-bike",
    "routing.openstreetmap.de/routed-foot",
    "vitesseMotoKmh",
    "fp-edit-field",
    "fpSaveBtn",
    "contenuFormulaireEdition",
]
for v in verifs:
    print(v, ":", v in html)
