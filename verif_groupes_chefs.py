import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
import django
django.setup()
from django.contrib.auth.models import User
for uname in ["chef_cadastre", "chef_fiscalite", "maire"]:
    try:
        u = User.objects.get(username=uname)
        groupes = list(u.groups.values_list("name", flat=True))
        print(f"{uname}: is_superuser={u.is_superuser} groupes={groupes}")
    except User.DoesNotExist:
        print(f"{uname}: COMPTE INEXISTANT")
