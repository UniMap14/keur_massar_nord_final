# -*- coding: utf-8 -*-
"""
Ajoute le CSS du panneau "Actions rapides" redesigne : bandeau sombre/
dore (meme esprit que la tuile Geoportail SIG deja presente sur cette
page) + grille de tuiles d'action (icone coloree + libelle), a la place
de la rangee de boutons plats actuelle.

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    .geo-access-card:hover .geo-access-btn {
        box-shadow: 0 8px 18px rgba(201,152,46,.4);
    }

    @media (prefers-reduced-motion: reduce) {'''

NOUVEAU = '''    .geo-access-card:hover .geo-access-btn {
        box-shadow: 0 8px 18px rgba(201,152,46,.4);
    }

    /* ===== ACTIONS RAPIDES (bandeau + tuiles) ===== */
    .quick-actions-panel { overflow: hidden; }
    .quick-actions-banner {
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);
        padding: 22px 26px;
        position: relative;
        overflow: hidden;
    }
    .quick-actions-banner::before {
        content: "";
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(201,152,46,.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(201,152,46,.08) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    .quick-actions-banner-text { position: relative; z-index: 1; }
    .quick-actions-banner-text .eyebrow {
        font-size: 11px; letter-spacing: .1em; text-transform: uppercase;
        color: #c9982e; font-weight: 700; margin-bottom: 4px;
    }
    .quick-actions-banner-text .title {
        font-family: 'Playfair Display', serif; font-weight: 700;
        font-size: 17px; color: #fff;
    }
    .quick-actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1px;
        background: rgba(43,30,22,.08);
    }
    .quick-action-tile {
        display: flex; flex-direction: column; align-items: flex-start; gap: 10px;
        background: #fdfcfa;
        padding: 18px 16px;
        text-decoration: none;
        transition: background .15s ease, transform .15s ease;
    }
    .quick-action-tile:hover { background: rgba(201,152,46,0.06); transform: translateY(-2px); }
    .quick-action-tile span {
        font-size: 12.5px; font-weight: 600; color: #2a2620;
        line-height: 1.3;
    }
    .quick-action-icon {
        width: 34px; height: 34px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px;
    }
    .quick-action-icon.tone-green { background: rgba(58,125,68,0.12); color: #3a7d44; }
    .quick-action-icon.tone-red   { background: rgba(179,38,30,0.10); color: #b3261e; }
    .quick-action-icon.tone-gold  { background: rgba(201,152,46,0.14); color: #a3791f; }
    .quick-action-icon.tone-blue  { background: rgba(45,100,160,0.10); color: #2d64a0; }

    @media (prefers-reduced-motion: reduce) {'''

if '.quick-actions-banner {' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre CSS introuvable (.geo-access-card:hover .geo-access-btn)")
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