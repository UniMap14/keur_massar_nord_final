# -*- coding: utf-8 -*-
"""
Ajoute un badge thematique calcule (non stocke en base, pas de migration)
a chaque carte de la cartotheque, pour permettre un affichage plus structure
et une recherche texte cote front.

Idempotent : si le bloc existe deja, ne touche a rien.
"""
import re

CHEMIN = "foncier/views.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

ANCIEN = '''def cartotheque(request):
    """Page publique presentant les cartes thematiques d'analyse (MNT, pente, etc.)."""
    from .models import CarteThematique
    cartes = CarteThematique.objects.order_by('ordre', '-date_ajout')
    return render(request, 'foncier/cartotheque.html', {'cartes': cartes})'''

NOUVEAU = '''def cartotheque(request):
    """Page publique presentant les cartes thematiques d'analyse (MNT, pente, etc.)."""
    from .models import CarteThematique
    cartes = list(CarteThematique.objects.order_by('ordre', '-date_ajout'))

    # Badge thematique calcule a la volee (pas de champ en base, donc aucune
    # migration necessaire) : simple reconnaissance de mots-cles dans le titre.
    regles_theme = [
        ('pente', 'Relief & pentes'),
        ('drainage', 'Hydrologie'),
        ('densité', 'Infrastructures'),
        ('scolaire', 'Éducation'),
        ('santé', 'Santé'),
    ]
    for c in cartes:
        titre_minuscule = c.titre.lower()
        c.theme = 'Analyse territoriale'
        for mot_cle, libelle in regles_theme:
            if mot_cle in titre_minuscule:
                c.theme = libelle
                break

    return render(request, 'foncier/cartotheque.html', {'cartes': cartes})'''

if NOUVEAU in contenu:
    print("IGNORE (deja applique)")
elif ANCIEN not in contenu:
    print("ERREUR : bloc d'origine introuvable tel quel, rien n'a ete modifie.")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU)
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : vue cartotheque mise a jour (badge thematique ajoute)")