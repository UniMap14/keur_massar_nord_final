import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()
from django.db.models import Sum, Avg, Count
from foncier.models import Parcelle

print("=== Répartition par occupation du sol (parcelles simulées) ===")
qs = (
    Parcelle.objects
    .filter(simulation_fiscale=True)
    .values('occupation_sol')
    .annotate(n=Count('id'), total=Sum('montant_taxe_annuelle'), moyenne=Avg('montant_taxe_annuelle'), superficie_totale=Sum('superficie'))
    .order_by('-total')
)
for r in qs:
    print(f"{r['occupation_sol']}: {r['n']} parcelles, total={r['total']:,.0f} FCFA, moyenne={r['moyenne']:,.0f} FCFA, superficie totale={r['superficie_totale']:,.0f} m2".replace(",", " "))

print()
print("=== Couverture globale ===")
total_parcelles = Parcelle.objects.count()
simulees = Parcelle.objects.filter(simulation_fiscale=True).count()
print(f"Total parcelles: {total_parcelles}")
print(f"Simulees: {simulees} ({100*simulees/total_parcelles:.1f}%)")

print()
print("=== Répartition par zone (top 10 zones avec le plus de recettes simulées) ===")
qs2 = (
    Parcelle.objects
    .filter(simulation_fiscale=True, zone__isnull=False)
    .values('zone__nom')
    .annotate(n=Count('id'), total=Sum('montant_taxe_annuelle'))
    .order_by('-total')[:10]
)
for r in qs2:
    print(f"{r['zone__nom']}: {r['n']} parcelles, total={r['total']:,.0f} FCFA".replace(",", " "))
if not qs2:
    print("(aucune parcelle simulée n'a de zone assignée)")
