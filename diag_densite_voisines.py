# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_densite_voisines.py', encoding='utf-8').read())"

Verifie la vraie repartition geographique des parcelles autour de la
parcelle NICAD 0152020102300970, a plusieurs rayons, pour savoir si le
"trou" visible a droite du plan est du a un manque reel de donnees a cet
endroit (zone non cadastree / route / terrain vague) ou a un probleme
de calcul.
"""
import foncier.models as m
import foncier.views as v

parcelle = m.Parcelle.objects.filter(nicad="0152020102300970").first()
print("Parcelle :", parcelle, "zone_id=", parcelle.zone_id)

xmin, ymin, xmax, ymax = parcelle.geom.extent
print("bbox parcelle (lon/lat) :", xmin, ymin, xmax, ymax)
cx = (xmin + xmax) / 2
cy = (ymin + ymax) / 2
print("centre approx (lon, lat) :", cx, cy)

for rayon_m in (100, 200, 300, 500, 800, 1200):
    tampon_deg = rayon_m / 111320.0
    zone_recherche = parcelle.geom.buffer(tampon_deg)
    nb = m.Parcelle.objects.filter(geom__intersects=zone_recherche).exclude(pk=parcelle.pk).count()
    print(f"rayon {rayon_m:5d} m -> {nb} parcelle(s) trouvee(s)")

print()
print("Repartition par quadrant (Nord/Sud/Est/Ouest) a 500m :")
tampon_deg = 500 / 111320.0
zone_recherche = parcelle.geom.buffer(tampon_deg)
candidats = m.Parcelle.objects.filter(geom__intersects=zone_recherche).exclude(pk=parcelle.pk).only("id", "geom")
compte = {"NE": 0, "NO": 0, "SE": 0, "SO": 0}
for cand in candidats:
    cxmin, cymin, cxmax, cymax = cand.geom.extent
    ccx, ccy = (cxmin + cxmax) / 2, (cymin + cymax) / 2
    cle = ("N" if ccy >= cy else "S") + ("E" if ccx >= cx else "O")
    compte[cle] += 1
print(compte)