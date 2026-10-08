# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''      document.body.classList.add('km-hero-locked');
      btnDecouvrir.addEventListener('click', function (e) {
        e.preventDefault();
        document.body.classList.remove('km-hero-locked');
        var cible = document.getElementById('page-chiffres');
        if (cible) cible.scrollIntoView({ behavior: 'smooth' });
      });'''

nouveau = '''      document.body.classList.add('km-hero-locked');
      btnDecouvrir.addEventListener('click', function (e) {
        e.preventDefault();
        document.body.classList.remove('km-hero-locked');
        var cible = document.getElementById('page-chiffres');
        if (cible) cible.scrollIntoView({ behavior: 'smooth' });
      });

      var btnMotDuMaireBas = document.getElementById('btnMotDuMaireBas');
      if (btnMotDuMaireBas) {
        btnMotDuMaireBas.addEventListener('click', function (e) {
          e.preventDefault();
          document.body.classList.remove('km-hero-locked');
          var cible = document.getElementById('page-chiffres');
          if (cible) cible.scrollIntoView({ behavior: 'smooth' });
        });
      }'''

if "btnMotDuMaireBas" in contenu and "addEventListener('click', function (e) {\n          e.preventDefault();" in contenu:
    print("IGNORE : JS deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Mot du Maire' de la bande debloque aussi le defilement.")
else:
    print("ERREUR : point d'ancrage introuvable.")