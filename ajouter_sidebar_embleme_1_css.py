# -*- coding: utf-8 -*-
"""
Ajoute le CSS de l'embleme dore decoratif + la phrase en bas de la
sidebar (au-dessus du bloc utilisateur/deconnexion), dans l'esprit
du modele fourni (icone cerclee d'or + petite phrase en italique).

Idempotent.
"""
CHEMIN = "foncier/static/dashboard/css/dashboard.css"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}'''

NOUVEAU = '''.sidebar-emblem {
  margin-top: 22px;
  padding: 18px 10px 4px;
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.sidebar-emblem-icon {
  width: 38px; height: 38px;
  margin: 0 auto 10px;
  border-radius: 50%;
  border: 1px solid rgba(201,152,46,0.45);
  display: flex; align-items: center; justify-content: center;
  color: var(--brand-gold);
  font-size: 15px;
}

.sidebar-emblem-tagline {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-style: italic;
  font-size: 11.5px;
  line-height: 1.5;
  color: rgba(233,217,173,0.55);
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}'''

if '.sidebar-emblem {' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (.sidebar-footer)")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")