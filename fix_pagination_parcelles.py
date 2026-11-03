# -*- coding: utf-8 -*-
"""
Ajoute la pagination a la page "Parcelles" de l'admin : au lieu de
charger et afficher les 40588 parcelles d'un coup (tres lent), on
n'affiche que 50 parcelles par page, avec une navigation en bas de
tableau qui conserve la recherche/le filtre en cours.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_pagination_parcelles.py
"""
import os

CHEMIN_VIEWS = os.path.join("foncier", "dashboard_views.py")
CHEMIN_HTML = os.path.join("foncier", "templates", "dashboard", "parcelle_list.html")

# ------------------------------------------------------------------
# 1) dashboard_views.py : paginer la liste des parcelles
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_VIEWS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_VIEWS}")

with open(CHEMIN_VIEWS, "r", encoding="utf-8") as f:
    views = f.read()

ANCRE_VIEWS = """    q = request.GET.get("q", "").strip()
    statut = request.GET.get("statut_fiscal", "").strip()

    parcelles = Parcelle.objects.select_related("proprietaire", "zone").order_by("-id")

    if q:
        parcelles = parcelles.filter(
            Q(nicad__icontains=q)
            | Q(proprietaire__nom__icontains=q)
            | Q(proprietaire__prenom__icontains=q)
            | Q(adresse_parcelle__icontains=q)
        )

    if statut:
        parcelles = parcelles.filter(statut_fiscal=statut)

    context = {
        "active_section": "parcelles",
        "nb_parcelles": Parcelle.objects.count(),
        "parcelles": parcelles,
        "q": q,
        "statut": statut,
    }
    return render(request, "dashboard/parcelle_list.html", context)"""

REMPLACEMENT_VIEWS = """    q = request.GET.get("q", "").strip()
    statut = request.GET.get("statut_fiscal", "").strip()

    parcelles = Parcelle.objects.select_related("proprietaire", "zone").order_by("-id")

    if q:
        parcelles = parcelles.filter(
            Q(nicad__icontains=q)
            | Q(proprietaire__nom__icontains=q)
            | Q(proprietaire__prenom__icontains=q)
            | Q(adresse_parcelle__icontains=q)
        )

    if statut:
        parcelles = parcelles.filter(statut_fiscal=statut)

    # Pagination : la liste complete (40000+ parcelles) rendait la page
    # tres lente a charger et a afficher. On ne charge/rend plus que
    # 50 parcelles a la fois.
    from django.core.paginator import Paginator
    paginator = Paginator(parcelles, 50)
    page_courante = paginator.get_page(request.GET.get("page"))

    context = {
        "active_section": "parcelles",
        "nb_parcelles": Parcelle.objects.count(),
        "parcelles": page_courante,
        "page_obj": page_courante,
        "paginator": paginator,
        "q": q,
        "statut": statut,
    }
    return render(request, "dashboard/parcelle_list.html", context)"""

deja_ok_views = "page_courante = paginator.get_page" in views

if not deja_ok_views:
    if ANCRE_VIEWS not in views:
        raise SystemExit(
            "ERREUR : code de dashboard_parcelle_list introuvable tel quel.\n"
            "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
        )
    if views.count(ANCRE_VIEWS) != 1:
        raise SystemExit("ERREUR : ce bloc est trouve plusieurs fois, patch annule par securite.")
    views = views.replace(ANCRE_VIEWS, REMPLACEMENT_VIEWS)

# ------------------------------------------------------------------
# 2) parcelle_list.html : sous-titre + navigation de pagination
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_HTML):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_HTML}")

with open(CHEMIN_HTML, "r", encoding="utf-8") as f:
    html = f.read()

ANCRE_SOUSTITRE = (
    '{% block header_subtitle %}<div class="topbar-subtitle">{{ parcelles.count }} '
    'parcelle(s) enregistrée(s)</div>{% endblock %}'
)
REMPLACEMENT_SOUSTITRE = (
    '{% block header_subtitle %}<div class="topbar-subtitle">{{ nb_parcelles }} '
    'parcelle(s) enregistrée(s)</div>{% endblock %}'
)

ANCRE_FIN_TABLE = """        {% endfor %}
      </tbody>
    </table>
    {% else %}"""
REMPLACEMENT_FIN_TABLE = """        {% endfor %}
      </tbody>
    </table>

    {% if page_obj.paginator.num_pages > 1 %}
    <div class="pagination-bar" style="display:flex; align-items:center; justify-content:center; gap:6px; padding:18px 10px 4px;">
      {% if page_obj.has_previous %}
        <a class="btn btn-outline btn-sm" href="?page={{ page_obj.previous_page_number }}{% if q %}&q={{ q }}{% endif %}{% if statut %}&statut_fiscal={{ statut }}{% endif %}"><i class="fa-solid fa-chevron-left"></i></a>
      {% endif %}
      <span style="font-size:13px; color:var(--ink-quiet,#6f6a5e); padding:0 10px;">
        Page {{ page_obj.number }} / {{ page_obj.paginator.num_pages }}
      </span>
      {% if page_obj.has_next %}
        <a class="btn btn-outline btn-sm" href="?page={{ page_obj.next_page_number }}{% if q %}&q={{ q }}{% endif %}{% if statut %}&statut_fiscal={{ statut }}{% endif %}"><i class="fa-solid fa-chevron-right"></i></a>
      {% endif %}
    </div>
    {% endif %}

    {% else %}"""

deja_ok_html = "pagination-bar" in html

if not deja_ok_html:
    for ancre, nom in [(ANCRE_SOUSTITRE, "SOUSTITRE"), (ANCRE_FIN_TABLE, "FIN_TABLE")]:
        if ancre not in html:
            raise SystemExit(f"ERREUR : ancre {nom} introuvable dans parcelle_list.html. Aucun changement effectue.")
        if html.count(ancre) != 1:
            raise SystemExit(f"ERREUR : ancre {nom} trouvee plusieurs fois, patch annule par securite.")
    html = html.replace(ANCRE_SOUSTITRE, REMPLACEMENT_SOUSTITRE)
    html = html.replace(ANCRE_FIN_TABLE, REMPLACEMENT_FIN_TABLE)

if deja_ok_views and deja_ok_html:
    print("OK : deja applique, rien a faire.")
else:
    with open(CHEMIN_VIEWS, "w", encoding="utf-8") as f:
        f.write(views)
    with open(CHEMIN_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK : pagination ajoutee sur la page Parcelles (50 par page).")
    print("-> Redemarrez le serveur Django puis rechargez /gestion/parcelles/.")