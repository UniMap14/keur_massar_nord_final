import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()
from foncier.models import Parcelle

n_proprietaire = Parcelle.objects.filter(proprietaire__isnull=False).count()
n_occupation = Parcelle.objects.exclude(occupation_sol='').count()
n_intersection = Parcelle.objects.filter(proprietaire__isnull=False).exclude(occupation_sol='').count()

print(f"Parcelles avec propriétaire identifié : {n_proprietaire}")
print(f"Parcelles avec occupation du sol connue : {n_occupation}")
print(f"Intersection (les deux) : {n_intersection}")
