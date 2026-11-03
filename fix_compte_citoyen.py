# -*- coding: utf-8 -*-
"""
Ajoute "Mon compte" dans l'espace citoyen : le total verse et
l'historique des paiements de DEMARCHES (extrait cadastral, etc.).

Volontairement distinct de la fiscalite (taxations/paiements du
contribuable, deja visibles dans "Vue d'ensemble") : ce compte ne suit
que les paiements rattaches a une DemandeService (montant_paye,
statut_paiement, reference_paiement), jamais l'argent du module
fiscal.

Idempotent : si deja applique, ne touche a rien.
"""
import io
import os

RACINE = r"citoyens"

# ------------------------------------------------------------------
# 1. urls.py : nouvelle route
# ------------------------------------------------------------------
chemin_urls = os.path.join(RACINE, "urls.py")
with io.open(chemin_urls, "r", encoding="utf-8") as f:
    contenu = f.read()

if "citoyen_mon_compte" not in contenu:
    ancre = (
        '    path("espace/demarches/<int:pk>/payer/", views.demande_payer_view, name="citoyen_demande_payer"),\n'
        "    # Espace gestion (agents / administration)"
    )
    remplacement = (
        '    path("espace/demarches/<int:pk>/payer/", views.demande_payer_view, name="citoyen_demande_payer"),\n'
        '    path("espace/mon-compte/", views.mon_compte_view, name="citoyen_mon_compte"),\n'
        "    # Espace gestion (agents / administration)"
    )
    if ancre not in contenu:
        raise SystemExit("ERREUR : ancre introuvable dans citoyens/urls.py. Fichier modifie ?")
    contenu = contenu.replace(ancre, remplacement, 1)
    with io.open(chemin_urls, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : route citoyen_mon_compte ajoutee dans citoyens/urls.py")
else:
    print("OK : citoyens/urls.py deja a jour")

# ------------------------------------------------------------------
# 2. views.py : nouvelle vue
# ------------------------------------------------------------------
chemin_views = os.path.join(RACINE, "views.py")
with io.open(chemin_views, "r", encoding="utf-8") as f:
    contenu = f.read()

if "def mon_compte_view" not in contenu:
    ancre = (
        '    return render(request, "citoyens/demandes/demande_payer.html", {\n'
        '        "demande": demande,\n'
        '        "form": form,\n'
        '        "citoyen": citoyen,\n'
        "    })"
    )
    nouvelle_vue = '''


@login_required
def mon_compte_view(request):
    """
    Compte personnel du citoyen pour ses paiements de DEMARCHES
    (extrait cadastral, etc.) : montant total verse + historique.
    Volontairement distinct de la fiscalite (taxations/paiements du
    contribuable, voir espace_personnel_view) — ce sont deux comptes
    differents, l'un ne doit jamais se melanger a l'autre.
    """
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demandes_payantes = (
        DemandeService.objects
        .filter(demandeur=request.user)
        .exclude(montant_paye__isnull=True)
        .select_related("type_demande")
        .order_by("-date_maj")
    )

    total_paye = sum(
        (d.montant_paye for d in demandes_payantes if d.statut_paiement == "CONFIRME"),
        0,
    )
    total_en_attente = sum(
        (d.montant_paye for d in demandes_payantes if d.statut_paiement == "EN_ATTENTE"),
        0,
    )

    return render(request, "citoyens/espace/mon_compte.html", {
        "citoyen": citoyen,
        "active_section": "mon_compte",
        "demandes_payantes": demandes_payantes,
        "total_paye": total_paye,
        "total_en_attente": total_en_attente,
    })'''
    if ancre not in contenu:
        raise SystemExit("ERREUR : ancre introuvable dans citoyens/views.py. Fichier modifie ?")
    contenu = contenu.replace(ancre, ancre + nouvelle_vue, 1)
    with io.open(chemin_views, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : vue mon_compte_view ajoutee dans citoyens/views.py")
else:
    print("OK : citoyens/views.py deja a jour")

# ------------------------------------------------------------------
# 3. Nouveau template citoyens/templates/citoyens/espace/mon_compte.html
# ------------------------------------------------------------------
chemin_template = os.path.join(RACINE, "templates", "citoyens", "espace", "mon_compte.html")
if not os.path.exists(chemin_template):
    contenu_template = '''{% extends "citoyens/base_citoyen.html" %}

{% block page_title %}Mon compte{% endblock %}
{% block header_title %}Mon compte{% endblock %}
{% block header_subtitle %}Paiements de vos démarches (extrait cadastral, etc.) — distinct de votre fiscalité.{% endblock %}

{% block content %}

<div class="card">
  <h2><i class="fa-solid fa-wallet"></i> Solde de mon compte</h2>
  <div style="display:flex; gap:30px; flex-wrap:wrap;">
    <div>
      <div style="font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; margin-bottom:6px;">Total payé et confirmé</div>
      <div style="font-size:28px; font-weight:800; color:var(--ok);">{{ total_paye|floatformat:0 }} FCFA</div>
    </div>
    {% if total_en_attente %}
    <div>
      <div style="font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; margin-bottom:6px;">En attente de validation</div>
      <div style="font-size:28px; font-weight:800; color:#b9740b;">{{ total_en_attente|floatformat:0 }} FCFA</div>
    </div>
    {% endif %}
  </div>
</div>

<div class="card">
  <h2><i class="fa-solid fa-clock-rotate-left"></i> Historique de mes paiements</h2>
  {% if demandes_payantes %}
    <table style="width:100%; border-collapse:collapse; font-size:13.5px;">
      <thead>
        <tr style="text-align:left; border-bottom:2px solid var(--border);">
          <th style="padding:8px 6px;">Démarche</th>
          <th style="padding:8px 6px;">Montant</th>
          <th style="padding:8px 6px;">Référence</th>
          <th style="padding:8px 6px;">Statut</th>
          <th style="padding:8px 6px;">Date</th>
        </tr>
      </thead>
      <tbody>
        {% for d in demandes_payantes %}
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px 6px;">
            <a href="{% url 'citoyen_demande_detail' d.pk %}">{{ d.type_demande.libelle }}</a>
            <div style="font-size:11px; color:var(--text-muted);">{{ d.numero_dossier }}</div>
          </td>
          <td style="padding:8px 6px; font-weight:700;">{{ d.montant_paye|floatformat:0 }} FCFA</td>
          <td style="padding:8px 6px; font-size:12px; color:var(--text-muted);">{{ d.reference_paiement|default:"—" }}</td>
          <td style="padding:8px 6px;">
            {% if d.statut_paiement == 'CONFIRME' %}
              <span style="color:var(--ok); font-weight:700;">Confirmé</span>
            {% elif d.statut_paiement == 'EN_ATTENTE' %}
              <span style="color:#b9740b; font-weight:700;">En attente</span>
            {% else %}
              {{ d.get_statut_paiement_display }}
            {% endif %}
          </td>
          <td style="padding:8px 6px; color:var(--text-muted);">{{ d.date_maj|date:"d/m/Y" }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p style="color:var(--text-muted);">Vous n'avez pas encore effectué de paiement de démarche.</p>
  {% endif %}
</div>

{% endblock %}
'''
    with io.open(chemin_template, "w", encoding="utf-8") as f:
        f.write(contenu_template)
    print("OK : template mon_compte.html cree")
else:
    print("OK : template mon_compte.html deja present")

# ------------------------------------------------------------------
# 4. base_citoyen.html : lien dans le menu
# ------------------------------------------------------------------
chemin_base = os.path.join(RACINE, "templates", "citoyens", "base_citoyen.html")
with io.open(chemin_base, "r", encoding="utf-8") as f:
    contenu = f.read()

if "citoyen_mon_compte" not in contenu:
    ancre = (
        "      <li><a href=\"{% url 'citoyen_modifier_profil' %}\" class=\"csidebar-link "
        "{% if active_section == 'profil' %}active{% endif %}\">\n"
        "        <i class=\"fa-solid fa-user-pen\"></i> Mon profil\n"
        "      </a></li>"
    )
    remplacement = (
        "      <li><a href=\"{% url 'citoyen_mon_compte' %}\" class=\"csidebar-link "
        "{% if active_section == 'mon_compte' %}active{% endif %}\">\n"
        "        <i class=\"fa-solid fa-wallet\"></i> Mon compte\n"
        "      </a></li>\n"
        "      <li><a href=\"{% url 'citoyen_modifier_profil' %}\" class=\"csidebar-link "
        "{% if active_section == 'profil' %}active{% endif %}\">\n"
        "        <i class=\"fa-solid fa-user-pen\"></i> Mon profil\n"
        "      </a></li>"
    )
    if ancre not in contenu:
        raise SystemExit("ERREUR : ancre introuvable dans base_citoyen.html. Fichier modifie ?")
    contenu = contenu.replace(ancre, remplacement, 1)
    with io.open(chemin_base, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : lien 'Mon compte' ajoute dans le menu citoyen")
else:
    print("OK : menu citoyen deja a jour")

print("\nTermine.")