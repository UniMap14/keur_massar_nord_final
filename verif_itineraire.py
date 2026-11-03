import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append("testserver")
from django.test import Client

c = Client()
r = c.get("/geoportail/")
html = r.content.decode("utf-8")

print("Statut HTTP :", r.status_code)

verifs = [
    "fpRouteBtn",
    "route-pied",
    "route-velo",
    "route-moto",
    "route-voiture",
    "centre.lat, centre.lng",
    "routing.openstreetmap.de/routed-bike",
    "routing.openstreetmap.de/routed-foot",
    "vitesseMotoKmh",
    "layer.getBounds().getCenter()",
]
for v in verifs:
    print(v, ":", v in html)
