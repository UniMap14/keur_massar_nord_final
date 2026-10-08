CHEMIN = "citoyens/templates/citoyens/demandes/demande_detail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  {% if demande.commentaire_agent %}
  <div class="comment-box">
    <strong>Message de l'administration :</strong><br>
    {{ demande.commentaire_agent|linebreaksbr }}
  </div>
  {% endif %}
</div>'''

nouveau = '''  {% if demande.commentaire_agent %}
  <div class="comment-box">
    <strong>Message de l'administration :</strong><br>
    {{ demande.commentaire_agent|linebreaksbr }}
  </div>
  {% endif %}

  {% if demande.type_demande.tarif and demande.type_demande.tarif > 0 %}
    <div class="comment-box" style="margin-top:16px;">
      <strong>Cette démarche est payante : {{ demande.type_demande.tarif|floatformat:0 }} FCFA</strong><br>
      {% if demande.statut_paiement == 'CONFIRME' %}
        <span style="color:var(--ok);">✓ Paiement confirmé.</span>
      {% elif demande.statut_paiement == 'EN_ATTENTE' %}
        <span style="color:#b9740b;">Paiement en attente de validation par un agent.</span>
      {% else %}
        <span style="color:var(--danger);">Paiement non encore effectué.</span><br>
        <a class="attachment-link" href="{% url 'citoyen_demande_payer' demande.pk %}">
          <i class="fa-solid fa-mobile-screen-button"></i> Payer maintenant
        </a>
      {% endif %}
    </div>
  {% endif %}

  {% if demande.statut == 'PRETE' and demande.parcelle and demande.type_demande.categorie == 'CADASTRE' %}
    {% if not demande.type_demande.tarif or demande.type_demande.tarif <= 0 or demande.statut_paiement == 'CONFIRME' %}
      <a class="attachment-link" href="{% url 'extrait_cadastral_pdf' demande.pk %}" style="margin-top:16px;">
        <i class="fa-solid fa-file-pdf"></i> Télécharger l'extrait cadastral
      </a>
    {% endif %}
  {% endif %}
</div>'''

if "Payer maintenant" in contenu:
    print("DEJA FAIT : deja modifie.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : statut de paiement + bouton extrait cadastral ajoutes.")
else:
    print("ERREUR : ancre introuvable.")