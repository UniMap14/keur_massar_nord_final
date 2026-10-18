# -*- coding: utf-8 -*-
"""
Round 4 :
1) Utilise le nouveau texte francais "il_y_a" (calcule par
   patch_dashboard_views_fr.py) a la place de "Il y a {{ item.date|timesince }}"
   qui s'affichait en anglais a cause de LANGUAGE_CODE='en-us'.
2) Force plus de colonnes sur la grille des cartes KPI (qui n'en
   affichait que 4, faisant prendre 3 lignes entieres aux 9 cartes) pour
   qu'elles tiennent sur 2 lignes et liberent de la hauteur.

Pre-requis : patch_dashboard_views_fr.py doit etre applique avant celui-ci
(sinon item.il_y_a sera vide).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Texte francais du fil d'activite
# ---------------------------------------------------------------------
ANCRE_TEMPS = '<div class="activity-time">Il y a {{ item.date|timesince }}</div>'
AJOUT_TEMPS = '<div class="activity-time">Il y a {{ item.il_y_a }}</div>'
if AJOUT_TEMPS in texte:
    pass
elif ANCRE_TEMPS not in texte:
    erreurs.append("ANCRE_TEMPS introuvable")
else:
    texte = texte.replace(ANCRE_TEMPS, AJOUT_TEMPS, 1)

# ---------------------------------------------------------------------
# 2) Grille KPI : plus de colonnes (auto-fit, cartes plus etroites)
#    pour que les 9 cartes tiennent sur 2 lignes au lieu de 3.
# ---------------------------------------------------------------------
ANCRE_KPIGRID = """    .kpi-grid { gap: 10px !important; }"""
AJOUT_KPIGRID = """    .kpi-grid {
        gap: 10px !important;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)) !important;
    }"""
if DEJA := ("grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)) !important;" in texte):
    pass
elif ANCRE_KPIGRID not in texte:
    erreurs.append("ANCRE_KPIGRID introuvable")
else:
    texte = texte.replace(ANCRE_KPIGRID, AJOUT_KPIGRID, 1)

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
    print("OK : dashboard/home.html mis a jour (texte francais + grille KPI plus large).")