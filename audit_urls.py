import os
import re
import glob

# Detecte automatiquement le module de settings depuis manage.py
with open('manage.py', encoding='utf-8') as f:
    contenu_manage = f.read()
m = re.search(r"DJANGO_SETTINGS_MODULE['\"]?\s*,\s*['\"]([\w\.]+)['\"]", contenu_manage)
settings_module = m.group(1) if m else 'kmsn.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

import django
django.setup()

from django.urls import get_resolver

def toutes_les_urls_nommees(resolver):
    noms = set()
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'url_patterns'):
            noms |= toutes_les_urls_nommees(pattern)
        elif getattr(pattern, 'name', None):
            noms.add(pattern.name)
    return noms

noms_definis = toutes_les_urls_nommees(get_resolver())
print(f"{len(noms_definis)} noms d'URL definis dans le projet.")

motif = re.compile(r"""\{%\s*url\s+['"]([a-zA-Z0-9_]+)['"]""")
manquants = {}
fichiers_scannes = 0

for path in glob.glob('**/templates/**/*.html', recursive=True):
    fichiers_scannes += 1
    with open(path, encoding='utf-8', errors='replace') as f:
        contenu = f.read()
    for m2 in motif.finditer(contenu):
        nom = m2.group(1)
        if nom not in noms_definis:
            manquants.setdefault(nom, set()).add(path)

print(f"{fichiers_scannes} fichiers .html scannes.")

if manquants:
    print("=== URLs referencees dans les templates mais INTROUVABLES (cassees) ===")
    for nom, fichiers in sorted(manquants.items()):
        print(f"- '{nom}' utilise dans :")
        for f2 in sorted(fichiers):
            print(f"    {f2}")
else:
    print("Aucun lien {% url %} casse trouve dans les templates.")