# -*- coding: utf-8 -*-
"""
Change le footer du site public (fond actuellement brun fonce) pour un
fond dore, avec un texte fonce lisible par-dessus (au lieu de blanc).

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_footer_dore.py
"""
import os

CHEMIN_CSS = os.path.join("foncier", "static", "foncier", "css", "style.css")
CHEMIN_HTML = os.path.join("foncier", "templates", "foncier", "base.html")

# ------------------------------------------------------------------
# 1) style.css : fond dore + couleurs de texte adaptees (lisibles)
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_CSS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_CSS}")

with open(CHEMIN_CSS, "r", encoding="utf-8") as f:
    css = f.read()

ANCRE_CSS = """footer {
  background : var(--green-dark);
  color      : white;
  padding    : 44px 60px 0;
}

.footer-grid {
  display               : grid;
  grid-template-columns : 1.6fr repeat(3, 1fr);
  gap                   : 40px;
  padding-bottom        : 32px;
  border-bottom         : 1px solid rgba(255, 255, 255, 0.1);
}

.footer-brand-desc {
  font-size   : 14px;
  color       : rgba(255, 255, 255, 0.52);
  line-height : 1.6;
  margin      : 12px 0;
  max-width   : 260px;
}

.footer-social {
  display: flex;
  gap    : 10px;
}

.soc-btn {
  width           : 36px;
  height          : 36px;
  border-radius   : 8px;
  background      : rgba(255, 255, 255, 0.14);
  border          : 1px solid rgba(255, 255, 255, 0.18);
  display         : flex;
  align-items     : center;
  justify-content : center;
  color           : rgba(255, 255, 255, 0.9);
  font-size       : 15px;
  transition      : all 0.25s;
}

.soc-btn:hover {
  background : var(--gold);
  color      : var(--green-dark);
}

.footer-col h4 {
  font-size      : 12px;
  font-weight    : 700;
  text-transform : uppercase;
  letter-spacing : 1.8px;
  color          : var(--gold);
  margin-bottom  : 14px;
}

.footer-col ul {
  list-style: none;
}

.footer-col ul li {
  margin-bottom: 8px;
}

.footer-col ul li a {
  color       : rgba(255, 255, 255, 0.52);
  font-size   : 14px;
  transition  : color 0.2s;
  display     : flex;
  align-items : center;
  gap         : 8px;
}

.footer-col ul li a:hover {
  color: white;
}

.footer-icon {
  color      : var(--gold);
  font-size  : 13px;
  flex-shrink: 0;
}

.footer-bottom {
  text-align : center;
  padding    : 14px 0;
}

.footer-bottom p {
  font-size : 13px;
  color     : rgba(255, 255, 255, 0.3);
}"""

REMPLACEMENT_CSS = """footer {
  background : var(--gold);
  color      : var(--green-dark);
  padding    : 44px 60px 0;
}

.footer-grid {
  display               : grid;
  grid-template-columns : 1.6fr repeat(3, 1fr);
  gap                   : 40px;
  padding-bottom        : 32px;
  border-bottom         : 1px solid rgba(60, 42, 32, 0.18);
}

.footer-brand-desc {
  font-size   : 14px;
  color       : rgba(60, 42, 32, 0.75);
  line-height : 1.6;
  margin      : 12px 0;
  max-width   : 260px;
}

.footer-social {
  display: flex;
  gap    : 10px;
}

.soc-btn {
  width           : 36px;
  height          : 36px;
  border-radius   : 8px;
  background      : rgba(60, 42, 32, 0.12);
  border          : 1px solid rgba(60, 42, 32, 0.22);
  display         : flex;
  align-items     : center;
  justify-content : center;
  color           : var(--green-dark);
  font-size       : 15px;
  transition      : all 0.25s;
}

.soc-btn:hover {
  background : var(--green-dark);
  color      : var(--gold);
}

.footer-col h4 {
  font-size      : 12px;
  font-weight    : 700;
  text-transform : uppercase;
  letter-spacing : 1.8px;
  color          : var(--green-dark);
  margin-bottom  : 14px;
}

.footer-col ul {
  list-style: none;
}

.footer-col ul li {
  margin-bottom: 8px;
}

.footer-col ul li a {
  color       : rgba(60, 42, 32, 0.72);
  font-size   : 14px;
  transition  : color 0.2s;
  display     : flex;
  align-items : center;
  gap         : 8px;
}

.footer-col ul li a:hover {
  color: var(--green-dark);
}

.footer-icon {
  color      : var(--green-dark);
  font-size  : 13px;
  flex-shrink: 0;
}

.footer-bottom {
  text-align : center;
  padding    : 14px 0;
}

.footer-bottom p {
  font-size : 13px;
  color     : rgba(60, 42, 32, 0.55);
}"""

deja_ok_css = REMPLACEMENT_CSS in css

if not deja_ok_css:
    if ANCRE_CSS not in css:
        raise SystemExit(
            "ERREUR : bloc CSS du footer introuvable tel quel dans style.css.\n"
            "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
        )
    if css.count(ANCRE_CSS) != 1:
        raise SystemExit("ERREUR : bloc CSS trouve plusieurs fois, patch annule par securite.")
    css = css.replace(ANCRE_CSS, REMPLACEMENT_CSS)
    with open(CHEMIN_CSS, "w", encoding="utf-8") as f:
        f.write(css)

# ------------------------------------------------------------------
# 2) base.html : le logo DGID etait force en blanc (pour fond sombre) ;
#    sur fond dore on le repasse en fonce pour qu'il reste lisible.
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_HTML):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_HTML}")

with open(CHEMIN_HTML, "r", encoding="utf-8") as f:
    html = f.read()

ANCRE_HTML = 'style="height:26px; margin-bottom:16px; filter: brightness(0) invert(1); opacity:0.75;"'
REMPLACEMENT_HTML = 'style="height:26px; margin-bottom:16px; filter: brightness(0); opacity:0.7;"'

deja_ok_html = REMPLACEMENT_HTML in html

if not deja_ok_html:
    if ANCRE_HTML not in html:
        raise SystemExit(
            "ERREUR : style du logo DGID introuvable tel quel dans base.html.\n"
            "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
        )
    if html.count(ANCRE_HTML) != 1:
        raise SystemExit("ERREUR : style du logo trouve plusieurs fois, patch annule par securite.")
    html = html.replace(ANCRE_HTML, REMPLACEMENT_HTML)
    with open(CHEMIN_HTML, "w", encoding="utf-8") as f:
        f.write(html)

if deja_ok_css and deja_ok_html:
    print("OK : deja applique, rien a faire.")
else:
    print("OK : footer repeint en dore avec texte fonce lisible.")
    print("-> " + CHEMIN_CSS + (" (deja a jour)" if deja_ok_css else " modifie"))
    print("-> " + CHEMIN_HTML + (" (deja a jour)" if deja_ok_html else " modifie"))
    print("-> Videz le cache navigateur (Ctrl+F5) pour bien voir le changement de CSS.")