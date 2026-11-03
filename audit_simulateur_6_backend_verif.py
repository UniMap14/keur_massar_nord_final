# -*- coding: utf-8 -*-
"""
python audit_simulateur_6_backend_verif.py

Les ancres du script precedent n'ont pas matche pour 2 passages dans
forms.py et 1 dans views.py. On relit ces passages tels qu'ils sont
reellement dans vos fichiers (peut-etre une apostrophe differente, ou
une ligne en plus) pour corriger les ancres avant de retenter.
"""
import io


def afficher_extrait(chemin, debut, fin, titre):
    print("=" * 100)
    print(f"{titre}  ({chemin}, lignes {debut} a {fin})")
    print("=" * 100)
    with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        lignes = f.readlines()
    debut_idx = max(0, debut - 1)
    fin_idx = min(len(lignes), fin)
    for i in range(debut_idx, fin_idx):
        print(f"{i + 1:5d} | {lignes[i].rstrip()}")
    print()


afficher_extrait("foncier/forms.py", 150, 260, "forms.py - SimulateurFiscalForm complet (champs + clean)")
afficher_extrait("foncier/views.py", 1030, 1105, "views.py - vue simuler_fiscalite (is / tva / cgu / else)")