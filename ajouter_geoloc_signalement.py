CHEMIN = "foncier/templates/foncier/signalement.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. CSS du bouton de geolocalisation ---
MARQUEUR_CSS = ".signal-geoloc-btn"

ancien_css = "  @media (max-width: 900px){ .signal-layout{ grid-template-columns:1fr; } }"

nouveau_css = '''  .signal-geoloc-box{
    background:var(--off-white); border:1px dashed var(--border); border-radius:10px;
    padding:14px 16px; margin-bottom:16px; display:flex; align-items:center; gap:12px; flex-wrap:wrap;
  }
  .signal-geoloc-btn{
    display:inline-flex; align-items:center; gap:8px; background:var(--green-dark); color:#fff;
    border:none; border-radius:999px; padding:9px 18px; font-size:13px; font-weight:600;
    cursor:pointer; transition:background .2s ease;
  }
  .signal-geoloc-btn:hover{ background:var(--green); }
  .signal-geoloc-btn:disabled{ opacity:.6; cursor:wait; }
  .signal-geoloc-status{ font-size:12.5px; color:var(--text-muted); }
  .signal-geoloc-status.ok{ color:#2f7a4f; font-weight:600; }
  .signal-geoloc-status.err{ color:#b23b2e; font-weight:600; }

  @media (max-width: 900px){ .signal-layout{ grid-template-columns:1fr; } }'''

if MARQUEUR_CSS in contenu:
    resultats.append("IGNORE : CSS geoloc deja present.")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("OK : CSS du bouton de geolocalisation ajoute.")
else:
    resultats.append("ERREUR : bloc CSS ancre introuvable.")

# --- 2. Bouton + zone de statut, juste avant le formulaire ---
MARQUEUR_HTML = 'id="signalGeolocBtn"'

ancien_html = '''      <h3 style="font-size:16px; margin-bottom:16px;">Nouveau signalement</h3>
      <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}'''

nouveau_html = '''      <h3 style="font-size:16px; margin-bottom:16px;">Nouveau signalement</h3>

      <div class="signal-geoloc-box">
        <button type="button" class="signal-geoloc-btn" id="signalGeolocBtn">
          <i class="fa-solid fa-location-crosshairs"></i> Localiser ma position
        </button>
        <span class="signal-geoloc-status" id="signalGeolocStatus">
          Facultatif : aide les agents &agrave; localiser pr&eacute;cis&eacute;ment le probl&egrave;me sur la carte.
        </span>
      </div>

      <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}'''

if MARQUEUR_HTML in contenu:
    resultats.append("IGNORE : bouton geoloc deja present.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("OK : bouton 'Localiser ma position' ajoute.")
else:
    resultats.append("ERREUR : bloc HTML ancre introuvable.")

# --- 3. Script de geolocalisation (rempli les champs caches id_latitude / id_longitude) ---
MARQUEUR_JS = "signalGeolocBtn.addEventListener"

script = '''
<script>
document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('signalGeolocBtn');
    var statut = document.getElementById('signalGeolocStatus');
    var champLat = document.getElementById('id_latitude');
    var champLng = document.getElementById('id_longitude');
    if (!btn || !champLat || !champLng) return;

    signalGeolocBtn.addEventListener('click', function () {
        if (!navigator.geolocation) {
            statut.textContent = "La g\\u00e9olocalisation n'est pas disponible sur cet appareil.";
            statut.className = 'signal-geoloc-status err';
            return;
        }
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Localisation en cours\\u2026';

        navigator.geolocation.getCurrentPosition(
            function (position) {
                champLat.value = position.coords.latitude;
                champLng.value = position.coords.longitude;
                statut.textContent = 'Position captur\\u00e9e \\u2713';
                statut.className = 'signal-geoloc-status ok';
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Actualiser ma position';
            },
            function () {
                statut.textContent = "Position non disponible : v\\u00e9rifiez que la localisation est autoris\\u00e9e pour ce site.";
                statut.className = 'signal-geoloc-status err';
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Localiser ma position';
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });
});
</script>
{% endblock %}'''

if MARQUEUR_JS in contenu:
    resultats.append("IGNORE : script geoloc deja present.")
elif contenu.rstrip().endswith('{% endblock %}'):
    contenu = contenu.rstrip()[:-len('{% endblock %}')].rstrip() + script
    resultats.append("OK : script de geolocalisation ajoute.")
else:
    resultats.append("ERREUR : fin de fichier inattendue, endblock introuvable en fin de fichier.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))