# -*- coding: utf-8 -*-
"""
Round 21 (home.html) : supprime le motif de fond quadrille visible
derriere les cartes du tableau de bord (vient probablement de
dashboard.css, fichier partage non accessible ici -- on neutralise
via override cible sans changer la couleur de fond elle-meme).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = """    .dashboard-grid .quick-actions-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        height: calc(100% - 26px) !important;
    }"""
AJOUT = """    .dashboard-grid .quick-actions-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        height: calc(100% - 26px) !important;
    }

    /* ===== Fond de page epure, sans motif quadrille (round 21) ===== */
    body,
    .content,
    .main {
        background-image: none !important;
    }
    .panel,
    .kpi-card {
        box-shadow: 0 1px 3px rgba(42,38,32,0.06) !important;
        border: 1px solid rgba(42,38,32,0.07) !important;
    }"""
if "Fond de page epure, sans motif quadrille (round 21)" in texte:
    pass
elif ANCRE not in texte:
    erreurs.append("ANCRE introuvable")
else:
    texte = texte.replace(ANCRE, AJOUT, 1)

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 21 (fond epure, cartes avec bordure/ombre discrete).")