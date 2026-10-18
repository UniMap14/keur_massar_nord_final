# -*- coding: utf-8 -*-
"""
Round 9 (home.html) : ajoute une petite icone de coin, en bas a droite
de chaque carte KPI (simple echo discret de l'icone principale, aucune
donnee chiffree ajoutee -- juste un habillage visuel conforme a la
maquette).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------
ANCRE_CSS = """    .geo-access-card::before,
    .quick-actions-banner::before {
        background-size: 42px 42px !important;
        opacity: 0.45 !important;
    }
</style>
{% endblock %}"""
AJOUT_CSS = """    .geo-access-card::before,
    .quick-actions-banner::before {
        background-size: 42px 42px !important;
        opacity: 0.45 !important;
    }

    /* ===== Icone de coin sur les cartes KPI (round 9) ===== */
    .kpi-card { position: relative !important; }
    .kpi-corner-icon {
        position: absolute;
        right: 10px;
        bottom: 8px;
        font-size: 13px;
        opacity: 0.16;
    }
</style>
{% endblock %}"""
if "Icone de coin sur les cartes KPI (round 9)" in texte:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# HTML : une icone de coin par carte KPI (echo de l'icone principale)
# ---------------------------------------------------------------------
ICONES = [
    "fa-sack-dollar",
    "fa-hourglass-half",
    "fa-triangle-exclamation",
    "fa-map",
    "fa-users",
    "fa-id-card",
    "fa-folder-open",
    "fa-road-bridge",
    "fa-envelope-open-text",
]

deja_toutes = all(
    f'<span class="kpi-corner-icon"><i class="fa-solid {ic}"></i></span>' in texte
    for ic in ICONES
)

if deja_toutes:
    pass
else:
    for ic in ICONES:
        ancre = f'<div class="kpi-icon"><i class="fa-solid {ic}"></i></div>'
        ajout = ancre + f'\n    <span class="kpi-corner-icon"><i class="fa-solid {ic}"></i></span>'
        marqueur = f'<span class="kpi-corner-icon"><i class="fa-solid {ic}"></i></span>'
        if marqueur in texte:
            continue
        if ancre not in texte:
            erreurs.append(f"ancre kpi-icon introuvable pour {ic}")
            continue
        texte = texte.replace(ancre, ajout, 1)

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
    print("OK : dashboard/home.html -- round 9 (icones de coin sur les cartes KPI).")