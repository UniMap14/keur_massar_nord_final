import ast
import glob
import re

RESULTATS_NON_APPLIQUES = []
RESULTATS_APPLIQUES = []
RESULTATS_AMBIGUS = []
RESULTATS_SANS_PATCH = []

def extraire_chaines(arbre):
    """{nom_variable: valeur} pour chaque assignation simple a une chaine litterale."""
    resultat = {}
    for node in ast.walk(arbre):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                resultat[node.targets[0].id] = node.value.value
    return resultat

def trouver_chemins_cibles(code_source, chaines):
    chemins = []
    # Cas 1 : open("litteral.py")
    chemins += re.findall(r'open\(\s*["\']([^"\']+\.(?:py|html))["\']', code_source)
    # Cas 2 : open(VARIABLE, ...) ou VARIABLE a ete assignee a une chaine plus haut
    for nom_var in re.findall(r'open\(\s*(\w+)\s*[,)]', code_source):
        valeur = chaines.get(nom_var, "")
        if valeur.endswith((".py", ".html")):
            chemins.append(valeur)
    return chemins

def trouver_marqueur_ancien(code_source, chaines):
    candidats = re.findall(r'\b(\w+)\s+not in\s+\w+', code_source)
    candidats += re.findall(r'\.replace\(\s*(\w+)\s*,', code_source)
    candidats += re.findall(r'\bif\s+(\w+)\s+in\s+\w+', code_source)
    for nom in candidats:
        if nom in chaines and len(chaines[nom]) > 15:
            return nom, chaines[nom]
    # repli : la plus longue chaine multilignes du script (souvent le bloc "ancien")
    multilignes = {k: v for k, v in chaines.items() if "\n" in v and len(v) > 15}
    if multilignes:
        nom = max(multilignes, key=lambda k: len(multilignes[k]))
        return nom, multilignes[nom]
    return None, None

tous_scripts = [p for p in sorted(glob.glob("*.py")) if p not in ("audit_patches.py", "audit_urls.py", "manage.py")]

for path in tous_scripts:
    try:
        with open(path, encoding="utf-8") as f:
            code_source = f.read()
        arbre = ast.parse(code_source)
    except Exception as e:
        RESULTATS_AMBIGUS.append((path, f"non analysable ({e})"))
        continue

    chaines = extraire_chaines(arbre)
    chemins = trouver_chemins_cibles(code_source, chaines)
    nom_marqueur, valeur_marqueur = trouver_marqueur_ancien(code_source, chaines)

    if not nom_marqueur or not chemins:
        RESULTATS_SANS_PATCH.append(path)
        continue

    cible = chemins[0]
    try:
        with open(cible, encoding="utf-8", errors="replace") as f:
            contenu_cible = f.read()
    except FileNotFoundError:
        RESULTATS_AMBIGUS.append((path, f"fichier cible introuvable : {cible}"))
        continue

    if valeur_marqueur in contenu_cible:
        RESULTATS_NON_APPLIQUES.append((path, cible))
    else:
        RESULTATS_APPLIQUES.append((path, cible))

print(f"Total scripts analyses : {len(tous_scripts)}")
print(f"- Scripts de donnees / sans patch textuel detecte : {len(RESULTATS_SANS_PATCH)}")
print(f"- Patches detectes comme deja appliques : {len(RESULTATS_APPLIQUES)}")
print(f"- Ambigus (non analysables automatiquement) : {len(RESULTATS_AMBIGUS)}")
print(f"- *** PATCHES POTENTIELLEMENT NON APPLIQUES *** : {len(RESULTATS_NON_APPLIQUES)}")

if RESULTATS_NON_APPLIQUES:
    print("\n=== A VERIFIER EN PRIORITE (le texte recherche est TOUJOURS present dans le fichier cible) ===")
    for script, cible in RESULTATS_NON_APPLIQUES:
        print(f"- {script}  ->  cible: {cible}")

if RESULTATS_AMBIGUS:
    print("\n=== Ambigus ===")
    for script, raison in RESULTATS_AMBIGUS:
        print(f"- {script} : {raison}")