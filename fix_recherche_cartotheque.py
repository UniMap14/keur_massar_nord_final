# -*- coding: utf-8 -*-
"""
Corrige la recherche de la cartotheque : au chargement, toutes les
cartes etaient cachees tant qu'on n'avait pas choisi un theme dans le
menu deroulant (aucunFiltreChoisi = true), ce qui rendait la barre de
recherche inutilisable au premier regard. On affiche desormais toutes
les cartes par defaut, et la recherche texte filtre immediatement.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/cartotheque.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "// Affiche toutes les cartes des le chargement"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    ancien_js = "let themeActif = '';\n    let aucunFiltreChoisi = true;"
    if ancien_js not in contenu:
        raise SystemExit("ANCRE JS INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_js = (
        "let themeActif = '';\n"
        "    let aucunFiltreChoisi = false; // Toutes les cartes sont visibles des le chargement.\n"
        "    // Affiche toutes les cartes des le chargement (pas de filtre impose)."
    )
    contenu = contenu.replace(ancien_js, nouveau_js)

    ancien_select = '<option value="" disabled selected>Choisir un filtre...</option>\n            <option value="__TOUTES__">Toutes les cartes</option>'
    if ancien_select not in contenu:
        raise SystemExit("ANCRE SELECT INTROUVABLE - abandon partiel, le JS a deja ete modifie, verifie le fichier.")

    nouveau_select = '<option value="__TOUTES__" selected>Toutes les cartes</option>'
    contenu = contenu.replace(ancien_select, nouveau_select)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")