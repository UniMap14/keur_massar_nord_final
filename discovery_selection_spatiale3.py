# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def imprimer_fonction(chemin, lignes, nom_fonction, titre=None):
    debut = None
    for i, l in enumerate(lignes):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{titre or nom_fonction} INTROUVABLE dans {chemin}\n")
        return
    fin = len(lignes)
    niveau = 0
    compte_ouvert = False
    for j in range(debut, len(lignes)):
        niveau += lignes[j].count("{") - lignes[j].count("}")
        if "{" in lignes[j]:
            compte_ouvert = True
        if compte_ouvert and niveau <= 0:
            fin = j + 1
            break
    print(f"=== [{chemin}] {titre or nom_fonction}, lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(repr(lignes[i]))
    print()

chemin_pub = "foncier/templates/foncier/geoportail.html"
with io.open(chemin_pub, "r", encoding="utf-8") as f:
    lignes_pub = f.readlines()

chemin_adm = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin_adm, "r", encoding="utf-8") as f:
    lignes_adm = f.readlines()

imprimer_fonction(chemin_pub, lignes_pub, "surlignerInfrastructure", "PUBLIC surlignerInfrastructure")
imprimer_fonction(chemin_pub, lignes_pub, "effacerSelection", "PUBLIC effacerSelection")
imprimer_fonction(chemin_adm, lignes_adm, "effacerSelection", "ADMIN effacerSelection")

print("=== [public] 'coucheInfraSurlignee' toutes occurrences ===")
for i, l in enumerate(lignes_pub):
    if "coucheInfraSurlignee" in l:
        print(f"{i+1}: {repr(l)}")
print()

print("=== [admin] 'coucheInfraSurlignee' existe ? ===")
print(any("coucheInfraSurlignee" in l for l in lignes_adm))
print()

print("=== [public] onEvent btnSelectionItineraire (contexte complet) ===")
for i, l in enumerate(lignes_pub):
    if "onEvent('btnSelectionItineraire'" in l:
        debut = i
        fin = min(len(lignes_pub), i + 15)
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes_pub[j])}")
        break
print()

print("=== [admin] onEvent btnSelectionEffacer + alentours (contexte) ===")
for i, l in enumerate(lignes_adm):
    if "onEvent('btnSelectionEffacer'" in l:
        debut = max(0, i - 3)
        fin = min(len(lignes_adm), i + 5)
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes_adm[j])}")
        break
print()

print("=== [admin] 'calculerItineraire' signature (verif existance) ===")
for i, l in enumerate(lignes_adm):
    if re.match(r"\s*function calculerItineraire\(", l):
        print(f"{i+1}: {repr(l)}")
        break