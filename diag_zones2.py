# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_zones2.py', encoding='utf-8').read())"
"""
import inspect
import foncier.models as m

print("=" * 100)
print("1) Definition du modele Zone :")
print("=" * 100)
print(inspect.getsource(m.Zone))
print()

print("=" * 100)
print("2) Definition du modele QuartierOfficiel :")
print("=" * 100)
print(inspect.getsource(m.QuartierOfficiel))
print()

print("=" * 100)
print("3) Le champ 'zone' de Parcelle pointe vers quel modele ?")
print("=" * 100)
champ = m.Parcelle._meta.get_field("zone")
print("related_model =", champ.related_model)
print()

print("=" * 100)
print("4) Combien de Parcelle ont un 'zone' (Zone) rempli vs vide ?")
print("=" * 100)
print("  total parcelles       :", m.Parcelle.objects.count())
print("  avec zone (Zone) non nul :", m.Parcelle.objects.exclude(zone__isnull=True).count())
print()

# Le lien parcelle -> QuartierOfficiel se fait peut-etre via la geometrie
# (spatial) plutot qu'une ForeignKey. On cherche un champ qui pointe vers
# QuartierOfficiel sur Parcelle, s'il existe.
champs_parcelle = [f.name for f in m.Parcelle._meta.get_fields()]
print("Tous les champs de Parcelle :", champs_parcelle)
print()

print("=" * 100)
print("5) Exemples d'enregistrements Zone (s'il y en a) et QuartierOfficiel :")
print("=" * 100)
print("Zone (5 premiers) :", list(m.Zone.objects.all()[:5]))
print("QuartierOfficiel (5 premiers) :", [(q.pk, q.nom) for q in m.QuartierOfficiel.objects.all()[:5]])
print()