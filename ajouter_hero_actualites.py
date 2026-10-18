# -*- coding: utf-8 -*-
"""
Ajoute le meme bandeau photo (hero, petite bande) en haut de la page
Actualites, juste apres la navbar.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/actualites_liste.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) CSS du bandeau hero (insere juste apres <style>)
# ------------------------------------------------------------------
ANCIEN_CSS = '''{% block extra_head %}
<style>
  .actu-toolbar {'''

NOUVEAU_CSS = '''{% block extra_head %}
<style>
  .actu-hero{ position:relative; height:110px; overflow:hidden; }
  .actu-hero-img{ width:100%; height:100%; object-fit:cover; display:block; }
  .actu-hero-overlay{
    position:absolute; inset:0;
    background:linear-gradient(180deg, rgba(20,14,10,.4) 0%, rgba(20,14,10,.68) 100%);
  }
  .actu-hero-content{
    position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:6px; padding:16px;
    text-align:center;
  }
  .actu-hero-content h1{
    font-family:'Playfair Display', serif; font-weight:800;
    font-size:clamp(22px,3vw,32px); color:#F7F2E8; margin:0;
    text-shadow:0 4px 18px rgba(0,0,0,.55);
  }
  .actu-hero-content p{
    max-width:680px; font-size:13px; line-height:1.5; color:#F0E6D2;
    margin:0; text-shadow:0 2px 10px rgba(0,0,0,.5);
  }
  @media (max-width: 700px){ .actu-hero{ height:95px; } }

  .actu-toolbar {'''

if '.actu-hero{' in contenu:
    pass
elif ANCIEN_CSS not in contenu:
    erreurs.append("ancre CSS introuvable")
else:
    contenu = contenu.replace(ANCIEN_CSS, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) HTML : bandeau juste apres l'ouverture de la section
# ------------------------------------------------------------------
ANCIEN_HTML = '''{% block content %}
<section class="container page-section">
'''

NOUVEAU_HTML = '''{% block content %}
<div class="actu-hero">
  <img src="{% static 'foncier/img/cartotheque-hero.jpg' %}" alt="Keur Massar Nord" class="actu-hero-img">
  <div class="actu-hero-overlay"></div>
  <div class="actu-hero-content">
    <h1>Actualit\u00e9s</h1>
    <p>Les derni\u00e8res nouvelles de la commune de Keur Massar Nord.</p>
  </div>
</div>

<section class="container page-section">
'''

if 'class="actu-hero"' in contenu:
    pass
elif ANCIEN_HTML not in contenu:
    erreurs.append("ancre HTML content/section introuvable")
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