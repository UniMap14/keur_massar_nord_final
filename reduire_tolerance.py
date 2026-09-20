CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "TOLERANCE_SIMPLIFICATION_TOUTES = 0.0003  # bien plus grossier : vue de toute la commune dézoomée"
nouveau = "TOLERANCE_SIMPLIFICATION_TOUTES = 0.00003  # formes reconnaissables meme pour les petites parcelles"

if nouveau in contenu:
    print("DEJA FAIT : valeur deja reduite.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : tolerance reduite de 0.0003 a 0.00003 (formes bien plus fideles).")
else:
    print("ERREUR : ligne exacte introuvable, verification necessaire.")