# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. HTML : reorganisation + icones + Gestion deplace a droite
# ============================================================
ancien_html = '''    <div class="nav-center">
      <ul id="navMenu">
        <li><a href="{% url 'home' %}">Accueil</a></li>
        <li><a href="{% url 'actualites' %}">Actualit&eacute;s</a></li>
        <li><a href="{% url 'fiscalite' %}">Fiscalit&eacute;</a></li>
        <li><a href="{% url 'contact' %}">Contact</a></li>
        <li><a href="{% url 'galerie' %}">Galerie</a></li>
        <li><a href="{% url 'cartotheque' %}">Cartoth&egrave;que</a></li>
        <li><a href="{% url 'dashboard_home' %}">Gestion</a></li>
      </ul>
    </div>

    <div class="nav-right">
      <img src="{% static 'foncier/img/logo-uidt.png' %}" alt="UIDT" class="nav-logo-uidt">
    </div>'''

nouveau_html = '''    <div class="nav-center">
      <ul id="navMenu">
        <li><a href="{% url 'home' %}"><i class="fa-solid fa-house"></i> Accueil</a></li>
        <li><a href="{% url 'actualites' %}"><i class="fa-solid fa-newspaper"></i> Actualit&eacute;s</a></li>
        <li><a href="{% url 'foncier_info' %}"><i class="fa-solid fa-landmark-dome"></i> Foncier</a></li>
        <li><a href="{% url 'fiscalite' %}"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a></li>
        <li><a href="{% url 'cartotheque' %}"><i class="fa-solid fa-map-location-dot"></i> Cartoth&egrave;que</a></li>
        <li><a href="{% url 'galerie' %}"><i class="fa-solid fa-images"></i> Galerie</a></li>
        <li><a href="{% url 'contact' %}"><i class="fa-solid fa-envelope"></i> Contact</a></li>
      </ul>
    </div>

    <div class="nav-right">
      <a href="{% url 'dashboard_home' %}" class="nav-gestion-link">
        <i class="fa-solid fa-right-to-bracket"></i> Gestion
      </a>
      <img src="{% static 'foncier/img/logo-uidt.png' %}" alt="UIDT" class="nav-logo-uidt">
    </div>'''

if 'class="nav-gestion-link"' in contenu:
    resultats.append("HTML navbar : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML navbar : OK (reorganise, icones ajoutees, Gestion deplace)")
else:
    resultats.append("HTML navbar : ERREUR bloc introuvable tel quel")

# ============================================================
# 2. CSS : icones alignees + style du lien Gestion + espacement nav-right
# ============================================================
ancien_css = '''#navMenu li a{
  display:block; padding:10px 16px; border-radius:999px; font-weight:600; font-size:14px;
  color:var(--ink,#2b1f17); text-decoration:none; transition:background .2s ease, color .2s ease;
}'''

nouveau_css = '''#navMenu li a{
  display:flex; align-items:center; gap:7px;
  padding:10px 16px; border-radius:999px; font-weight:600; font-size:14px;
  color:var(--ink,#2b1f17); text-decoration:none; transition:background .2s ease, color .2s ease;
}
#navMenu li a i{ font-size:12px; opacity:.75; }

.nav-right{ gap:18px; }
.nav-gestion-link{
  display:inline-flex; align-items:center; gap:8px;
  padding:9px 20px; border-radius:999px; font-weight:700; font-size:13.5px;
  color:#fff; background:var(--gold,#c9982e); text-decoration:none;
  transition:background .2s ease, transform .2s ease;
  white-space:nowrap;
}
.nav-gestion-link:hover{ background:var(--gold-dark,#9c6f1d); color:#fff; transform:translateY(-1px); }
.nav-gestion-link i{ font-size:12px; }'''

if ".nav-gestion-link{" in contenu:
    resultats.append("CSS navbar : IGNORE (deja present)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS navbar : OK (icones + bouton Gestion stylises)")
else:
    resultats.append("CSS navbar : ERREUR bloc introuvable tel quel")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))