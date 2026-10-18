# -*- coding: utf-8 -*-
"""
Ajoute une valeur par defaut (date du jour) au champ date_publication du
modele Actualite, pour que le formulaire ne bloque plus si on l'oublie.
Le champ reste modifiable (on peut toujours choisir une autre date).

Idempotent.
"""
CHEMIN = "foncier/models.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

ANCIEN_CHAMP = '    date_publication = models.DateField(verbose_name="Date à afficher")'
NOUVEAU_CHAMP = '    date_publication = models.DateField(verbose_name="Date à afficher", default=timezone.now)'
IMPORT_TIMEZONE = "from django.utils import timezone"

if NOUVEAU_CHAMP in contenu:
    print("IGNORE (deja applique)")
elif ANCIEN_CHAMP not in contenu:
    print("ERREUR : champ d'origine introuvable tel quel, rien n'a ete modifie.")
else:
    idx_classe = contenu.index("class Actualite(models.Model):")
    partie_avant = contenu[:idx_classe]
    if IMPORT_TIMEZONE not in partie_avant:
        contenu = contenu.replace(
            "class Actualite(models.Model):",
            IMPORT_TIMEZONE + "\n\n\nclass Actualite(models.Model):",
            1,
        )
    contenu = contenu.replace(ANCIEN_CHAMP, NOUVEAU_CHAMP)
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : date_publication a maintenant une valeur par defaut (aujourd'hui)")