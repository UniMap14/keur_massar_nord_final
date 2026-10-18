# -*- coding: utf-8 -*-
"""
Ajoute le meme bandeau photo (hero) que la Cartotheque en haut de la page
Galerie, juste apres la navbar, avec le titre "Galerie photo".

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/galerie.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) CSS du bandeau hero (insere juste avant ".gal-grid-section{ ... }")
# ------------------------------------------------------------------
ANCIEN_CSS = '''    /* ---- Grille de photos ---- */
    .gal-grid-section{ max-width:1320px; margin:0 auto; padding:56px 60px 0; }'''

NOUVEAU_CSS = '''    /* ---- Bandeau photo (hero) ---- */
    .gal-hero{ position:relative; height:340px; overflow:hidden; }
    .gal-hero-img{ width:100%; height:100%; object-fit:cover; display:block; }
    .gal-hero-overlay{
        position:absolute; inset:0;
        background:linear-gradient(180deg, rgba(20,14,10,.4) 0%, rgba(20,14,10,.68) 100%);
    }
    .gal-hero-content{
        position:absolute; inset:0; display:flex; flex-direction:column;
        align-items:center; justify-content:center; gap:14px; padding:24px;
        text-align:center;
    }
    .gal-hero-content h1{
        font-family:'Playfair Display', serif; font-weight:800;
        font-size:clamp(28px,4vw,44px); color:#F7F2E8; margin:0;
        text-shadow:0 4px 18px rgba(0,0,0,.55);
    }
    .gal-hero-content p{
        max-width:680px; font-size:14.5px; line-height:1.7; color:#F0E6D2;
        margin:0; text-shadow:0 2px 10px rgba(0,0,0,.5);
    }
    @media (max-width: 700px){ .gal-hero{ height:300px; } }

    /* ---- Grille de photos ---- */
    .gal-grid-section{ max-width:1320px; margin:0 auto; padding:40px 60px 0; }'''

if '.gal-hero{' in contenu:
    pass
elif ANCIEN_CSS not in contenu:
    erreurs.append("ancre CSS .gal-grid-section introuvable")
else:
    contenu = contenu.replace(ANCIEN_CSS, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) HTML : bandeau photo juste apres <div class="gal-page">
# ------------------------------------------------------------------
ANCIEN_HTML = '''{% block content %}
<div class="gal-page">

    <section class="gal-grid-section">'''

NOUVEAU_HTML = '''{% block content %}
<div class="gal-page">

    <div class="gal-hero">
        <img src="{% static 'foncier/img/cartotheque-hero.jpg' %}" alt="Keur Massar Nord" class="gal-hero-img">
        <div class="gal-hero-overlay"></div>
        <div class="gal-hero-content">
            <h1>Galerie photo</h1>
            <p>Photos et images officielles de la commune de Keur Massar Nord.</p>
        </div>
    </div>

    <section class="gal-grid-section">'''

if 'class="gal-hero"' in contenu:
    pass
elif ANCIEN_HTML not in contenu:
    erreurs.append("ancre HTML gal-page/gal-grid-section introuvable")
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