# -*- coding: utf-8 -*-
"""
Passe tout le texte du footer en noir plein (fini les rgba attenues) et
en gras, en gardant le degrade dore/marron du fond.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_footer_texte_noir_gras.py
"""
import os

CHEMIN_CSS = os.path.join("foncier", "static", "foncier", "css", "style.css")

if not os.path.exists(CHEMIN_CSS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_CSS}")

with open(CHEMIN_CSS, "r", encoding="utf-8") as f:
    css = f.read()

ANCRE = """footer {
  background : linear-gradient(135deg, var(--gold-soft) 0%, var(--brown-soft) 100%);
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

REMPLACEMENT = """footer {
  background : linear-gradient(135deg, var(--gold-soft) 0%, var(--brown-soft) 100%);
  color      : #000000;
  font-weight: 700;
  padding    : 44px 60px 0;
}

.footer-grid {
  display               : grid;
  grid-template-columns : 1.6fr repeat(3, 1fr);
  gap                   : 40px;
  padding-bottom        : 32px;
  border-bottom         : 1px solid rgba(0, 0, 0, 0.18);
}

.footer-brand-desc {
  font-size   : 14px;
  color       : #000000;
  font-weight : 700;
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
  background      : rgba(0, 0, 0, 0.12);
  border          : 1px solid rgba(0, 0, 0, 0.22);
  display         : flex;
  align-items     : center;
  justify-content : center;
  color           : #000000;
  font-size       : 15px;
  transition      : all 0.25s;
}

.soc-btn:hover {
  background : #000000;
  color      : var(--gold);
}

.footer-col h4 {
  font-size      : 12px;
  font-weight    : 700;
  text-transform : uppercase;
  letter-spacing : 1.8px;
  color          : #000000;
  margin-bottom  : 14px;
}

.footer-col ul {
  list-style: none;
}

.footer-col ul li {
  margin-bottom: 8px;
}

.footer-col ul li a {
  color       : #000000;
  font-weight : 700;
  font-size   : 14px;
  transition  : color 0.2s;
  display     : flex;
  align-items : center;
  gap         : 8px;
}

.footer-col ul li a:hover {
  color: var(--gold-dark);
}

.footer-icon {
  color      : #000000;
  font-size  : 13px;
  flex-shrink: 0;
}

.footer-bottom {
  text-align : center;
  padding    : 14px 0;
}

.footer-bottom p {
  font-size   : 13px;
  font-weight : 700;
  color       : #000000;
}"""

deja_ok = REMPLACEMENT in css

if not deja_ok:
    if ANCRE not in css:
        raise SystemExit(
            "ERREUR : bloc CSS du footer introuvable tel quel dans style.css.\n"
            "Le fichier a peut-etre deja ete modifie differemment. Aucun changement effectue."
        )
    if css.count(ANCRE) != 1:
        raise SystemExit("ERREUR : bloc footer trouve plusieurs fois, patch annule par securite.")
    css = css.replace(ANCRE, REMPLACEMENT)
    with open(CHEMIN_CSS, "w", encoding="utf-8") as f:
        f.write(css)
    print("OK : texte du footer passe en noir et en gras (fond degrade dore/marron conserve).")
    print("-> Videz le cache navigateur (Ctrl+F5) pour voir le changement.")
else:
    print("OK : deja applique, rien a faire.")