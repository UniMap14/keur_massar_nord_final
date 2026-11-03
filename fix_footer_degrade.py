# -*- coding: utf-8 -*-
"""
Adoucit le footer : au lieu d'un dore plein (sature), un degrade doux
dore -> marron, en tons attenues, avec le texte fonce deja en place
qui reste parfaitement lisible dessus.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_footer_degrade.py
"""
import os

CHEMIN_CSS = os.path.join("foncier", "static", "foncier", "css", "style.css")

if not os.path.exists(CHEMIN_CSS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_CSS}")

with open(CHEMIN_CSS, "r", encoding="utf-8") as f:
    css = f.read()

# ------------------------------------------------------------------
# 1) Ajouter deux variables de couleur attenuees (dore clair / marron clair)
# ------------------------------------------------------------------
ANCRE_VARS = "  --gold-dark   : #a67c1f;\n"
REMPLACEMENT_VARS = (
    "  --gold-dark   : #a67c1f;\n"
    "  --gold-soft   : #d8bd84;\n"
    "  --brown-soft  : #a9845f;\n"
)

deja_ok_vars = "--gold-soft" in css

if not deja_ok_vars:
    if ANCRE_VARS not in css:
        raise SystemExit("ERREUR : ancre VARS introuvable dans style.css. Aucun changement effectue.")
    if css.count(ANCRE_VARS) != 1:
        raise SystemExit("ERREUR : ancre VARS trouvee plusieurs fois, patch annule par securite.")
    css = css.replace(ANCRE_VARS, REMPLACEMENT_VARS)

# ------------------------------------------------------------------
# 2) Fond du footer : degrade doux dore -> marron (au lieu du dore plein)
# ------------------------------------------------------------------
ANCRE_FOOTER = """footer {
  background : var(--gold);
  color      : var(--green-dark);
  padding    : 44px 60px 0;
}"""
REMPLACEMENT_FOOTER = """footer {
  background : linear-gradient(135deg, var(--gold-soft) 0%, var(--brown-soft) 100%);
  color      : var(--green-dark);
  padding    : 44px 60px 0;
}"""

deja_ok_footer = "linear-gradient(135deg, var(--gold-soft)" in css

if not deja_ok_footer:
    if ANCRE_FOOTER not in css:
        raise SystemExit(
            "ERREUR : bloc 'footer {...}' introuvable tel quel dans style.css.\n"
            "Le fichier a peut-etre deja ete modifie differemment. Aucun changement effectue."
        )
    if css.count(ANCRE_FOOTER) != 1:
        raise SystemExit("ERREUR : bloc footer trouve plusieurs fois, patch annule par securite.")
    css = css.replace(ANCRE_FOOTER, REMPLACEMENT_FOOTER)

if deja_ok_vars and deja_ok_footer:
    print("OK : deja applique, rien a faire.")
else:
    with open(CHEMIN_CSS, "w", encoding="utf-8") as f:
        f.write(css)
    print("OK : footer en degrade dore/marron attenue, texte fonce conserve pour la lisibilite.")
    print("-> Videz le cache navigateur (Ctrl+F5) pour voir le changement.")