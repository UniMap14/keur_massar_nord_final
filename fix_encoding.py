import io

CHEMIN = "foncier/dashboard_views.py"

# utf-8-sig : lit normalement l'UTF-8, et retire automatiquement le BOM
# (marque invisible en debut de fichier) s'il est present - sans planter.
with io.open(CHEMIN, "r", encoding="utf-8-sig") as f:
    contenu = f.read()

if "\u00c3\u00a9" not in contenu and "\u00c3\u00a0" not in contenu:
    print("Aucune corruption d'encodage detectee.")
    print("Rien a faire ici, passe directement a fix_views.py.")
else:
    try:
        contenu_repare = contenu.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        print("ECHEC : la reparation automatique n'a pas pu s'appliquer proprement.")
        print("Detail :", e)
        print("Le fichier n'a PAS ete modifie. Montre-moi ce message d'erreur.")
    else:
        with io.open(CHEMIN, "w", encoding="utf-8", newline="") as f:
            f.write(contenu_repare)
        print("OK : encodage repare sur tout le fichier (BOM retire aussi).")
        print()
        import re
        m = re.search(r".{0,15}(a bien.{0,40})", contenu_repare)
        if m:
            print("Apres :", m.group(1))
