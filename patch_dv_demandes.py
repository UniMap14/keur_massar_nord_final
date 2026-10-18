# -*- coding: utf-8 -*-
"""
Ajoute au tableau de bord deux blocs bases sur des donnees 100% reelles :
1) "dernieres_demandes" : les dernieres DemandeService deposees par les
   citoyens (reference, demandeur, date, statut reel).
2) "parcelle_recente" : la parcelle la plus recemment enregistree en
   base. Parcelle n'a aucun champ date exploitable -> on utilise l'ordre
   naturel de l'identifiant auto-incremente (-pk), qui correspond
   reellement a l'ordre d'insertion en base (ce n'est pas une donnee
   inventee, juste un ordre technique reel).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Nouvelles requetes, juste apres top_retardaires
# ---------------------------------------------------------------------
ANCRE_REQUETES = """    top_retardaires = (
        Parcelle.objects.filter(statut_fiscal="EN_RETARD")
        .select_related("proprietaire", "zone")
        .order_by("-montant_taxe_annuelle")[:3]
    )"""
AJOUT_REQUETES = """    top_retardaires = (
        Parcelle.objects.filter(statut_fiscal="EN_RETARD")
        .select_related("proprietaire", "zone")
        .order_by("-montant_taxe_annuelle")[:3]
    )

    dernieres_demandes = (
        DemandeService.objects.select_related("demandeur", "type_demande")
        .order_by("-date_demande")[:4]
    )

    parcelle_recente = (
        Parcelle.objects.select_related("proprietaire")
        .order_by("-pk")
        .first()
    )"""
if "dernieres_demandes = (" in texte:
    pass
elif ANCRE_REQUETES not in texte:
    erreurs.append("ANCRE_REQUETES introuvable")
else:
    texte = texte.replace(ANCRE_REQUETES, AJOUT_REQUETES, 1)

# ---------------------------------------------------------------------
# 2) Ajout au dictionnaire de contexte
# ---------------------------------------------------------------------
ANCRE_CONTEXT = """        "derniers_paiements": derniers_paiements,
        "top_retardaires": top_retardaires,"""
AJOUT_CONTEXT = """        "derniers_paiements": derniers_paiements,
        "top_retardaires": top_retardaires,
        "dernieres_demandes": dernieres_demandes,
        "parcelle_recente": parcelle_recente,"""
if '"dernieres_demandes": dernieres_demandes,' in texte:
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
    print("OK : dashboard_views.py -- dernieres_demandes + parcelle_recente ajoutes au contexte.")