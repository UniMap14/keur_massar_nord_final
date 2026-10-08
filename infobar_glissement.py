CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  .km-ib-rotator{ position:relative; height:18px; flex:1; max-width:420px; }
  .km-ib-slide{
    position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:7px;
    opacity:0; transform:translateY(6px); transition:opacity .5s ease, transform .5s ease;
    pointer-events:none;
  }
  .km-ib-slide.is-active{ opacity:1; transform:translateY(0); pointer-events:auto; }'''

nouveau = '''  .km-ib-rotator{ position:relative; height:18px; flex:1; max-width:420px; overflow:hidden; }
  .km-ib-slide{
    position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:7px;
    opacity:0; transform:translateX(40px); transition:opacity .6s ease, transform .6s ease;
    pointer-events:none;
  }
  .km-ib-slide.is-active{ opacity:1; transform:translateX(0); pointer-events:auto; }
  .km-ib-slide.is-leaving{ opacity:0; transform:translateX(-40px); }'''

if ".km-ib-slide.is-leaving" in contenu:
    print("IGNORE : glissement deja en place.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : CSS du glissement horizontal ajoute.")
else:
    print("ERREUR : bloc CSS introuvable.")