# -*- coding: utf-8 -*-
"""
A lancer depuis la racine du projet (ou se trouve manage.py) :

    python dump_cartotheque_public.py

Affiche le contenu complet, numerote, de :
  foncier/templates/foncier/cartotheque.html
(la page PUBLIQUE de la cartotheque, pas le formulaire d'admin)

Ne modifie rien. Copiez-collez tout le resultat.
"""
import os

chemin = os.path.join("foncier", "templates", "foncier", "cartotheque.html")

if not os.path.exists(chemin):
    print(f"INTROUVABLE : {chemin}")
    print("Lancez ce script depuis le dossier qui contient manage.py.")
else:
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        lignes = f.readlines()
    print(f"Fichier : {os.path.abspath(chemin)}")
    print(f"Nombre de lignes : {len(lignes)}")
    print("=" * 70)
    for i, ligne in enumerate(lignes, start=1):
        print(f"{i:4d}\t{ligne.rstrip()}")