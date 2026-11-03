# -*- coding: utf-8 -*-
import io

CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    lignes = f.readlines()


def trouver(sous_chaine, depart=0):
    for i in range(depart, len(lignes)):
        if sous_chaine in lignes[i]:
            return i
    raise ValueError("Introuvable : " + sous_chaine)


idx_fn = trouver("function localiserMoi() {")
idx_msg = trouver("Position trouvée.</span>", idx_fn)
indent = lignes[idx_msg][:len(lignes[idx_msg]) - len(lignes[idx_msg].lstrip())]

lignes[idx_msg:idx_msg + 1] = [
    indent + "const coordAffichees = formaterCoordonnees({ lat: pos.coords.latitude, lng: pos.coords.longitude });\n",
    indent + "status.innerHTML = '<span style=\"color:#2f7a4f;\"><i class=\"fa-solid fa-check\"></i> Position trouvée : ' + coordAffichees + '</span>';\n",
]

with io.open(CHEMIN, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lignes)

print("OK : coordonnees ajoutees au message de localisation")
