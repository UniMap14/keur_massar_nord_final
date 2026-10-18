# -*- coding: utf-8 -*-
"""
Complement a la Priorite 1 : _est_agent(user) etait defini comme
'return user.is_staff', sans aucune distinction de role. Cette fonction
protege 4 endpoints admin (carte_geoportail_admin,
api_parcelles_geojson_admin, api_parcelles_toutes_geojson_admin,
parcelle_update_fiscal) via @user_passes_test(_est_agent).

Decision validee avec l'utilisateur : la carte admin (cadastre + fiscal
melanges) reste consultable par tout agent ayant un role reconnu
(technique OU fiscal), au lieu de n'importe quel compte staff. Les
comptes Superviseur et les comptes historiques sans groupe assigne
gardent l'acces complet (deja gere par a_role()).

a_role est deja importe dans ce fichier (ajoute lors de la Priorite 1).

Idempotent.
"""
CHEMIN = "foncier/views.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''def _est_agent(user):
    return user.is_staff'''

NOUVEAU = '''def _est_agent(user):
    # Tout compte staff ne suffit plus : il faut aussi detenir un role
    # reconnu (technique ou fiscal). Superviseur et comptes historiques
    # sans groupe assigne restent couverts par a_role() (retrocompatibilite).
    return user.is_staff and a_role(user, 'technique', 'fiscal')'''

if "a_role(user, 'technique', 'fiscal')" in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (def _est_agent)")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")