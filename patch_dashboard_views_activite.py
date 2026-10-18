# -*- coding: utf-8 -*-
"""
Phase 3 (backend) : ajoute au contexte de dashboard_home() un vrai fil
d'activite recente (paiements, demandes, signalements, messages,
infrastructures -- tries par date reelle, rien d'invente) et les
statistiques agregees de la mini-carte de la commune (superficie totale,
nombre de zones, parcelles actives).

Tous les champs utilises (date_paiement, numero_dossier, date_demande,
titre, date_signalement, sujet, date_envoi, nom, date_ajout, superficie,
parcelle_active) sont des champs reels, deja utilises ailleurs dans ce
meme fichier -- aucun nom de champ devine.

Pre-requis : patch_dashboard_views_kpis.py doit deja etre applique
(ce script s'ancre juste apres son bloc).

Idempotent.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Calcul du fil d'activite + stats mini-carte, juste avant context={}
# ---------------------------------------------------------------------
ANCRE_CALC = """    nb_infrastructures = Infrastructure.objects.count()
    nb_contribuables = Contribuable.objects.count()

    context = {"""
AJOUT_CALC = '''    nb_infrastructures = Infrastructure.objects.count()
    nb_contribuables = Contribuable.objects.count()

    # --- Fil d'activite recente (evenements reels, tries par date) ---
    evenements = []

    for p in Paiement.objects.select_related("taxation__contribuable").order_by("-date_paiement")[:5]:
        evenements.append({
            "date": p.date_paiement,
            "titre": f"Paiement recu ({_fcfa(p.montant)})",
            "icone": "fa-credit-card",
            "tone": "green",
        })

    for d in DemandeService.objects.order_by("-date_demande")[:5]:
        evenements.append({
            "date": d.date_demande,
            "titre": f"Nouvelle demande {d.numero_dossier}",
            "icone": "fa-folder-open",
            "tone": "gold",
        })

    for s in Signalement.objects.order_by("-date_signalement")[:5]:
        evenements.append({
            "date": s.date_signalement,
            "titre": f"Signalement : {s.titre}",
            "icone": "fa-triangle-exclamation",
            "tone": "red",
        })

    for m in MessageContact.objects.order_by("-date_envoi")[:5]:
        evenements.append({
            "date": m.date_envoi,
            "titre": f"Message : {m.sujet}" if getattr(m, "sujet", None) else "Nouveau message de contact",
            "icone": "fa-envelope",
            "tone": "blue",
        })

    for i in Infrastructure.objects.order_by("-date_ajout")[:5]:
        evenements.append({
            "date": i.date_ajout,
            "titre": f"Infrastructure recensee : {i.nom}",
            "icone": "fa-road-bridge",
            "tone": "purple",
        })

    evenements = [e for e in evenements if e["date"] is not None]
    evenements.sort(key=lambda e: e["date"], reverse=True)
    activite_recente = evenements[:8]

    # --- Stats de la mini-carte de la commune (donnees reelles) ---
    map_superficie_m2 = Parcelle.objects.aggregate(t=Sum("superficie"))["t"] or 0
    map_superficie_km2 = round(float(map_superficie_m2) / 1000000, 1)
    map_nb_zones = Zone.objects.count()
    map_nb_parcelles_actives = Parcelle.objects.filter(parcelle_active=True).count()

    context = {'''
if "activite_recente" in texte:
    pass
elif ANCRE_CALC not in texte:
    erreurs.append("ANCRE_CALC introuvable (le patch precedent patch_dashboard_views_kpis.py est-il applique ?)")
else:
    texte = texte.replace(ANCRE_CALC, AJOUT_CALC, 1)

# ---------------------------------------------------------------------
# 2) Ajout des nouvelles cles dans le dictionnaire context
# ---------------------------------------------------------------------
ANCRE_CONTEXT = """        "nb_contribuables": nb_contribuables,
        "chart_contribuables_valeurs": json.dumps(valeurs_contribuables),
        "delta_contribuables": _delta_pct(valeurs_contribuables),
    }
    return render(request, "dashboard/home.html", context)"""
AJOUT_CONTEXT = """        "nb_contribuables": nb_contribuables,
        "chart_contribuables_valeurs": json.dumps(valeurs_contribuables),
        "delta_contribuables": _delta_pct(valeurs_contribuables),

        "activite_recente": activite_recente,
        "map_superficie_km2": map_superficie_km2,
        "map_nb_zones": map_nb_zones,
        "map_nb_parcelles_actives": map_nb_parcelles_actives,
    }
    return render(request, "dashboard/home.html", context)"""
if '"activite_recente"' in texte:
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
    print("OK : foncier/dashboard_views.py mis a jour (fil d'activite + stats mini-carte).")