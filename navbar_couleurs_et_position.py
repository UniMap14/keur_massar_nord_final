CHEMIN = "foncier/static/foncier/css/style.css"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien1 = '''nav ul li a {
  color         : var(--text);
  font-size     : 13.5px;
  font-weight   : 500;
  padding       : 8px 14px;
  border-radius : 6px;
  transition    : all 0.25s;
  letter-spacing: 0.2px;
}'''

nouveau1 = '''nav ul li a {
  color         : var(--text);
  font-size     : 13.5px;
  font-weight   : 500;
  padding       : 13px 14px;
  border-radius : 6px;
  transition    : all 0.25s;
  letter-spacing: 0.2px;
}'''

if "padding       : 13px 14px;" in contenu:
    resultats.append("Padding (descendre les liens) : IGNORE (deja present)")
elif ancien1 in contenu:
    contenu = contenu.replace(ancien1, nouveau1, 1)
    resultats.append("Padding (descendre les liens) : OK")
else:
    resultats.append("Padding : ERREUR introuvable")

ancien2 = '''nav ul li a:hover,
nav ul li a.active {
  color      : var(--white);
  background : var(--green-dark);
}'''

nouveau2 = '''nav ul li a:hover,
nav ul li a.active {
  color      : var(--brown-dark, #2b1e16);
  background : var(--gold);
}'''

if "background : var(--gold);" in contenu and "nav ul li a:hover" in contenu:
    resultats.append("Couleur active doree : IGNORE (deja present)")
elif ancien2 in contenu:
    contenu = contenu.replace(ancien2, nouveau2, 1)
    resultats.append("Couleur active doree : OK")
else:
    resultats.append("Couleur active : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))