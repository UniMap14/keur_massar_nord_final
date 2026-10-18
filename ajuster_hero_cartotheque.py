# -*- coding: utf-8 -*-
"""
Deplace le texte descriptif DANS le bandeau photo (sous le titre) et
supprime la section .carto-intro separee, pour que la barre de
recherche/filtres remonte juste apres le bandeau.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) CSS : agrandir le bandeau, ajouter le style du texte dans le hero,
#    retirer les regles .carto-intro devenues inutiles
# ------------------------------------------------------------------
ANCIEN_CSS = '''    .carto-hero{ position:relative; height:260px; overflow:hidden; }
    .carto-hero-img{ width:100%; height:100%; object-fit:cover; display:block; }
    .carto-hero-overlay{
        position:absolute; inset:0;
        background:linear-gradient(180deg, rgba(20,14,10,.35) 0%, rgba(20,14,10,.6) 100%);
    }
    .carto-hero-content{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }
    .carto-hero-content h1{
        font-family:'Playfair Display', serif; font-weight:800;
        font-size:clamp(28px,4vw,44px); color:#F7F2E8; margin:0;
        text-shadow:0 4px 18px rgba(0,0,0,.55);
    }
    @media (max-width: 700px){ .carto-hero{ height:180px; } }

    .carto-intro{ max-width:760px; margin:0 auto; padding:34px 24px 10px; text-align:center; }
    .carto-intro h1{
        font-family:'Playfair Display', serif; font-size:clamp(26px,3.6vw,38px); font-weight:800;
        color:var(--cp-brown-dark); margin:0 0 14px;
    }
    .carto-intro p{ font-size:15px; line-height:1.7; color:var(--cp-brown-light); margin:0; }

    .carto-toolbar{
        max-width:620px; margin:30px auto 0; padding:0 24px;
        display:flex; flex-direction:column; align-items:center; gap:10px;
    }'''

NOUVEAU_CSS = '''    .carto-hero{ position:relative; height:340px; overflow:hidden; }
    .carto-hero-img{ width:100%; height:100%; object-fit:cover; display:block; }
    .carto-hero-overlay{
        position:absolute; inset:0;
        background:linear-gradient(180deg, rgba(20,14,10,.4) 0%, rgba(20,14,10,.68) 100%);
    }
    .carto-hero-content{
        position:absolute; inset:0; display:flex; flex-direction:column;
        align-items:center; justify-content:center; gap:14px; padding:24px;
        text-align:center;
    }
    .carto-hero-content h1{
        font-family:'Playfair Display', serif; font-weight:800;
        font-size:clamp(28px,4vw,44px); color:#F7F2E8; margin:0;
        text-shadow:0 4px 18px rgba(0,0,0,.55);
    }
    .carto-hero-content p{
        max-width:680px; font-size:14.5px; line-height:1.7; color:#F0E6D2;
        margin:0; text-shadow:0 2px 10px rgba(0,0,0,.5);
    }
    @media (max-width: 700px){ .carto-hero{ height:300px; } }

    .carto-toolbar{
        max-width:620px; margin:26px auto 0; padding:0 24px;
        display:flex; flex-direction:column; align-items:center; gap:10px;
    }'''

if '.carto-hero-content p{' in contenu:
    pass
elif ANCIEN_CSS not in contenu:
    erreurs.append("ancre CSS introuvable")
else:
    contenu = contenu.replace(ANCIEN_CSS, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) HTML : texte dans le hero, suppression de .carto-intro
# ------------------------------------------------------------------
ANCIEN_HTML = '''    <div class="carto-hero">
        <img src="{% static 'foncier/img/cartotheque-hero.jpg' %}" alt="Keur Massar Nord" class="carto-hero-img">
        <div class="carto-hero-overlay"></div>
        <div class="carto-hero-content">
            <h1>La cartoth\u00e8que</h1>
        </div>
    </div>

    <div class="carto-intro">
        <p>Les cartes d'analyse r\u00e9alis\u00e9es sur le territoire de Keur Massar Nord \u2014 mod\u00e8le num\u00e9rique de terrain, pente, densit\u00e9 et autres donn\u00e9es g\u00e9ographiques \u2014 avec leur explication.</p>
    </div>'''

NOUVEAU_HTML = '''    <div class="carto-hero">
        <img src="{% static 'foncier/img/cartotheque-hero.jpg' %}" alt="Keur Massar Nord" class="carto-hero-img">
        <div class="carto-hero-overlay"></div>
        <div class="carto-hero-content">
            <h1>La cartoth\u00e8que</h1>
            <p>Les cartes d'analyse r\u00e9alis\u00e9es sur le territoire de Keur Massar Nord \u2014 mod\u00e8le num\u00e9rique de terrain, pente, densit\u00e9 et autres donn\u00e9es g\u00e9ographiques \u2014 avec leur explication.</p>
        </div>
    </div>'''

if '<h1>La cartoth\u00e8que</h1>\n            <p>' in contenu:
    pass
elif ANCIEN_HTML not in contenu:
    erreurs.append("ancre HTML hero/intro introuvable")
else:
    contenu = contenu.replace(ANCIEN_HTML, NOUVEAU_HTML, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")