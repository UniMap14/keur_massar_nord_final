# -*- coding: utf-8 -*-
"""
Ajoute au contexte de dashboard_home() de vraies series mensuelles (12
derniers mois) et des variations en % pour 3 nouveaux indicateurs :
Demandes en cours, Infrastructures recensees, Contribuables enregistres.

Aucune donnee n'est inventee : chaque serie vient d'une vraie requete sur
un champ date qui existe reellement sur le modele (verifie via
manage.py shell avant d'ecrire ce script) :
  - DemandeService.date_demande
  - Infrastructure.date_ajout
  - Contribuable.date_creation
Parcelle n'a aucun champ date (import en bloc depuis le shapefile) :
aucune tendance n'est donc ajoutee pour les parcelles, par honnetete.

Idempotent : si le patch est deja applique, le script le signale et ne
touche a rien.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Import : Count (necessaire pour les nouvelles series mensuelles)
# ---------------------------------------------------------------------
ANCRE_IMPORT = "from django.db.models import Sum, Q\n"
AJOUT_IMPORT = "from django.db.models import Sum, Q, Count\n"
if "from django.db.models import Sum, Q, Count" in texte:
    pass
elif ANCRE_IMPORT not in texte:
    erreurs.append("ANCRE_IMPORT introuvable")
else:
    texte = texte.replace(ANCRE_IMPORT, AJOUT_IMPORT, 1)

# ---------------------------------------------------------------------
# 2) Fonctions utilitaires : serie mensuelle generique + variation %
# ---------------------------------------------------------------------
ANCRE_FCFA = '''def _fcfa(valeur):
    if valeur is None:
        valeur = 0
    return f"{valeur:,.0f} FCFA".replace(",", " ")'''
AJOUT_FCFA = '''def _fcfa(valeur):
    if valeur is None:
        valeur = 0
    return f"{valeur:,.0f} FCFA".replace(",", " ")


def _serie_mensuelle(queryset, champ_date, debut_periode):
    """Retourne (labels, valeurs) sur 12 mois a partir d'un queryset et
    d'un champ date/datetime reel du modele, en reprenant le meme
    decoupage mensuel que le graphique des paiements."""
    annote = (
        queryset.filter(**{f"{champ_date}__gte": debut_periode})
        .annotate(mois=TruncMonth(champ_date))
        .values("mois")
        .annotate(total=Count("id"))
        .order_by("mois")
    )
    totaux = {}
    for a in annote:
        mois_valeur = a["mois"]
        if hasattr(mois_valeur, "date"):
            mois_valeur = mois_valeur.date()
        totaux[mois_valeur] = a["total"]

    labels, valeurs = [], []
    mois_cursor = debut_periode
    for _ in range(12):
        labels.append(f"{calendar.month_abbr[mois_cursor.month].capitalize()} {mois_cursor.year}")
        valeurs.append(totaux.get(mois_cursor, 0))
        annee = mois_cursor.year + (1 if mois_cursor.month == 12 else 0)
        mois = 1 if mois_cursor.month == 12 else mois_cursor.month + 1
        mois_cursor = date(annee, mois, 1)
    return labels, valeurs


def _delta_pct(valeurs):
    """Variation en % entre les deux derniers mois d'une serie reelle.
    Retourne None (pas de badge affiche) si le mois precedent est a 0 :
    une division par zero donnerait un pourcentage absurde, on prefere
    ne rien afficher plutot que d'inventer un chiffre."""
    if len(valeurs) < 2:
        return None
    dernier, precedent = valeurs[-1], valeurs[-2]
    if not precedent:
        return None
    return round((dernier - precedent) / precedent * 100, 1)'''
if "_serie_mensuelle" in texte:
    pass
elif ANCRE_FCFA not in texte:
    erreurs.append("ANCRE_FCFA introuvable")
else:
    texte = texte.replace(ANCRE_FCFA, AJOUT_FCFA, 1)

# ---------------------------------------------------------------------
# 3) Calcul des 3 nouvelles series + compteurs, dans dashboard_home()
# ---------------------------------------------------------------------
ANCRE_CALC = '''    labels_taxes = [r["type_taxe__libelle"] for r in repartition_taxes]
    valeurs_taxes = [float(r["total"] or 0) for r in repartition_taxes]

    context = {'''
AJOUT_CALC = '''    labels_taxes = [r["type_taxe__libelle"] for r in repartition_taxes]
    valeurs_taxes = [float(r["total"] or 0) for r in repartition_taxes]

    # --- Nouveaux indicateurs KPI avec tendance reelle sur 12 mois ---
    _labels_demandes, valeurs_demandes = _serie_mensuelle(
        DemandeService.objects.all(), "date_demande", debut_periode
    )
    _labels_infra, valeurs_infra = _serie_mensuelle(
        Infrastructure.objects.all(), "date_ajout", debut_periode
    )
    _labels_contribuables, valeurs_contribuables = _serie_mensuelle(
        Contribuable.objects.all(), "date_creation", debut_periode
    )

    nb_demandes_en_cours = DemandeService.objects.filter(
        statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]
    ).count()
    nb_infrastructures = Infrastructure.objects.count()
    nb_contribuables = Contribuable.objects.count()

    context = {'''
if "nb_demandes_en_cours" in texte:
    pass
elif ANCRE_CALC not in texte:
    erreurs.append("ANCRE_CALC introuvable")
else:
    texte = texte.replace(ANCRE_CALC, AJOUT_CALC, 1)

# ---------------------------------------------------------------------
# 4) Ajout des nouvelles cles dans le dictionnaire context
# ---------------------------------------------------------------------
ANCRE_CONTEXT = '''        "chart_taxes_labels": json.dumps(labels_taxes),
        "chart_taxes_valeurs": json.dumps(valeurs_taxes),
        "chart_taxes_has_data": len(labels_taxes) > 0,
    }
    return render(request, "dashboard/home.html", context)'''
AJOUT_CONTEXT = '''        "chart_taxes_labels": json.dumps(labels_taxes),
        "chart_taxes_valeurs": json.dumps(valeurs_taxes),
        "chart_taxes_has_data": len(labels_taxes) > 0,

        "delta_recouvrement": _delta_pct(valeurs_mois),

        "nb_demandes_en_cours": nb_demandes_en_cours,
        "chart_demandes_valeurs": json.dumps(valeurs_demandes),
        "delta_demandes": _delta_pct(valeurs_demandes),

        "nb_infrastructures": nb_infrastructures,
        "chart_infra_valeurs": json.dumps(valeurs_infra),
        "delta_infra": _delta_pct(valeurs_infra),

        "nb_contribuables": nb_contribuables,
        "chart_contribuables_valeurs": json.dumps(valeurs_contribuables),
        "delta_contribuables": _delta_pct(valeurs_contribuables),
    }
    return render(request, "dashboard/home.html", context)'''
if '"delta_recouvrement"' in texte:
    pass
elif ANCRE_CONTEXT not in texte:
    erreurs.append("ANCRE_CONTEXT introuvable")
else:
    texte = texte.replace(ANCRE_CONTEXT, AJOUT_CONTEXT, 1)

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : foncier/dashboard_views.py mis a jour (nouveaux indicateurs KPI).")