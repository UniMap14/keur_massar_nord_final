# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('verif_champ_reference_arrete.py', encoding='utf-8').read())"
"""
import foncier.models as m

noms = [f.name for f in m.Parcelle._meta.get_fields()]
print("reference_arrete present :", "reference_arrete" in noms)
print("Champs contenant 'arrete' ou 'arrêté' :", [n for n in noms if "arret" in n.lower()])