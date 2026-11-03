# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin_adm = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin_adm, "r", encoding="utf-8") as f:
    contenu_adm = f.read()

for motif in ["function infrastructuresFiltrees", "filtreInfraCategorie", "let filteredParcelles",
              "function celluleDansLaCommune", "turf.union", "turf.intersect", "let allLimites"]:
    print(motif, ":", motif in contenu_adm)