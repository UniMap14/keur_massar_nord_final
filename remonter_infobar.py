CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  .km-hero-infobar{
    position:absolute; bottom:0; left:0; right:0; z-index:3;
    background:rgba(20,14,10,.6); backdrop-filter:blur(6px);
    border-top:1px solid rgba(217,165,43,.25);
  }'''

nouveau = '''  .km-hero-infobar{
    position:absolute; bottom:28px; left:0; right:0; z-index:3;
    background:rgba(20,14,10,.6); backdrop-filter:blur(6px);
    border-top:1px solid rgba(217,165,43,.25);
  }'''

if "bottom:28px; left:0; right:0; z-index:3;" in contenu:
    print("IGNORE : deja remontee.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : bande remontee de 28px par rapport au bas.")
else:
    print("ERREUR : bloc introuvable.")