# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''      btnDecouvrir.addEventListener('click', function (e) {
        e.preventDefault();
        document.body.classList.remove('km-hero-locked');
        var cible = document.getElementById('apres-hero');
        if (cible) cible.scrollIntoView({ behavior: 'smooth' });
      });'''

nouveau = '''      btnDecouvrir.addEventListener('click', function (e) {
        e.preventDefault();
        document.body.classList.remove('km-hero-locked');
        var cible = document.getElementById('page-chiffres');
        if (cible) cible.scrollIntoView({ behavior: 'smooth' });
      });'''

if "getElementById('page-chiffres')" in contenu:
    print("IGNORE : JS deja mis a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : JS du bouton 'Decouvrir' redirige vers la page 2.")
else:
    print("ERREUR : bloc JS introuvable tel quel.")