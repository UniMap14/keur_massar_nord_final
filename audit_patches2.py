import re
import glob

tous_scripts = [p for p in sorted(glob.glob("*.py")) if p not in ("audit_patches.py", "audit_urls.py", "manage.py", "audit_patches2.py")]

PROBABLEMENT_OK = []
A_VERIFIER = []
SANS_DEF_DETECTEE = []

def trouver_cible(code_source):
    m = re.search(r'open\(\s*["\']([^"\']+\.(?:py|html))["\']', code_source)
    if m:
        return m.group(1)
    m = re.search(r'CHEMIN\s*=\s*["\']([^"\']+)["\']', code_source, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

for path in tous_scripts:
    with open(path, encoding="utf-8", errors="replace") as f:
        code_source = f.read()

    noms_fonctions = set(re.findall(r'def\s+(\w+)\s*\(', code_source))
    noms_fonctions -= {"__init__"}

    if not noms_fonctions:
        SANS_DEF_DETECTEE.append(path)
        continue

    cible = trouver_cible(code_source)
    if not cible:
        A_VERIFIER.append((path, list(noms_fonctions), "cible introuvable"))
        continue

    try:
        with open(cible, encoding="utf-8", errors="replace") as f:
            contenu_cible = f.read()
    except FileNotFoundError:
        A_VERIFIER.append((path, list(noms_fonctions), f"fichier cible absent : {cible}"))
        continue

    manquantes = [n for n in noms_fonctions if f"def {n}(" not in contenu_cible]

    if not manquantes:
        PROBABLEMENT_OK.append(path)
    else:
        A_VERIFIER.append((path, manquantes, cible))

print(f"Total scripts avec au moins une 'def' detectee : {len(tous_scripts) - len(SANS_DEF_DETECTEE)}")
print(f"- Fonctions toutes retrouvees dans leur cible (OK) : {len(PROBABLEMENT_OK)}")
print(f"- Sans def a verifier (scripts de donnees, champs de modele, etc.) : {len(SANS_DEF_DETECTEE)}")
print(f"- *** A VERIFIER (fonction(s) introuvable(s) dans la cible) *** : {len(A_VERIFIER)}")

if A_VERIFIER:
    print("\n=== Details ===")
    for script, manquantes, cible in A_VERIFIER:
        print(f"- {script}")
        print(f"    cible attendue : {cible}")
        print(f"    fonction(s) introuvable(s) : {manquantes}")