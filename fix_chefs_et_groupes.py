import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
import django
django.setup()

from django.contrib.auth.models import User, Group

NOMS = {
    "chef_cadastre": ("Ibrahima", "DIALLO"),
    "chef_fiscalite": ("Mariama", "SOW"),
}
for username, infos in NOMS.items():
    prenom, nom = infos
    u = User.objects.get(username=username)
    u.first_name = prenom
    u.last_name = nom
    u.save()
    print("OK : " + username + " -> " + prenom + " " + nom + " (modifiable via Mon Profil)")

ORPHELINS = {
    "chef_cadastre": "Agent technique",
    "chef_fiscalite": "Agent fiscal",
}
for username, nom_groupe in ORPHELINS.items():
    u = User.objects.get(username=username)
    groupe = Group.objects.filter(name=nom_groupe).first()
    if groupe and u.groups.filter(pk=groupe.pk).exists():
        u.groups.remove(groupe)
        print("OK : groupe orphelin retire de " + username + " : " + nom_groupe)
    else:
        print("RAS : " + username + " n'avait pas (ou plus) le groupe : " + nom_groupe)

print("")
print("=== Verification finale ===")
for username in ["chef_cadastre", "chef_fiscalite"]:
    u = User.objects.get(username=username)
    nom_complet = u.first_name + " " + u.last_name
    groupes = list(u.groups.values_list("name", flat=True))
    print(username + ": nom=" + nom_complet + " groupes=" + str(groupes))
