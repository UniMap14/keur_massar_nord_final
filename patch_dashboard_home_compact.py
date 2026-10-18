# -*- coding: utf-8 -*-
"""
Compacte le tableau de bord pour qu'il tienne au maximum sur un seul
ecran : graphiques moins hauts, espacements reduits, et surtout une
hauteur maximale + defilement interne sur les panneaux "flush" (listes
et tableaux : Derniers paiements, Parcelles en retard, Activite
recente), qui sont ceux qui peuvent grandir sans limite selon le
volume de donnees reelles.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

DEJA_APPLIQUE = "panel-body.flush { max-height" in texte

# ---------------------------------------------------------------------
# 1) Graphiques moins hauts
# ---------------------------------------------------------------------
ANCRE_CHARTS = """    .chart-wrap { position: relative; width: 100%; height: 300px; }
    .chart-wrap-sm { height: 220px; }"""
AJOUT_CHARTS = """    .chart-wrap { position: relative; width: 100%; height: 190px; }
    .chart-wrap-sm { height: 150px; }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_CHARTS not in texte:
    erreurs.append("ANCRE_CHARTS introuvable")
else:
    texte = texte.replace(ANCRE_CHARTS, AJOUT_CHARTS, 1)

# ---------------------------------------------------------------------
# 2) Grille : espacement reduit
# ---------------------------------------------------------------------
ANCRE_GAP = """    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 20px;
        align-items: stretch;
    }"""
AJOUT_GAP = """    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        align-items: stretch;
    }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_GAP not in texte:
    erreurs.append("ANCRE_GAP introuvable")
else:
    texte = texte.replace(ANCRE_GAP, AJOUT_GAP, 1)

# ---------------------------------------------------------------------
# 3) Mini-carte moins haute
# ---------------------------------------------------------------------
ANCRE_CARTE = '    .mini-map-canvas { height: 180px; width: 100%; }'
AJOUT_CARTE = '    .mini-map-canvas { height: 140px; width: 100%; }'
if DEJA_APPLIQUE:
    pass
elif ANCRE_CARTE not in texte:
    erreurs.append("ANCRE_CARTE introuvable")
else:
    texte = texte.replace(ANCRE_CARTE, AJOUT_CARTE, 1)

# ---------------------------------------------------------------------
# 4) Fil d'activite : espacement reduit
# ---------------------------------------------------------------------
ANCRE_ACTFEED = '    .activity-feed { list-style: none; margin: 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 14px; }'
AJOUT_ACTFEED = '    .activity-feed { list-style: none; margin: 0; padding: 10px 14px; display: flex; flex-direction: column; gap: 9px; }'
if DEJA_APPLIQUE:
    pass
elif ANCRE_ACTFEED not in texte:
    erreurs.append("ANCRE_ACTFEED introuvable")
else:
    texte = texte.replace(ANCRE_ACTFEED, AJOUT_ACTFEED, 1)

# ---------------------------------------------------------------------
# 5) Bandeau actions rapides : moins de padding
# ---------------------------------------------------------------------
ANCRE_BANNER = """    .quick-actions-banner {
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);
        padding: 22px 26px;"""
AJOUT_BANNER = """    .quick-actions-banner {
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);
        padding: 14px 20px;"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_BANNER not in texte:
    erreurs.append("ANCRE_BANNER introuvable")
else:
    texte = texte.replace(ANCRE_BANNER, AJOUT_BANNER, 1)

# ---------------------------------------------------------------------
# 6) Tuiles d'actions rapides : moins de padding
# ---------------------------------------------------------------------
ANCRE_TILE = """    .quick-action-tile {
        display: flex; flex-direction: column; align-items: flex-start; gap: 10px;
        background: #fdfcfa;
        padding: 18px 16px;"""
AJOUT_TILE = """    .quick-action-tile {
        display: flex; flex-direction: column; align-items: flex-start; gap: 8px;
        background: #fdfcfa;
        padding: 12px 14px;"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_TILE not in texte:
    erreurs.append("ANCRE_TILE introuvable")
else:
    texte = texte.replace(ANCRE_TILE, AJOUT_TILE, 1)

# ---------------------------------------------------------------------
# 7) NOUVEAU : hauteur maximale + defilement interne pour les panneaux
#    "flush" de la grille (tableaux et listes) -- c'est ce qui borne
#    vraiment la hauteur totale de la page.
# ---------------------------------------------------------------------
ANCRE_FLUSH = """    .activity-text { flex: 1; }
    .activity-title { font-size: 12.5px; color: var(--ink, #2a2620); line-height: 1.4; }
    .activity-time { font-size: 11px; color: var(--ink-quiet, #7a7266); margin-top: 2px; }
</style>
{% endblock %}"""
AJOUT_FLUSH = """    .activity-text { flex: 1; }
    .activity-title { font-size: 12.5px; color: var(--ink, #2a2620); line-height: 1.4; }
    .activity-time { font-size: 11px; color: var(--ink-quiet, #7a7266); margin-top: 2px; }

    /* ===== Plafond de hauteur + defilement interne (tient sur un ecran) ===== */
    .dashboard-grid .panel-body.flush { max-height: 280px; overflow-y: auto; }
</style>
{% endblock %}"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_FLUSH not in texte:
    erreurs.append("ANCRE_FLUSH introuvable")
else:
    texte = texte.replace(ANCRE_FLUSH, AJOUT_FLUSH, 1)

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
    print("OK : dashboard/home.html compacte (tient sur un ecran).")