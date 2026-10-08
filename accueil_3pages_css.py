# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. CSS : simplification de .km-hero-inner (grille -> centre)
# ============================================================
ancien_css1 = '''  .km-hero-inner{
    position:relative;
    z-index:2;
    max-width:1320px;margin:0 auto;width:100%;
    display:grid;grid-template-columns:1fr 380px;gap:40px;align-items:center;
    padding:36px 60px;
  }

  .km-hero-left{ display:flex; align-items:center; justify-content:center; min-height:200px; }'''

nouveau_css1 = '''  .km-hero-inner{
    position:relative;
    z-index:2;
    max-width:1320px;margin:0 auto;width:100%;
    display:flex;align-items:center;justify-content:center;
    padding:36px 60px;
    min-height:100%;
  }

  .km-hero-left{ display:flex; align-items:center; justify-content:center; min-height:200px; width:100%; }'''

if nouveau_css1 in contenu:
    resultats.append("CSS hero-inner : IGNORE (deja present)")
elif ancien_css1 in contenu:
    contenu = contenu.replace(ancien_css1, nouveau_css1, 1)
    resultats.append("CSS hero-inner : OK")
else:
    resultats.append("CSS hero-inner : ERREUR introuvable")

# ============================================================
# 2. CSS : media query hero (nettoyage grid-template-columns)
# ============================================================
ancien_css2 = '''  @media (max-width: 991px){
    .km-hero{ min-height:auto; }
    .km-hero-inner{ grid-template-columns:1fr; padding:40px 24px; gap:28px; }
    .km-hero-left{ min-height:auto; }
  }'''

nouveau_css2 = '''  @media (max-width: 991px){
    .km-hero{ min-height:auto; }
    .km-hero-inner{ padding:40px 24px; }
    .km-hero-left{ min-height:auto; }
  }'''

if nouveau_css2 in contenu:
    resultats.append("CSS media hero : IGNORE (deja present)")
elif ancien_css2 in contenu:
    contenu = contenu.replace(ancien_css2, nouveau_css2, 1)
    resultats.append("CSS media hero : OK")
else:
    resultats.append("CSS media hero : ERREUR introuvable")

# ============================================================
# 3. CSS : nouvelle section Page 2 (chiffres + maire) + intro bento
#    inseree juste avant le commentaire "Ticker d'actualites"
# ============================================================
ancien_css3 = '''  /* --- Ticker d'actualites (en haut de page) --- */'''

nouveau_css3 = '''  /* ===== PAGE 2 : Keur Massar en chiffres + Mot du Maire ===== */
  .km-page2{
    position:relative; min-height:100vh; display:flex; align-items:center;
    background: linear-gradient(160deg, var(--km-cream) 0%, var(--km-cream-2) 100%);
    overflow:hidden; padding:70px 60px;
  }
  .km-page2::before{
    content:""; position:absolute; inset:0;
    background-image:
      linear-gradient(rgba(43,27,20,.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(43,27,20,.05) 1px, transparent 1px);
    background-size:38px 38px;
    pointer-events:none;
  }
  .km-page2-eyebrow{
    position:relative; z-index:1;
    display:inline-flex; align-items:center; gap:8px;
    background:rgba(217,165,43,.14); border:1px solid rgba(217,165,43,.35);
    color:var(--km-gold-muted); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.6px;
    padding:7px 16px; border-radius:999px; margin-bottom:18px;
  }
  .km-page2-inner{
    position:relative; z-index:1;
    max-width:1200px; margin:0 auto; width:100%;
    display:grid; grid-template-columns:1fr 1fr; gap:54px; align-items:center;
  }
  .km-page2-left, .km-page2-right{ display:flex; flex-direction:column; gap:18px; }
  .km-stats-panel-big{ padding:30px 28px; }
  .km-stats-panel-big h3{ font-size:22px; margin-bottom:20px; }
  .km-stats-panel-big .km-stats-grid{ gap:14px; }
  .km-stats-panel-big .km-stat-item{ padding:18px 10px; }
  .km-stats-panel-big .km-stat-item strong{ font-size:24px; }
  .km-stats-panel-big .km-stat-item span{ font-size:10.5px; }
  .km-mayor-card-big{ padding:28px; }
  .km-mayor-card-big .km-mayor-photo{ width:110px; height:110px; }
  .km-mayor-card-big .km-mayor-text h5{ font-size:19px; }
  .km-mayor-card-big .km-mayor-text p{ font-size:13px; line-height:1.65; }
  .km-page2-cta{ align-self:flex-start; margin-top:4px; }

  @media (max-width: 991px){
    .km-page2{ padding:60px 24px; }
    .km-page2-inner{ grid-template-columns:1fr; gap:32px; }
  }

  /* ===== Intro texte au-dessus des fonctionnalites (page 3) ===== */
  .km-bento-intro{ text-align:center; max-width:680px; margin:0 auto 38px; }
  .km-bento-intro .section-label{ color:var(--km-gold-muted); }
  .km-bento-intro h2{
    font-family:'Playfair Display', serif; font-size:clamp(24px,3vw,32px); font-weight:800;
    color:var(--km-brown-dark); margin:10px 0 12px;
  }
  .km-bento-intro p{ font-size:14.5px; line-height:1.7; color:var(--km-brown-light); margin:0; }

  /* Petite touche "magnifique" : liseret dore anime au survol des tuiles */
  .km-bento-small{ position:relative; }
  .km-bento-small::before{
    content:""; position:absolute; top:0; left:0; right:0; height:3px; border-radius:18px 18px 0 0;
    background:linear-gradient(90deg, var(--km-gold-light), var(--km-gold));
    transform:scaleX(0); transform-origin:left; transition:transform .3s ease;
  }
  .km-bento-small:hover::before{ transform:scaleX(1); }

  /* --- Ticker d'actualites (en haut de page) --- */'''

if ".km-page2{" in contenu:
    resultats.append("CSS page2 : IGNORE (deja present)")
elif ancien_css3 in contenu:
    contenu = contenu.replace(ancien_css3, nouveau_css3, 1)
    resultats.append("CSS page2 + intro bento : OK")
else:
    resultats.append("CSS page2 : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))