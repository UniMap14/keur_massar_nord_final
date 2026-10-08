import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from foncier.models import Infrastructure, CategorieInfrastructure

n_infra = Infrastructure.objects.count()
n_cat = CategorieInfrastructure.objects.count()

Infrastructure.objects.all().delete()
CategorieInfrastructure.objects.all().delete()

print(f"Supprime : {n_infra} infrastructure(s), {n_cat} categorie(s).")
print("Vous pouvez maintenant relancer importer_infrastructures.py puis lier_infrastructures_parcelles.py")