# -*- coding: utf-8 -*-
"""
Script de diagnostic : a executer depuis la racine du projet Django
(le dossier qui contient manage.py), avec :

    python diag_demarches.py

Il cherche et affiche tout ce qui touche a "Demarches en ligne" (vue,
urls, template, JS) pour comprendre pourquoi le badge affiche 502 mais
la liste est vide. Copiez-collez toute la sortie ici.
"""
import os
import re
import sys

ROOT = os.getcwd()


def trouver_fichier(nom_cible):
    resultats = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # on evite de fouiller dans les environnements virtuels / git / node_modules
        dirnames[:] = [
            d for d in dirnames
            if d not in (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")
        ]
        for f in filenames:
            if f == nom_cible:
                resultats.append(os.path.join(dirpath, f))
    return resultats


def afficher_fichier(chemin, titre=None):
    print("=" * 100)
    print(titre or chemin)
    print("=" * 100)
    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            print(f.read())
    except Exception as e:
        print(f"[Erreur de lecture : {e}]")
    print()


def extraire_fonction(chemin, nom_fonction):
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

    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def\s+\w+\s*\(", lignes[j]) or re.match(r"^class\s+\w+", lignes[j]):
            fin = j
            break

    print("=" * 100)
    print(f"{chemin} :: def {nom_fonction}(...)  [lignes {debut+1}-{fin}]")
    print("=" * 100)
    print("".join(lignes[debut:fin]))
    print()
    return True


def grep_contexte(chemin, motifs, contexte=3):
    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()
    except Exception:
        return
    trouve = False
    for i, ligne in enumerate(lignes):
        if any(m.lower() in ligne.lower() for m in motifs):
            if not trouve:
                print("=" * 100)
                print(f"{chemin} :: extraits autour de {motifs}")
                print("=" * 100)
                trouve = True
            debut = max(0, i - contexte)
            fin = min(len(lignes), i + contexte + 1)
            print(f"--- ligne {i+1} ---")
            print("".join(lignes[debut:fin]))
            print()
    if trouve:
        print()


def main():
    if not os.path.exists(os.path.join(ROOT, "manage.py")):
        print("ATTENTION : manage.py introuvable dans le dossier courant.")
        print(f"Dossier courant : {ROOT}")
        print("Relancez ce script depuis la racine du projet Django (a cote de manage.py).")
        print()

    print(f"Dossier courant : {ROOT}\n")

    # 1) dashboard_urls.py : routes "demandes"
    for chemin in trouver_fichier("dashboard_urls.py"):
        grep_contexte(chemin, ["demande"], contexte=2)

    # 2) views.py : la/les fonction(s) dashboard_demande_list / dashboard_demande_detail
    fichiers_views = trouver_fichier("views.py")
    noms_fonctions_possibles = [
        "dashboard_demande_list",
        "dashboard_demande_detail",
    ]
    trouve_une_fonction = False
    for chemin in fichiers_views:
        for nom in noms_fonctions_possibles:
            if extraire_fonction(chemin, nom):
                trouve_une_fonction = True

    if not trouve_une_fonction:
        print("Aucune fonction 'dashboard_demande_list' / 'dashboard_demande_detail' trouvee.")
        print("Recherche plus large de 'demande' dans tous les views.py :\n")
        for chemin in fichiers_views:
            grep_contexte(chemin, ["def ", "demande"], contexte=1)

    # 3) Templates : la page "Demarches en ligne" (badge 502, liste vide)
    extensions_templates = (".html",)
    motifs_template = ["emarches en ligne", "dashboard_demande", "demarche"]
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            d for d in dirnames
            if d not in (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")
        ]
        for f in filenames:
            if f.endswith(extensions_templates):
                chemin = os.path.join(dirpath, f)
                try:
                    with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                        contenu = fh.read()
                except Exception:
                    continue
                if any(m.lower() in contenu.lower() for m in motifs_template):
                    print(f"[Template concerne] {chemin}")

    print()
    print("Script termine. Copiez-collez toute la sortie ci-dessus.")


if __name__ == "__main__":
    main()