CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def _pied_de_page_document(c, marge, hauteur_page_url, texte_verif):
    """Pied de page commun (authenticite + date d'edition)."""
    from django.utils import timezone
    c.setFillColor(HexColor("#6b5d4f"))'''

nouveau = '''def _pied_de_page_document(c, marge, hauteur_page_url, texte_verif):
    """Pied de page commun (authenticite + date d'edition)."""
    from django.utils import timezone
    from reportlab.lib.colors import HexColor
    c.setFillColor(HexColor("#6b5d4f"))'''

if nouveau in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : import HexColor ajoute dans _pied_de_page_document.")
else:
    print("ERREUR : bloc exact introuvable.")