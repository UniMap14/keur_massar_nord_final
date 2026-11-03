# -*- coding: utf-8 -*-
"""
A LANCER DEPUIS LA RACINE DU PROJET DJANGO (le dossier qui contient manage.py),
c'est a dire :  C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn

    python diagnostiquer_cartotheque.py

Ce script cherche tout seul :
  1) les templates HTML dont le nom ou le contenu parle de "carto"
     (cartotheque, cartotheque.html, etc.)
  2) les vues (views.py) et les urls (urls.py) qui en parlent

Il n'ecrit RIEN, il ne fait que lire et afficher. Copiez-collez tout ce qui
s'affiche dans votre reponse.
"""
import os

RACINE = os.getcwd()
MOTS_CLES = ["carto"]  # cartotheque, cartotheques, carte...

print(f"Racine analysee : {RACINE}")
print("=" * 70)

# -----------------------------------------------------------------
# 1) Recherche des templates HTML lies a "carto"
# -----------------------------------------------------------------
templates_trouves = []

for dossier, sous_dossiers, fichiers in os.walk(RACINE):
    # on evite de fouiller dans des dossiers lourds/inutiles
    sous_dossiers[:] = [
        d for d in sous_dossiers
        if d not in (".git", "node_modules", "venv", ".venv", "__pycache__", "staticfiles")
    ]
    for nom_fichier in fichiers:
        if not nom_fichier.lower().endswith(".html"):
            continue
        chemin_complet = os.path.join(dossier, nom_fichier)
        trouve_dans_nom = any(mot in nom_fichier.lower() for mot in MOTS_CLES)
        trouve_dans_contenu = False
        try:
            with open(chemin_complet, "r", encoding="utf-8", errors="replace") as f:
                contenu = f.read()
            if any(mot in contenu.lower() for mot in MOTS_CLES):
                trouve_dans_contenu = True
        except Exception:
            contenu = ""

        if trouve_dans_nom or trouve_dans_contenu:
            templates_trouves.append((chemin_complet, trouve_dans_nom, trouve_dans_contenu, len(contenu) if contenu else 0))

print(f"\n### {len(templates_trouves)} template(s) HTML lie(s) a 'carto' trouve(s) :\n")
for chemin, nom_ok, contenu_ok, taille in templates_trouves:
    tags = []
    if nom_ok:
        tags.append("NOM")
    if contenu_ok:
        tags.append("CONTENU")
    print(f" - {chemin}  [{', '.join(tags)}]  ({taille} caracteres)")

# -----------------------------------------------------------------
# 2) Recherche dans les views.py et urls.py
# -----------------------------------------------------------------
print("\n" + "=" * 70)
print("### Occurrences de 'carto' dans les fichiers views.py / urls.py :\n")

for dossier, sous_dossiers, fichiers in os.walk(RACINE):
    sous_dossiers[:] = [
        d for d in sous_dossiers
        if d not in (".git", "node_modules", "venv", ".venv", "__pycache__", "staticfiles")
    ]
    for nom_fichier in fichiers:
        if nom_fichier not in ("views.py", "urls.py"):
            continue
        chemin_complet = os.path.join(dossier, nom_fichier)
        try:
            with open(chemin_complet, "r", encoding="utf-8", errors="replace") as f:
                lignes = f.readlines()
        except Exception as e:
            print(f" - (erreur lecture {chemin_complet}: {e})")
            continue

        lignes_trouvees = [
            (i + 1, ligne.rstrip())
            for i, ligne in enumerate(lignes)
            if "carto" in ligne.lower()
        ]
        if lignes_trouvees:
            print(f"--- {chemin_complet} ---")
            for numero, texte in lignes_trouvees:
                print(f"   L{numero}: {texte}")
            print()

# -----------------------------------------------------------------
# 3) Si on a trouve un template "principal", on affiche son contenu complet
# -----------------------------------------------------------------
print("=" * 70)
if templates_trouves:
    # on privilegie celui dont le NOM de fichier contient "carto"
    candidats_nom = [t for t in templates_trouves if t[1]]
    meilleur = candidats_nom[0] if candidats_nom else templates_trouves[0]
    chemin_meilleur = meilleur[0]
    print(f"### Contenu complet du template le plus probable : {chemin_meilleur}\n")
    try:
        with open(chemin_meilleur, "r", encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()
        for i, ligne in enumerate(lignes, start=1):
            print(f"{i:4d}\t{ligne.rstrip()}")
    except Exception as e:
        print(f"(erreur de lecture : {e})")
else:
    print("Aucun template trouve automatiquement.")
    print("Dites-moi le nom exact de la page dans le menu du site,")
    print("ou le chemin du fichier si vous le connaissez.")