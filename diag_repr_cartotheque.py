# -*- coding: utf-8 -*-
"""
A lancer depuis la racine du projet :

    python diag_repr_cartotheque.py

Affiche, en repr() (donc avec tous les caracteres invisibles visibles :
espaces, tabulations, fins de ligne), les 3 zones du fichier qui nous
interessent. Copiez-collez TOUT le resultat, meme s'il parait illisible -
c'est fait pour.
"""
import io

chemin = "foncier/templates/foncier/cartotheque.html"

with io.open(chemin, "r", encoding="utf-8", newline="") as f:
    lignes = f.readlines()

def dump(debut, fin, titre):
    print(f"\n===== {titre} (lignes {debut} a {fin}) =====")
    for i in range(debut - 1, min(fin, len(lignes))):
        print(f"{i+1:4d}: {lignes[i]!r}")

dump(173, 190, "ZONE 1 - CSS lightbox-close / img-wrap")
dump(260, 270, "ZONE 2 - HTML lightbox overlay")
dump(278, 296, "ZONE 3 - JS click/fermer/keydown")