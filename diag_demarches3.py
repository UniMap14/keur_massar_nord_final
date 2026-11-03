# -*- coding: utf-8 -*-
"""
Troisieme script de diagnostic : meme principe, depuis la racine du
projet (a cote de manage.py) :

    python diag_demarches3.py

Cette fois on va chercher :
  1) la fonction _filtrer_demandes_service (le filtre qui limite la liste
     selon le role de l'agent connecte)
  2) comment le badge "502" de la sidebar est calcule (probablement un
     comptage NON filtre, d'ou le decalage avec la liste filtree)
  3) les roles possibles d'un agent (pour comprendre "Chef du Service
     Fiscalite" vs "Chef du Service Cadastre")
"""
import os
import re

ROOT = os.getcwd()
EXCLUS = (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")


def lister_fichiers(extensions):
    resultats = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUS]
        for f in filenames:
            if f.endswith(extensions):
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
    fichiers_py = lister_fichiers((".py",))
    fichiers_html = lister_fichiers((".html",))

    print(f"Dossier courant : {ROOT}\n")

    # 1) _filtrer_demandes_service
    trouve = False
    for chemin in fichiers_py:
        if afficher_fonction_complete(chemin, "_filtrer_demandes_service"):
            trouve = True
    if not trouve:
        print("'_filtrer_demandes_service' introuvable comme def. Recherche large :\n")
        for chemin in fichiers_py:
            grep_contexte(chemin, ["_filtrer_demandes_service"], contexte=2)

    # 2) badge sidebar "Démarches en ligne" : chercher dans base.html / sidebar
    print("=" * 100)
    print("Recherche du badge sidebar lie aux demandes (base.html / sidebar)")
    print("=" * 100)
    for chemin in fichiers_html:
        if "sidebar" in chemin.lower() or os.path.basename(chemin) == "base.html":
            grep_contexte(chemin, ["demande", "nb_demande", "badge"], contexte=2)

    # 3) contexte processor / vue dashboard_home ou autre qui calcule un total "demandes" non filtre
    print("=" * 100)
    print("Recherche de contexte processors possibles (fichier context_processors.py)")
    print("=" * 100)
    for chemin in fichiers_py:
        if "context_processor" in os.path.basename(chemin).lower():
            print(f"--- {chemin} ---")
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as f:
                    print(f.read())
            except Exception as e:
                print(f"[Erreur : {e}]")
            print()

    # 4) role / service de l'agent : chercher ProfilAgent ou AgentFoncier ou champ "service"/"role"
    print("=" * 100)
    print("Recherche du modele de role agent (service cadastre / fiscalite)")
    print("=" * 100)
    for chemin in fichiers_py:
        if os.path.basename(chemin) == "models.py":
            grep_contexte(chemin, ["chef du service", "CHEF_FISCALITE", "CHEF_CADASTRE", "class ProfilAgent", "SERVICE_CHOICES", "ROLE_CHOICES"], contexte=4)

    print("Script termine. Copiez-collez toute la sortie ci-dessus.")


if __name__ == "__main__":
    main()