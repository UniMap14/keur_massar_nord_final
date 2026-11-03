# -*- coding: utf-8 -*-
import sys, io, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== Recherche de settings.py ===")
candidats = glob.glob("**/settings.py", recursive=True)
for c in candidats:
    print(c)
print()

if candidats:
    chemin_settings = candidats[0]
    with io.open(chemin_settings, "r", encoding="utf-8") as f:
        contenu = f.read()
    print(f"=== Extraits pertinents de {chemin_settings} ===")
    for motif in ["DEBUG", "CACHES", "MIDDLEWARE", "GZip", "WhiteNoise", "STATICFILES_STORAGE", "ALLOWED_HOSTS"]:
        print(f"--- {motif} ---")
        for m in re.finditer(r"^.*" + re.escape(motif) + r".*$", contenu, re.MULTILINE):
            print(m.group(0))
        print()

print("=== Constantes PARCELLES_MAX_PAR_REQUETE / TOLERANCE dans views.py ===")
with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    contenu_views = f.read()
for motif in ["PARCELLES_MAX_PAR_REQUETE", "TOLERANCE_SIMPLIFICATION", "CACHE_KEY_PUBLIC", "CACHE_KEY_ADMIN", "cache.set", "def api_parcelles_bounds"]:
    print(f"--- {motif} ---")
    for m in re.finditer(r"^.*" + re.escape(motif) + r".*$", contenu_views, re.MULTILINE):
        print(m.group(0))
    print()