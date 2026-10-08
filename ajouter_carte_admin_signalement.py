CHEMIN = "foncier/templates/dashboard/signalement_detail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. CSS Leaflet + mini-carte (dans extra_head, avant </style>) ---
MARQUEUR_CSS = "#signalMiniMap"

ancien_css = "    .form-field .errorlist { list-style: none; margin: 6px 0 0; padding: 0; color: #c0392b; font-size: 12px; }\n</style>"

nouveau_css = '''    .form-field .errorlist { list-style: none; margin: 6px 0 0; padding: 0; color: #c0392b; font-size: 12px; }

    #signalMiniMap {
        width: 100%; height: 240px; border-radius: 10px; margin-top: 6px;
        border: 1px solid var(--line, #ece6da);
    }
</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />'''

if MARQUEUR_CSS in contenu:
    resultats.append("IGNORE : CSS mini-carte deja present.")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("OK : CSS + import Leaflet ajoutes.")
else:
    resultats.append("ERREUR : bloc CSS ancre introuvable.")

# --- 2. Remplace le champ "Coordonnees" (texte brut) par la mini-carte ---
MARQUEUR_HTML = 'id="signalMiniMap"'

ancien_html = '''    {% if signalement.latitude and signalement.longitude %}
    <div class="info-field">
      <label><i class="fa-solid fa-map-pin"></i> Coordonnées</label>
      <div class="val" style="font-weight:400;">{{ signalement.latitude }}, {{ signalement.longitude }}</div>
    </div>
    {% endif %}'''

nouveau_html = '''    {% if signalement.latitude and signalement.longitude %}
    <div class="info-field">
      <label><i class="fa-solid fa-map-pin"></i> Localisation transmise par le citoyen</label>
      <div id="signalMiniMap" data-lat="{{ signalement.latitude }}" data-lng="{{ signalement.longitude }}"></div>
      <div class="val" style="font-weight:400; font-size:11.5px; margin-top:6px; color:var(--ink-quiet,#7a7266);">
        {{ signalement.latitude }}, {{ signalement.longitude }}
        &middot; <a href="https://www.google.com/maps?q={{ signalement.latitude }},{{ signalement.longitude }}" target="_blank" rel="noopener">Ouvrir dans Google Maps</a>
      </div>
    </div>
    {% endif %}'''

if MARQUEUR_HTML in contenu:
    resultats.append("IGNORE : mini-carte HTML deja presente.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("OK : mini-carte inseree a la place des coordonnees brutes.")
else:
    resultats.append("ERREUR : bloc HTML des coordonnees introuvable.")

# --- 3. Script Leaflet (ajoute juste avant {% endblock %} final) ---
MARQUEUR_JS = "signalMiniMap"

script = '''
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function () {
    var conteneur = document.getElementById('signalMiniMap');
    if (!conteneur || typeof L === 'undefined') return;

    var lat = parseFloat(conteneur.getAttribute('data-lat'));
    var lng = parseFloat(conteneur.getAttribute('data-lng'));
    if (isNaN(lat) || isNaN(lng)) return;

    var carte = L.map(conteneur).setView([lat, lng], 16);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        subdomains: 'abc',
    }).addTo(carte);
    L.marker([lat, lng]).addTo(carte);
});
</script>
{% endblock %}'''

if 'leaflet@1.9.4/dist/leaflet.js' in contenu:
    resultats.append("IGNORE : script mini-carte deja present.")
elif contenu.rstrip().endswith('{% endblock %}'):
    contenu = contenu.rstrip()[:-len('{% endblock %}')].rstrip() + script
    resultats.append("OK : script de la mini-carte ajoute.")
else:
    resultats.append("ERREUR : fin de fichier inattendue, endblock introuvable en fin de fichier.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))