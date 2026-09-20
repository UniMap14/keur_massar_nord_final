CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

marqueur_temp = "###DEJA_CORRIGE###"
contenu = contenu.replace('SimplifyPreserveTopology("geom",', marqueur_temp + '("geom",')
n_restantes = contenu.count('Simplify("geom",')
contenu = contenu.replace('Simplify("geom",', 'SimplifyPreserveTopology("geom",')
contenu = contenu.replace(marqueur_temp + '("geom",', 'SimplifyPreserveTopology("geom",')

if n_restantes:
    changements += 1
    print(f"OK : {n_restantes} appel(s) Simplify(...) restant(s) corrige(s) en SimplifyPreserveTopology(...).")
else:
    print("INFO : plus aucun appel Simplify(...) a corriger.")

ancre_limite = "PARCELLES_MAX_PAR_REQUETE = 1500"
nouvelle_limite = "PARCELLES_MAX_PAR_REQUETE = 10000"

if ancre_limite in contenu:
    contenu = contenu.replace(ancre_limite, nouvelle_limite, 1)
    changements += 1
    print("OK : PARCELLES_MAX_PAR_REQUETE passe de 1500 a 10000.")
elif nouvelle_limite in contenu:
    print("DEJA FAIT : limite deja a 10000.")
else:
    print("ERREUR : ancre de la limite introuvable.")

if changements:
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"\n=== {changements} type(s) de changement enregistres. ===")
else:
    print("\n=== Rien enregistre. ===")