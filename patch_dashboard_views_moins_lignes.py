# -*- coding: utf-8 -*-
"""
Le fil d'activite recente affichait "Il y a 2 weeks, 1 day" en anglais,
car LANGUAGE_CODE = 'en-us' dans settings.py fait parler anglais au
filtre Django |timesince, meme si le reste du site est en francais.

Ce patch calcule le texte "il y a ..." directement en francais dans la
vue (sans dependre de la locale Django ni modifier settings.py), et
l'ajoute a chaque evenement du fil d'activite sous la cle "il_y_a".

Idempotent. Ancres 100% ASCII.
"""
import pathlib
import re

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Fonction utilitaire : "il y a ..." en francais, sans dependance a
#    la locale Django (import local, pas besoin de toucher les imports
#    en haut du fichier).
# ---------------------------------------------------------------------
ANCRE_FONCTION = "def _delta_pct(valeurs):"
AJOUT_FONCTION = '''def _il_y_a_francais(dt):
    """Formate une date/datetime en "il y a ..." en francais, sans
    dependre de LANGUAGE_CODE (qui vaut 'en-us' dans ce projet et ferait
    parler anglais a |timesince)."""
    from django.utils import timezone as _tz
    from datetime import datetime as _datetime

    maintenant = _tz.now()
    if not isinstance(dt, _datetime):
        dt = _tz.make_aware(_datetime.combine(dt, _datetime.min.time()), _tz.get_current_timezone())
    elif _tz.is_naive(dt):
        dt = _tz.make_aware(dt, _tz.get_current_timezone())

    secondes = max((maintenant - dt).total_seconds(), 0)
    minutes = secondes / 60
    heures = minutes / 60
    jours = heures / 24

    if secondes < 60:
        return "moins d'une minute"
    if minutes < 60:
        n = int(minutes)
        return f"{n} minute{'s' if n > 1 else ''}"
    if heures < 24:
        n = int(heures)
        return f"{n} heure{'s' if n > 1 else ''}"
    if jours < 7:
        n = int(jours)
        return f"{n} jour{'s' if n > 1 else ''}"
    if jours < 30:
        n = int(jours / 7)
        return f"{n} semaine{'s' if n > 1 else ''}"
    if jours < 365:
        n = int(jours / 30)
        return f"{n} mois"
    n = int(jours / 365)
    return f"{n} an{'s' if n > 1 else ''}"


def _delta_pct(valeurs):'''
if "_il_y_a_francais" in texte:
    pass
elif ANCRE_FONCTION not in texte:
    erreurs.append("ANCRE_FONCTION introuvable")
else:
    texte = texte.replace(ANCRE_FONCTION, AJOUT_FONCTION, 1)

# ---------------------------------------------------------------------
# 2) Calcul du texte "il y a ..." pour chaque evenement du fil
#    d'activite, juste apres le decoupage de la liste (quel que soit le
#    nombre d'elements garde : [:8], [:4], ...).
# ---------------------------------------------------------------------
if '["il_y_a"]' in texte:
    pass
else:
    motif = re.compile(r"activite_recente = evenements\[:\d+\]")
    if motif.search(texte) is None:
        erreurs.append("Ligne 'activite_recente = evenements[:N]' introuvable")
    else:
        texte = motif.sub(
            lambda m: m.group(0) + "\n    for _e in activite_recente:\n        _e[\"il_y_a\"] = _il_y_a_francais(_e[\"date\"])",
            texte, count=1,
        )

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : foncier/dashboard_views.py mis a jour (fil d'activite en francais).")