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

c = Client()
r1 = c.get("/geoportail/")
c.force_login(superviseur)
r2 = c.get("/geoportail/admin/")

html1 = r1.content.decode("utf-8")
html2 = r2.content.decode("utf-8")

print("Public - statut :", r1.status_code)
print("Public - coordAffichees present :", "coordAffichees" in html1)
print("Public - aucune trace du mode manuel :", "modePositionManuelle" not in html1)

print("")
print("Admin - statut :", r2.status_code)
print("Admin - coordAffichees present :", "coordAffichees" in html2)
print("Admin - aucune trace du mode manuel :", "modePositionManuelle" not in html2)
