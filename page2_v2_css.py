# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  /* ===== PAGE 2 : Keur Massar en chiffres + Mot du Maire ===== */
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
  }'''

nouveau = '''  /* ===== PAGE 2 : Keur Massar en chiffres + Mot du Maire (v2) ===== */
  .km-page2{
    position:relative; min-height:100vh; display:flex; flex-direction:column; justify-content:center;
    background: var(--km-cream);
    padding:80px 60px 60px;
  }

  .km-page2-weather-badge{ position:absolute; top:28px; right:60px; z-index:3; }
  .km-page2-weather-badge .km-weather-box{ padding:8px 18px; border-radius:999px; }

  .km-page2-stats-bar{
    display:grid; grid-template-columns:repeat(4,1fr);
    max-width:1180px; margin:0 auto 76px; position:relative;
  }
  .km-page2-stat{ text-align:center; padding:0 22px; position:relative; }
  .km-page2-stat:not(:last-child)::after{
    content:""; position:absolute; right:0; top:8%; bottom:8%; width:1px; background:var(--km-border);
  }
  .km-page2-stat i{ color:var(--km-gold); font-size:22px; margin-bottom:14px; display:block; }
  .km-page2-stat strong{
    font-family:'Playfair Display', serif; font-weight:800; font-size:clamp(26px,2.8vw,38px);
    color:var(--km-gold-muted); display:block; line-height:1;
  }
  .km-page2-stat strong::after{ content:""; display:block; width:26px; height:2px; background:var(--km-brown-dark); margin:13px auto 0; opacity:.45; }
  .km-page2-stat span{
    display:block; margin-top:10px; font-size:10.5px; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; color:var(--km-brown-light);
  }

  .km-page2-maire{
    max-width:1180px; margin:0 auto; width:100%;
    display:grid; grid-template-columns:1.15fr .85fr; gap:60px; align-items:center;
  }
  .km-page2-eyebrow-line{
    display:inline-flex; align-items:center; gap:10px;
    font-size:11.5px; font-weight:800; letter-spacing:1.5px; text-transform:uppercase;
    color:var(--km-gold-muted); margin-bottom:18px;
  }
  .km-page2-eyebrow-line::before{ content:""; width:28px; height:2px; background:var(--km-gold-muted); display:inline-block; }
  .km-page2-maire-text h2{
    font-family:'Playfair Display', serif; font-weight:800; line-height:1.18;
    font-size:clamp(27px,3.2vw,38px); color:var(--km-brown-dark); margin:0 0 22px;
  }
  .km-page2-maire-text h2 em{ color:var(--km-gold-muted); font-style:italic; }
  .km-page2-quote{
    position:relative; padding-left:32px; margin:0 0 16px; font-size:15px; line-height:1.7;
    color:var(--km-brown-dark); font-style:italic;
  }
  .km-page2-quote i{ position:absolute; left:0; top:3px; color:var(--km-gold); font-size:15px; opacity:.75; }
  .km-page2-bio{ font-size:13.5px; line-height:1.75; color:var(--km-brown-light); margin:0 0 30px; }
  .km-page2-maire-actions{ display:flex; gap:14px; flex-wrap:wrap; }

  .km-page2-photo-wrap{ position:relative; }
  .km-page2-photo-wrap::before{
    content:""; position:absolute; top:18px; right:-18px; bottom:-18px; left:18px;
    border:2px solid var(--km-gold); border-radius:var(--km-radius); z-index:0;
  }
  .km-page2-photo{
    position:relative; z-index:1; width:100%; aspect-ratio:4/4.6; object-fit:cover;
    border-radius:var(--km-radius); box-shadow:var(--km-shadow-lg); display:block;
  }

  @media (max-width: 991px){
    .km-page2{ padding:60px 24px 50px; }
    .km-page2-weather-badge{ position:static; display:flex; justify-content:center; margin-bottom:24px; }
    .km-page2-stats-bar{ grid-template-columns:repeat(2,1fr); gap:30px 0; margin-bottom:46px; }
    .km-page2-stat:nth-child(2)::after{ display:none; }
    .km-page2-maire{ grid-template-columns:1fr; gap:36px; }
    .km-page2-photo-wrap{ order:-1; max-width:300px; margin:0 auto; }
  }'''

if "km-page2-stats-bar{" in contenu:
    print("IGNORE : CSS page2 v2 deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : CSS page2 remplacee par la version v2 (barre de stats + mot du maire 2 colonnes).")
else:
    print("ERREUR : bloc CSS page2 (v1) introuvable tel quel.")