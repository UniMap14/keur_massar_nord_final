from foncier.models import Infrastructure

total = Infrastructure.objects.count()
rattachees = Infrastructure.objects.filter(parcelle__isnull=False).count()
non_rattachees = Infrastructure.objects.filter(parcelle__isnull=True).count()

print(f"Total infrastructures       : {total}")
print(f"Rattachées à une parcelle   : {rattachees}")
print(f"Hors parcelle cadastrée     : {non_rattachees}")