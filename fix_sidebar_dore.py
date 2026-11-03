# -*- coding: utf-8 -*-
"""
Applique a la sidebar du dashboard admin le meme degrade dore/marron
attenue que celui du footer du site public, et bascule tous les textes
(actuellement en blanc/blanc transparent, prevus pour un fond sombre)
en brun fonce pour qu'ils restent parfaitement lisibles sur le nouveau
fond clair.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_sidebar_dore.py
"""
import os

CHEMIN_CSS = os.path.join("foncier", "static", "dashboard", "css", "dashboard.css")

if not os.path.exists(CHEMIN_CSS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_CSS}")

with open(CHEMIN_CSS, "r", encoding="utf-8") as f:
    css = f.read()

deja_tout_ok = "--brand-gold-soft" in css and "linear-gradient(135deg, var(--brand-gold-soft)" in css

PATCHES = []  # liste de (nom, ancre, remplacement)

# 1) Nouvelles variables de couleur attenuees
PATCHES.append((
    "variables",
    "  --brand-gold-light:  #e9d9ad;\n",
    "  --brand-gold-light:  #e9d9ad;\n"
    "  --brand-gold-soft:   #d8bd84;\n"
    "  --brand-brown-soft:  #a9845f;\n",
))

# 2) Fond de la sidebar : degrade dore/marron au lieu du degrade sombre
PATCHES.append((
    "fond sidebar",
    """.sidebar {
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(201,152,46,0.10), transparent 55%),
    linear-gradient(185deg, var(--brand-brown-dark) 0%, #24180f 100%);
  color: var(--brand-cream-white);
  padding: 26px 18px 24px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(0,0,0,0.25);
}""",
    """.sidebar {
  background: linear-gradient(135deg, var(--brand-gold-soft) 0%, var(--brand-brown-soft) 100%);
  color: var(--brand-brown-dark);
  padding: 26px 18px 24px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(43,30,22,0.25);
}""",
))

# 3) Separateur sous le logo/nom de la commune
PATCHES.append((
    "separateur sidebar-brand",
    """.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 8px 22px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 18px;
}""",
    """.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 8px 22px;
  border-bottom: 1px solid rgba(43,30,22,0.18);
  margin-bottom: 18px;
}""",
))

# 4) Nom de la commune (etait blanc)
PATCHES.append((
    "sidebar-brand-text .name",
    """.sidebar-brand-text .name {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  font-size: 15px;
  color: #fff;
  line-height: 1.2;
}""",
    """.sidebar-brand-text .name {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  font-size: 15px;
  color: var(--brand-brown-dark);
  line-height: 1.2;
}""",
))

# 5) Sous-titre "FONCIER & FISCAL" (etait dore, invisible sur fond dore)
PATCHES.append((
    "sidebar-brand-text .sub",
    """.sidebar-brand-text .sub {
  font-size: 10.5px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--brand-gold);
}""",
    """.sidebar-brand-text .sub {
  font-size: 10.5px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--brand-brown-dark);
}""",
))

# 6) Titres de section ("VUE D'ENSEMBLE", "FONCIER", "CITOYENS"...)
PATCHES.append((
    "sidebar-section-label",
    """.sidebar-section-label {
  font-size: 10.5px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.38);
  padding: 18px 10px 8px;
}""",
    """.sidebar-section-label {
  font-size: 10.5px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: rgba(43,30,22,0.6);
  padding: 18px 10px 8px;
}""",
))

# 7) Liens du menu (Parcelles, Proprietaires, Zones, ...)
PATCHES.append((
    "sidebar-link",
    """.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: rgba(255,255,255,0.78);
  font-size: 13.5px;
  margin-bottom: 2px;
  transition: background .15s var(--ease), color .15s var(--ease), padding-left .15s var(--ease);
}""",
    """.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--brand-brown-dark);
  font-weight: 600;
  font-size: 13.5px;
  margin-bottom: 2px;
  transition: background .15s var(--ease), color .15s var(--ease), padding-left .15s var(--ease);
}""",
))

# 8) Survol d'un lien du menu
PATCHES.append((
    "sidebar-link:hover",
    """.sidebar-link:hover {
  background: rgba(255,255,255,0.07);
  color: #fff;
  padding-left: 16px;
}""",
    """.sidebar-link:hover {
  background: rgba(43,30,22,0.10);
  color: var(--brand-brown-dark);
  padding-left: 16px;
}""",
))

# 9) Badges numeriques (522, 20, 504, 22 ...)
PATCHES.append((
    "sidebar-link .count",
    """.sidebar-link .count {
  font-size: 11px;
  background: rgba(255,255,255,0.12);
  padding: 1px 8px;
  border-radius: 999px;
  font-variant-numeric: tabular-nums;
}""",
    """.sidebar-link .count {
  font-size: 11px;
  background: rgba(43,30,22,0.14);
  color: var(--brand-brown-dark);
  padding: 1px 8px;
  border-radius: 999px;
  font-variant-numeric: tabular-nums;
}""",
))

# 10) Icone du blason en bas de sidebar
PATCHES.append((
    "sidebar-emblem-icon",
    """.sidebar-emblem-icon {
  width: 38px; height: 38px;
  margin: 0 auto 10px;
  border-radius: 50%;
  border: 1px solid rgba(201,152,46,0.45);
  display: flex; align-items: center; justify-content: center;
  color: var(--brand-gold);
  font-size: 15px;
}""",
    """.sidebar-emblem-icon {
  width: 38px; height: 38px;
  margin: 0 auto 10px;
  border-radius: 50%;
  border: 1px solid rgba(43,30,22,0.35);
  display: flex; align-items: center; justify-content: center;
  color: var(--brand-brown-dark);
  font-size: 15px;
}""",
))

# 11) Separateur au-dessus du blason
PATCHES.append((
    "sidebar-emblem",
    """.sidebar-emblem {
  margin-top: 22px;
  padding: 18px 10px 4px;
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.08);
}""",
    """.sidebar-emblem {
  margin-top: 22px;
  padding: 18px 10px 4px;
  text-align: center;
  border-top: 1px solid rgba(43,30,22,0.18);
}""",
))

# 12) Petite citation italique sous le blason
PATCHES.append((
    "sidebar-emblem-tagline",
    """.sidebar-emblem-tagline {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-style: italic;
  font-size: 11.5px;
  line-height: 1.5;
  color: rgba(233,217,173,0.55);
}""",
    """.sidebar-emblem-tagline {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-style: italic;
  font-size: 11.5px;
  line-height: 1.5;
  color: rgba(43,30,22,0.65);
}""",
))

# 13) Separateur au-dessus du bloc utilisateur (bas de sidebar)
PATCHES.append((
    "sidebar-footer",
    """.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}""",
    """.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(43,30,22,0.18);
}""",
))

# 14) Nom de l'agent connecte
PATCHES.append((
    "sidebar-user .who",
    ".sidebar-user .who { font-size: 12.5px; color: #fff; line-height: 1.3; }",
    ".sidebar-user .who { font-size: 12.5px; color: var(--brand-brown-dark); line-height: 1.3; }",
))

# 15) Role de l'agent connecte (sous son nom)
PATCHES.append((
    "sidebar-user .who .role",
    ".sidebar-user .who .role { color: rgba(255,255,255,0.5); font-size: 11px; }",
    ".sidebar-user .who .role { color: rgba(43,30,22,0.65); font-size: 11px; }",
))

# 16) Lien "Se deconnecter"
PATCHES.append((
    "sidebar-logout",
    """.sidebar-logout {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(255,255,255,0.55);
  padding: 6px 8px;
  transition: color .15s var(--ease);
}""",
    """.sidebar-logout {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(43,30,22,0.7);
  padding: 6px 8px;
  transition: color .15s var(--ease);
}""",
))

PATCHES.append((
    "sidebar-logout:hover",
    ".sidebar-logout:hover { color: var(--brand-gold); }",
    ".sidebar-logout:hover { color: var(--brand-brown-dark); font-weight: 700; }",
))

if deja_tout_ok:
    print("OK : deja applique, rien a faire.")
else:
    erreurs = []
    for nom, ancre, remplacement in PATCHES:
        if remplacement in css:
            continue  # ce patch precis est deja applique
        if ancre not in css:
            erreurs.append(f"- ancre introuvable pour « {nom} »")
            continue
        if css.count(ancre) != 1:
            erreurs.append(f"- ancre « {nom} » trouvee {css.count(ancre)} fois (attendu 1)")
            continue
        css = css.replace(ancre, remplacement)

    if erreurs:
        print("ERREUR : certains blocs n'ont pas pu etre localises tels quels :")
        for e in erreurs:
            print(e)
        raise SystemExit("Aucun fichier n'a ete modifie (securite : tout ou rien).")

    with open(CHEMIN_CSS, "w", encoding="utf-8") as f:
        f.write(css)
    print("OK : sidebar du dashboard en degrade dore/marron, texte en brun fonce bien lisible.")
    print("-> Videz le cache navigateur (Ctrl+F5) pour voir le changement.")