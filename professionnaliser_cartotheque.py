# -*- coding: utf-8 -*-
"""
Refond l'affichage des cartes de la Cartotheque : grille de cartes
compactes et homogenes (au lieu des blocs alternes pleine largeur),
images recadrees uniformement, survol plus soigne.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

def remplacer(ancien, nouveau, marqueur_deja_fait):
    global contenu, remplacements_ok
    if marqueur_deja_fait in contenu:
        return
    if ancien not in contenu:
        erreurs.append(f"ancre introuvable : {ancien[:60]}...")
        return
    contenu = contenu.replace(ancien, nouveau, 1)
    remplacements_ok += 1

# 1) Grille au lieu d'une colonne empilee
remplacer(
    '''    .carto-list{ max-width:1100px; margin:0 auto; padding:34px 24px 0; display:flex; flex-direction:column; gap:30px; }''',
    '''    .carto-list{
        max-width:1280px; margin:0 auto; padding:34px 24px 0;
        display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:28px;
    }''',
    'grid-template-columns:repeat(auto-fill'
)

# 2) Cartes homogenes (plus d'alternance gauche/droite)
remplacer(
    '''    .carto-card{
        background:#fff; border:1px solid var(--cp-border); border-radius:var(--cp-radius);
        overflow:hidden; display:grid; grid-template-columns: 1.15fr 1fr;
        box-shadow:var(--cp-shadow-md); transition: box-shadow .25s ease, transform .25s ease, opacity .25s ease;
        opacity:0; transform:translateY(16px);
    }
    .carto-card.carto-visible{ opacity:1; transform:translateY(0); }
    .carto-card:hover{ box-shadow:var(--cp-shadow-lg); transform:translateY(-4px); }
    .carto-card.carto-visible:hover{ transform:translateY(-4px); }
    .carto-card:nth-child(even){ grid-template-columns: 1fr 1.15fr; }
    .carto-card:nth-child(even) .carto-card-img{ order:2; }
    .carto-card.carto-hidden{ display:none; }''',
    '''    .carto-card{
        background:#fff; border:1px solid var(--cp-border); border-radius:var(--cp-radius);
        overflow:hidden; display:flex; flex-direction:column;
        box-shadow:var(--cp-shadow-md); transition: box-shadow .25s ease, transform .25s ease, opacity .25s ease;
        opacity:0; transform:translateY(16px);
    }
    .carto-card.carto-visible{ opacity:1; transform:translateY(0); }
    .carto-card:hover{ box-shadow:var(--cp-shadow-lg); transform:translateY(-6px); }
    .carto-card.carto-visible:hover{ transform:translateY(-6px); }
    .carto-card.carto-hidden{ display:none; }''',
    'display:flex; flex-direction:column;\n        box-shadow:var(--cp-shadow-md)'
)

# 3) Image recadree uniformement (ratio fixe au lieu de min-height variable)
remplacer(
    '''    .carto-card-img{
        position:relative; cursor:zoom-in; min-height:280px; overflow:hidden; background:var(--cp-cream-2);
    }
    .carto-card-img img{ width:100%; height:100%; object-fit:cover; display:block; transition: transform .4s ease; }
    .carto-card-img:hover img{ transform:scale(1.04); }
    .carto-card-zoom{
        position:absolute; bottom:14px; right:14px; width:36px; height:36px; border-radius:50%;
        background:rgba(43,27,20,.75); color:#fff; display:flex; align-items:center; justify-content:center;
        font-size:13px;
    }''',
    '''    .carto-card-img{
        position:relative; cursor:zoom-in; aspect-ratio:4/3; overflow:hidden; background:var(--cp-cream-2);
    }
    .carto-card-img img{ width:100%; height:100%; object-fit:cover; display:block; transition: transform .4s ease; }
    .carto-card-img::after{
        content:""; position:absolute; inset:0;
        background:linear-gradient(180deg, rgba(43,27,20,0) 45%, rgba(43,27,20,.6) 100%);
        opacity:0; transition:opacity .25s ease;
    }
    .carto-card-img:hover img{ transform:scale(1.06); }
    .carto-card-img:hover::after{ opacity:1; }
    .carto-card-zoom{
        position:absolute; bottom:14px; right:14px; width:34px; height:34px; border-radius:50%;
        background:rgba(255,255,255,.95); color:var(--cp-brown-dark); display:flex; align-items:center; justify-content:center;
        font-size:12px; opacity:0; transform:translateY(6px); transition: all .25s ease;
    }
    .carto-card-img:hover .carto-card-zoom{ opacity:1; transform:translateY(0); }''',
    'aspect-ratio:4/3; overflow:hidden'
)

# 4) Corps de carte plus compact
remplacer(
    '''    .carto-card-body{ padding:34px 38px; display:flex; flex-direction:column; justify-content:center; }''',
    '''    .carto-card-body{ padding:22px 24px; display:flex; flex-direction:column; flex:1; }''',
    'display:flex; flex-direction:column; flex:1; }'
)

# 5) Titre legerement plus petit (coherent avec des cartes plus compactes)
remplacer(
    '''    .carto-card-body h3{
        font-family:'Playfair Display', serif; font-size:21px; font-weight:800;
        color:var(--cp-brown-dark); margin:0 0 14px; line-height:1.3;
    }''',
    '''    .carto-card-body h3{
        font-family:'Playfair Display', serif; font-size:18px; font-weight:800;
        color:var(--cp-brown-dark); margin:0 0 10px; line-height:1.3;
    }''',
    'font-size:18px; font-weight:800;\n        color:var(--cp-brown-dark); margin:0 0 10px;'
)

# 6) Texte d'explication limite a 4 lignes (evite les cartes trop hautes/inegales)
remplacer(
    '''    .carto-card-body p{ font-size:14px; line-height:1.75; color:var(--cp-brown-light); margin:0; white-space:pre-line; }''',
    '''    .carto-card-body p{
        font-size:13.5px; line-height:1.65; color:var(--cp-brown-light); margin:0;
        display:-webkit-box; -webkit-line-clamp:4; -webkit-box-orient:vertical; overflow:hidden;
    }''',
    '-webkit-line-clamp:4'
)

# 7) Media query adaptee a la grille
remplacer(
    '''    @media (max-width: 860px){
        .carto-card, .carto-card:nth-child(even){ grid-template-columns: 1fr; }
        .carto-card:nth-child(even) .carto-card-img{ order:0; }
        .carto-card-img{ min-height:220px; }
        .carto-card-body{ padding:26px 24px; }
    }''',
    '''    @media (max-width: 860px){
        .carto-list{ grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:20px; }
    }
    @media (max-width: 520px){
        .carto-list{ grid-template-columns: 1fr; }
    }''',
    'minmax(260px, 1fr)'
)

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")