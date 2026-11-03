# -*- coding: utf-8 -*-
"""
Corrige la lenteur du geoportail (public + admin) :

1) Le cache stockait un gros dictionnaire Python (40588 parcelles).
   Meme "a chaud", Django devait le (de)serialiser integralement a
   chaque requete : ~25-26 secondes mesurees, pour rien. On met
   desormais en cache le JSON deja pret (une simple chaine), comme
   c'etait deja fait pour les zones -- l'affichage redevient quasi
   instantane une fois le cache chaud.

2) Le cache utilise (LocMemCache, le defaut Django) est en memoire du
   process : il se vide a CHAQUE redemarrage du serveur. On passe a un
   cache sur disque (FileBasedCache) pour qu'il survive aux
   redemarrages -- la premiere "vraie" lenteur (~1 minute) ne se
   produira donc plus qu'une seule fois, pas a chaque redemarrage.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_perf_geoportail.py
"""
import os

CHEMIN_VIEWS = os.path.join("foncier", "views.py")
CHEMIN_SETTINGS = os.path.join("kmsn", "settings.py")

# ------------------------------------------------------------------
# 1) foncier/views.py : mettre en cache le JSON deja serialise
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_VIEWS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_VIEWS}")

with open(CHEMIN_VIEWS, "r", encoding="utf-8") as f:
    views = f.read()

PATCHES_VIEWS = []

PATCHES_VIEWS.append((
    "lecture cache PUBLIC",
    "    data = cache.get(CACHE_KEY_PUBLIC)\n    if data is None:\n",
    "    data_json = cache.get(CACHE_KEY_PUBLIC)\n    if data_json is None:\n",
))

PATCHES_VIEWS.append((
    "ecriture cache PUBLIC + reponse",
    '        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle}\n'
    "        cache.set(CACHE_KEY_PUBLIC, data, None)  # pas d'expiration : invalidé par le signal\n"
    "\n"
    "    return JsonResponse(data)",

    '        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle}\n'
    "        # On met en cache le JSON deja serialise (une chaine), pas le dict\n"
    "        # Python : avec ~40000 features, (de)serialiser l'objet complet a\n"
    '        # chaque lecture du cache coutait ~25s a elle seule, meme "a chaud".\n'
    "        data_json = json.dumps(data)\n"
    "        cache.set(CACHE_KEY_PUBLIC, data_json, None)  # pas d'expiration : invalidé par le signal\n"
    "\n"
    "    return HttpResponse(data_json, content_type=\"application/json\")",
))

PATCHES_VIEWS.append((
    "lecture cache ADMIN",
    "    data = cache.get(CACHE_KEY_ADMIN)\n    if data is None:\n",
    "    data_json = cache.get(CACHE_KEY_ADMIN)\n    if data_json is None:\n",
))

PATCHES_VIEWS.append((
    "ecriture cache ADMIN + reponse",
    '        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle_admin}\n'
    "        cache.set(CACHE_KEY_ADMIN, data, None)\n"
    "\n"
    "    return JsonResponse(data)",

    '        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle_admin}\n'
    "        data_json = json.dumps(data)\n"
    "        cache.set(CACHE_KEY_ADMIN, data_json, None)\n"
    "\n"
    "    return HttpResponse(data_json, content_type=\"application/json\")",
))

deja_ok_views = "data_json = cache.get(CACHE_KEY_PUBLIC)" in views and "data_json = cache.get(CACHE_KEY_ADMIN)" in views

if not deja_ok_views:
    erreurs = []
    for nom, ancre, remplacement in PATCHES_VIEWS:
        if remplacement in views:
            continue
        if ancre not in views:
            erreurs.append(f"- ancre introuvable pour « {nom} »")
            continue
        if views.count(ancre) != 1:
            erreurs.append(f"- ancre « {nom} » trouvee {views.count(ancre)} fois (attendu 1)")
            continue
        views = views.replace(ancre, remplacement)
    if erreurs:
        print("ERREUR dans foncier/views.py :")
        for e in erreurs:
            print(e)
        raise SystemExit("Aucun fichier n'a ete modifie (securite : tout ou rien).")

# ------------------------------------------------------------------
# 2) kmsn/settings.py : cache sur disque (survit aux redemarrages)
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_SETTINGS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_SETTINGS}")

with open(CHEMIN_SETTINGS, "r", encoding="utf-8") as f:
    settings_py = f.read()

deja_ok_settings = "CACHES" in settings_py

BLOC_CACHES = '''

# ============================================================
# Cache sur disque (et non en memoire) : le geoportail met en cache
# ~40000 parcelles (calcul a froid ~1 minute). Avec le cache par defaut
# de Django (LocMemCache, en memoire du process), ce cache est perdu a
# CHAQUE redemarrage du serveur de developpement. En passant sur disque,
# il survit aux redemarrages -- le calcul lourd ne se refait que quand
# les donnees changent reellement (voir les signaux dans foncier/views.py).
# ============================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "django_cache",
    }
}
'''

if not deja_ok_settings:
    settings_py = settings_py.rstrip("\n") + "\n" + BLOC_CACHES
    with open(CHEMIN_SETTINGS, "w", encoding="utf-8") as f:
        f.write(settings_py)

if not deja_ok_views:
    with open(CHEMIN_VIEWS, "w", encoding="utf-8") as f:
        f.write(views)

if deja_ok_views and deja_ok_settings:
    print("OK : deja applique, rien a faire.")
else:
    print("OK : geoportail optimise.")
    print("-> foncier/views.py " + ("(deja a jour)" if deja_ok_views else "modifie : cache du JSON deja serialise"))
    print("-> kmsn/settings.py " + ("(deja a jour)" if deja_ok_settings else "modifie : cache sur disque (survit aux redemarrages)"))
    print("-> Redemarrez le serveur Django. Le PROCHAIN chargement du geoportail (public ou admin)")
    print("   sera encore lent une fois (~1 minute, le temps de calculer le cache) -- ensuite ce")
    print("   sera rapide, meme apres de futurs redemarrages.")