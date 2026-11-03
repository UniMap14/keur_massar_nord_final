# -*- coding: utf-8 -*-
"""
Deuxieme script de diagnostic : a executer depuis la racine du projet
(a cote de manage.py) avec :

    python diag_demarches2.py

Il cherche "dashboard_demande_list" (et la vue qui rend demande_list.html)
dans TOUS les fichiers .py du projet, pas seulement ceux nommes views.py.
Copiez-collez toute la sortie ici.
"""
import os
import re

ROOT = os.getcwd()
EXCLUS = (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")


def lister_fichiers_py():
    resultats = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUS]
        for f in filenames:
            if f.endswith(".py"):
                resultats.append(os.path.join(dirpath, f))
    return resultats


def afficher_fonction_complete(chemin, nom_fonction):
    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()
    except Exception as e:
        print(f"[Erreur de lecture {chemin}: {e}]")
        return False

    debut = None
    for i, ligne in enumerate(lignes):
        if re.match(rf"^def\s+{re.escape(nom_fonction)}\s*\(", ligne):
            debut = i
            break
    if debut is None:
        return False

    # on remonte pour inclure les decorateurs juste au-dessus
    haut = debut
    while haut > 0 and lignes[haut - 1].lstrip().startswith("@"):
        haut -= 1

    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def\s+\w+\s*\(", lignes[j]) or re.match(r"^class\s+\w+", lignes[j]):
            fin = j
            break

    print("=" * 100)
    print(f"{chemin} :: def {nom_fonction}(...)  [lignes {haut+1}-{fin}]")
    print("=" * 100)
    print("".join(lignes[haut:fin]))
    print()
    return True


def grep_ligne(chemin, motif):
    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()
    except Exception:
        return []
    return [(i + 1, l.rstrip("\n")) for i, l in enumerate(lignes) if motif.lower() in l.lower()]


def main():
    fichiers = lister_fichiers_py()
    print(f"Dossier courant : {ROOT}")
    print(f"{len(fichiers)} fichiers .py trouves (hors venv/git/etc.)\n")

    # 1) la fonction elle-meme, ou qu'elle soit
    trouve = False
    for chemin in fichiers:
        if afficher_fonction_complete(chemin, "dashboard_demande_list"):
            trouve = True
    if not trouve:
        print("'dashboard_demande_list' introuvable comme def dans aucun fichier .py.\n")

    # 2) tous les fichiers qui en parlent (import, reference, etc.)
    print("=" * 100)
    print("Occurrences de 'dashboard_demande_list' dans tout le projet :")
    print("=" * 100)
    for chemin in fichiers:
        for num, ligne in grep_ligne(chemin, "dashboard_demande_list"):
            print(f"{chemin}:{num}: {ligne}")
    print()

    # 3) qui rend (render) le template demande_list.html ?
    print("=" * 100)
    print("Occurrences de 'demande_list.html' dans tout le projet :")
    print("=" * 100)
    for chemin in fichiers:
        for num, ligne in grep_ligne(chemin, "demande_list.html"):
            print(f"{chemin}:{num}: {ligne}")
    print()

    # 4) contenu complet de dashboard_urls.py (toutes les occurrences, au cas ou il y en a plusieurs copies)
    print("=" * 100)
    print("Contenu complet de chaque dashboard_urls.py trouve :")
    print("=" * 100)
    for chemin in fichiers:
        if os.path.basename(chemin) == "dashboard_urls.py":
            print(f"--- {chemin} ---")
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as f:
                    print(f.read())
            except Exception as e:
                print(f"[Erreur de lecture : {e}]")
            print()

    print("Script termine. Copiez-collez toute la sortie ci-dessus (ne coupez pas le debut).")


if __name__ == "__main__":
    main()