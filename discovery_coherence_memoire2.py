# -*- coding: utf-8 -*-
# Suite de la verification de coherence. Lecture seule.
import io
from django.apps import apps

def titre(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)

def get_model_souple(noms_app, noms_modele):
    for app in noms_app:
        for modele in noms_modele:
            try:
                return apps.get_model(app, modele)
            except LookupError:
                continue
    return None

Parcelle = get_model_souple(["foncier"], ["Parcelle"])
Contribuable = get_model_souple(["foncier"], ["Contribuable"])
PlanPaiement = get_model_souple(["foncier"], ["PlanPaiement"])
RecoursFiscal = get_model_souple(["foncier"], ["RecoursFiscal"])

# ------------------------------------------------------------
titre("1) D'OU VIENT LE CHIFFRE 5041 / 5036 ?")
# ------------------------------------------------------------
if Parcelle is not None:
    champs = [f.name for f in Parcelle._meta.get_fields()]
    for champ in ("simulation_fiscale", "montant_taxe_annuelle", "valeur_locative"):
        if champ in champs:
            try:
                if champ == "simulation_fiscale":
                    n = Parcelle.objects.filter(**{champ: True}).count()
                    print(f"Parcelle.objects.filter({champ}=True).count() = {n}")
                else:
                    n = Parcelle.objects.exclude(**{f"{champ}__isnull": True}).count()
                    print(f"Parcelle avec {champ} non-null : {n}")
            except Exception as exc:
                print(f"Erreur sur {champ} :", exc)
    try:
        n_statut = Parcelle.objects.exclude(statut_fiscal__isnull=True).exclude(statut_fiscal="").count()
        print("Parcelle avec statut_fiscal renseigne (non vide) :", n_statut)
    except Exception as exc:
        print("Erreur statut_fiscal :", exc)

if Contribuable is not None:
    print("\nContribuable.objects.count() =", Contribuable.objects.count())
    champs_c = [f.name for f in Contribuable._meta.get_fields()]
    if "taxations" in champs_c:
        try:
            from django.db.models import Count
            n_contrib_sans_taxation = Contribuable.objects.filter(taxations__isnull=True).count()
            print("Contribuables SANS aucune taxation :", n_contrib_sans_taxation)
        except Exception as exc:
            print("Erreur contribuables sans taxation :", exc)

# ------------------------------------------------------------
titre("2) ENTITE PROPRIETAIRE : table separee ou simple champ ?")
# ------------------------------------------------------------
if Parcelle is not None:
    try:
        champ_proprio = Parcelle._meta.get_field("proprietaire")
        print("Type du champ Parcelle.proprietaire :", type(champ_proprio).__name__)
        if hasattr(champ_proprio, "related_model") and champ_proprio.related_model:
            print("  -> pointe vers le modele :", champ_proprio.related_model._meta.app_label, champ_proprio.related_model.__name__)
            print("  -> champs de ce modele :", [f.name for f in champ_proprio.related_model._meta.get_fields()])
        else:
            print("  -> PAS une relation : c'est un champ simple (texte/autre), pas une entite separee.")
    except Exception as exc:
        print("Erreur champ proprietaire sur Parcelle :", exc)

if Contribuable is not None:
    try:
        champ_proprio_c = Contribuable._meta.get_field("proprietaire")
        print("\nType du champ Contribuable.proprietaire :", type(champ_proprio_c).__name__)
        if hasattr(champ_proprio_c, "related_model") and champ_proprio_c.related_model:
            print("  -> pointe vers le modele :", champ_proprio_c.related_model._meta.app_label, champ_proprio_c.related_model.__name__)
        else:
            print("  -> PAS une relation : champ simple.")
    except Exception as exc:
        print("Erreur champ proprietaire sur Contribuable :", exc)

# ------------------------------------------------------------
titre("3) ECHEANCES ET REDRESSEMENT : modelises comment ?")
# ------------------------------------------------------------
if PlanPaiement is not None:
    champs_plan = [f.name for f in PlanPaiement._meta.get_fields()]
    print("Champs de PlanPaiement :", champs_plan)
else:
    print("PlanPaiement : INTROUVABLE")

if RecoursFiscal is not None:
    champs_recours = [f.name for f in RecoursFiscal._meta.get_fields()]
    print("\nChamps de RecoursFiscal :", champs_recours)
else:
    print("RecoursFiscal : INTROUVABLE")

print("\nFIN")