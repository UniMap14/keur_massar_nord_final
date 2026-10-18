# -*- coding: utf-8 -*-
"""
Round 13 (home.html) : certains panneaux (Dernieres demandes vide,
Repartition par type avec sa legende, message "pas assez de donnees
par zone") depassaient la hauteur de tuile (135px) et etaient coupes
de maniere invisible (overflow: hidden). On remplace par un
defilement interne discret (overflow-y: auto) + un etat vide plus
compact, pour que le contenu reste accessible sans jamais faire
deborder la page entiere.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) panel-body : defilement interne au lieu de coupe invisible
# ---------------------------------------------------------------------
ANCRE_BODY = """    .dashboard-grid .panel-body {
        overflow: hidden !important;
    }"""
AJOUT_BODY = """    .dashboard-grid .panel-body {
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }"""
if "overflow-y: auto !important;\n        overflow-x: hidden !important;" in texte:
    pass
elif ANCRE_BODY not in texte:
    erreurs.append("ANCRE_BODY introuvable")
else:
    texte = texte.replace(ANCRE_BODY, AJOUT_BODY, 1)

# ---------------------------------------------------------------------
# 2) Etat vide compact (icone + texte) pour les tuiles reduites
# ---------------------------------------------------------------------
ANCRE_FIN = """    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 12 !important; }"""
AJOUT_FIN = """    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 12 !important; }

    /* ===== Etat vide compact dans les tuiles reduites (round 13) ===== */
    .dashboard-grid .empty-state {
        padding: 10px 8px !important;
        font-size: 11px !important;
        line-height: 1.35 !important;
    }
    .dashboard-grid .empty-state .icon {
        width: 26px !important;
        height: 26px !important;
        font-size: 11px !important;
        margin: 0 auto 6px !important;
    }"""
if "Etat vide compact dans les tuiles reduites (round 13)" in texte:
    pass
elif ANCRE_FIN not in texte:
    erreurs.append("ANCRE_FIN introuvable")
else:
    texte = texte.replace(ANCRE_FIN, AJOUT_FIN, 1)

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 13 (contenu scrollable + etat vide compact).")