# -*- coding: utf-8 -*-
"""
Corrige le widget du champ date_publication dans ActualiteForm : il
utilisait un DateTimeInput (date+heure) alors que le modele est un
DateField (date seule), ce qui faisait toujours echouer la validation.

Idempotent.
"""
CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

ANCIEN = '''            "date_publication": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),'''
NOUVEAU = '''            "date_publication": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),'''

if NOUVEAU in contenu:
    print("IGNORE (deja applique)")
elif ANCIEN not in contenu:
    print("ERREUR : ligne d'origine introuvable telle quelle, rien n'a ete modifie.")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU)
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : widget de date_publication corrige (DateInput au lieu de DateTimeInput)")