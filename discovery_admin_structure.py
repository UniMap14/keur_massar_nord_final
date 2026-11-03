# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for chemin in ["foncier/templates/foncier/geoportail.html", "foncier/templates/foncier/geoportail_admin.html", "foncier/templates/dashboard/geoportail_shell.html"]:
    taille = os.path.getsize(chemin)
    with io.open(chemin, "r", encoding="utf-8") as f:
        lignes = f.readlines()
    print(chemin, "-", taille, "octets -", len(lignes), "lignes")
    print("Premieres lignes :")
    print("".join(lignes[:15]))
    print("---")
    print()

print("=== geoportail_admin.html : contient-il {% extends %} ou {% include %} ? ===")
with io.open("foncier/templates/foncier/geoportail_admin.html", "r", encoding="utf-8") as f:
    contenu_admin = f.read()
import re
for m in re.finditer(r"\{%\s*(extends|include)[^%]*%\}", contenu_admin):
    print(m.group(0))

print()
print("=== geoportail_admin.html : contient-il 'analyserZonesSousDesservies' / 'basculerVoronoi' / 'celluleDansLaCommune' ? ===")
for motif in ["analyserZonesSousDesservies", "basculerVoronoi", "celluleDansLaCommune", "infrastructuresFiltrees", "allLimites", "toggle-choropleth"]:
    print(motif, ":", motif in contenu_admin)