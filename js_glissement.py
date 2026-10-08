CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''      var rotateur = document.getElementById('kmInfobarRotator');
      if (rotateur) {
        var diapos = rotateur.querySelectorAll('.km-ib-slide');
        var indexDiapo = 0;
        if (diapos.length > 1) {
          setInterval(function () {
            diapos[indexDiapo].classList.remove('is-active');
            indexDiapo = (indexDiapo + 1) % diapos.length;
            diapos[indexDiapo].classList.add('is-active');
          }, 3000);
        }
      }'''

nouveau = '''      var rotateur = document.getElementById('kmInfobarRotator');
      if (rotateur) {
        var diapos = rotateur.querySelectorAll('.km-ib-slide');
        var indexDiapo = 0;
        if (diapos.length > 1) {
          setInterval(function () {
            var ancienneDiapo = diapos[indexDiapo];
            ancienneDiapo.classList.remove('is-active');
            ancienneDiapo.classList.add('is-leaving');

            indexDiapo = (indexDiapo + 1) % diapos.length;
            diapos[indexDiapo].classList.add('is-active');

            setTimeout(function () {
              ancienneDiapo.classList.remove('is-leaving');
            }, 650);
          }, 3000);
        }
      }'''

if "is-leaving" in contenu and "ancienneDiapo" in contenu:
    print("IGNORE : JS du glissement deja en place.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : JS gere maintenant la transition en glissement.")
else:
    print("ERREUR : point d'ancrage introuvable.")