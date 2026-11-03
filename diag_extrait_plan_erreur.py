# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_extrait_plan_erreur.py', encoding='utf-8').read())"

Reproduit exactement ce que fait extrait_cadastral_pdf_view pour generer
le plan (voisines + image), mais SANS avaler l'exception, pour voir le
vrai message d'erreur / traceback.
"""
import traceback
import foncier.models as m
import foncier.views as v

parcelle = m.Parcelle.objects.filter(nicad="0152020102300970").first()
if parcelle is None:
    print("Parcelle NICAD 0152020102300970 introuvable -- recherche approximative...")
    parcelle = m.Parcelle.objects.filter(nicad__icontains="0970").first()

print("Parcelle trouvee :", parcelle)
print("zone_id :", parcelle.zone_id if parcelle else None)
print("geom valide :", bool(parcelle.geom) if parcelle else None)

try:
    voisines = v._voisines_parcelle(parcelle, rayon_m=160, max_resultats=160)
    print("Nombre de voisines trouvees :", len(voisines))
    image_plan, echelle_texte = v._generer_image_plan_type_officiel(parcelle, voisines)
    print("OK : image generee, echelle =", echelle_texte)
except Exception:
    print("ERREUR :")
    traceback.print_exc()