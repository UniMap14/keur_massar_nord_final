CHEMIN = "foncier/static/foncier/css/style.css"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''nav ul li a:hover,
nav ul li a.active {
  color      : var(--white);
  background : var(--green-dark);
}'''

nouveau = '''nav ul li a:hover,
nav ul li a.active {
  color      : var(--brown-dark, #2b1e16);
  background : var(--gold);
}'''

if ancien not in contenu:
    print("DEJA CORRIGE ou introuvable (verifie manuellement si besoin).")
else:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : couleur active/hover du menu passee au dore.")