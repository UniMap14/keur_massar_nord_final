Q = chr(34)
NL = chr(10)

CHEMIN = "foncier/models.py"
ANCRE = "numero_titre_foncier = models.CharField(max_length=100, blank=True, verbose_name=" + Q + "Numéro du titre foncier" + Q + ")"

AJOUT = (
    NL
    + "    simulation_fiscale = models.BooleanField(" + NL
    + "        default=False, verbose_name=" + Q + "Montant fiscal simulé" + Q + "," + NL
    + "        help_text=(" + NL
    + "            " + Q + "Coché si le montant de taxe/valeur locative provient d'une simulation " + Q + NL
    + "            " + Q + "académique, et non d'une déclaration ou d'un calcul réel." + Q + NL
    + "        )," + NL
    + "    )"
)

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "simulation_fiscale = models.BooleanField" in contenu:
    print("DEJA PRESENT : rien a faire.")
elif ANCRE not in contenu:
    print("ERREUR : ancre introuvable, rien modifie.")
else:
    contenu = contenu.replace(ANCRE, ANCRE + AJOUT, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ simulation_fiscale ajoute.")
