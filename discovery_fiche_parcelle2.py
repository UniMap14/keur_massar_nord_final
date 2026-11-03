# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin_adm = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin_adm, "r", encoding="utf-8") as f:
    lignes_adm = f.readlines()

def imprimer_fonction(nom_fonction):
    debut = None
    for i, l in enumerate(lignes_adm):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{nom_fonction} INTROUVABLE\n")
        return
    fin = len(lignes_adm)
    niveau = 0
    compte_ouvert = False
    for j in range(debut, len(lignes_adm)):
        niveau += lignes_adm[j].count("{") - lignes_adm[j].count("}")
        if "{" in lignes_adm[j]:
            compte_ouvert = True
        if compte_ouvert and niveau <= 0:
            fin = j + 1
            break
    print(f"=== {nom_fonction}, lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(repr(lignes_adm[i]))
    print()

imprimer_fonction("contenuFicheParcelle")
imprimer_fonction("attacherEvenementsFiche")