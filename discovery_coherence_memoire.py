# -*- coding: utf-8 -*-
# Verification de coherence entre le memoire (PFC) et le systeme reel.
# Lecture seule : ne modifie rien.
import sys
import io

def titre(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)

# ------------------------------------------------------------
titre("A) VERSIONS")
# ------------------------------------------------------------
import django
print("Django version :", django.get_version())
print("Python version :", sys.version.split()[0])

# ------------------------------------------------------------
titre("B) VOLUMETRIE DES TABLES SPATIALES")
# ------------------------------------------------------------
from django.apps import apps

def get_model_souple(noms_app, noms_modele):
    """Essaie plusieurs combinaisons app/modele, retourne le premier trouve."""
    for app in noms_app:
        for modele in noms_modele:
            try:
                return apps.get_model(app, modele)
            except LookupError:
                continue
    return None

Parcelle = get_model_souple(["foncier"], ["Parcelle"])
Infrastructure = get_model_souple(["foncier"], ["Infrastructure"])
QuartierOfficiel = get_model_souple(["foncier"], ["QuartierOfficiel"])
SectionCadastrale = get_model_souple(["foncier"], ["SectionCadastrale"])
LimiteAdministrative = get_model_souple(["foncier"], ["LimiteAdministrative"])

for nom, modele in [
    ("Parcelle", Parcelle),
    ("Infrastructure", Infrastructure),
    ("QuartierOfficiel", QuartierOfficiel),
    ("SectionCadastrale", SectionCadastrale),
    ("LimiteAdministrative", LimiteAdministrative),
]:
    if modele is None:
        print(f"{nom} : MODELE INTROUVABLE")
    else:
        try:
            print(f"{nom} : {modele.objects.count()} enregistrements")
        except Exception as exc:
            print(f"{nom} : ERREUR lors du comptage -> {exc}")

if Infrastructure is not None:
    champs_infra = [f.name for f in Infrastructure._meta.get_fields()]
    print("\nChamps d'Infrastructure :", champs_infra)
    champ_parcelle_infra = None
    for candidat in ("parcelle",):
        if candidat in champs_infra:
            champ_parcelle_infra = candidat
    if champ_parcelle_infra:
        try:
            avec = Infrastructure.objects.filter(**{f"{champ_parcelle_infra}__isnull": False}).count()
            sans = Infrastructure.objects.filter(**{f"{champ_parcelle_infra}__isnull": True}).count()
            print(f"Infrastructures rattachees a une parcelle : {avec}")
            print(f"Infrastructures SANS parcelle : {sans}")
        except Exception as exc:
            print("Erreur lors du comptage rattachement infra/parcelle :", exc)
    else:
        print("Pas de champ 'parcelle' trouve sur Infrastructure (a verifier manuellement).")

# Parcelles avec donnees fiscales (5041 attendu) : on essaie plusieurs pistes
Taxation = get_model_souple(["foncier"], ["Taxation"])
Contribuable = get_model_souple(["foncier"], ["Contribuable"])
if Taxation is not None:
    try:
        champs_taxation = [f.name for f in Taxation._meta.get_fields()]
        champ_parcelle = "parcelle" if "parcelle" in champs_taxation else None
        if champ_parcelle:
            nb = Taxation.objects.values(champ_parcelle).distinct().count()
            print(f"\nNombre de parcelles distinctes ayant au moins une Taxation : {nb}")
        else:
            print("\nTaxation trouve mais pas de champ 'parcelle' direct :", champs_taxation)
    except Exception as exc:
        print("Erreur Taxation :", exc)
else:
    print("\nTaxation : MODELE INTROUVABLE")

if Contribuable is not None:
    try:
        print(f"Contribuable : {Contribuable.objects.count()} enregistrements")
        champs_contrib = [f.name for f in Contribuable._meta.get_fields()]
        print("Champs de Contribuable :", champs_contrib)
    except Exception as exc:
        print("Erreur Contribuable :", exc)
else:
    print("Contribuable : MODELE INTROUVABLE")

if Parcelle is not None:
    champs_parcelle = [f.name for f in Parcelle._meta.get_fields()]
    print("\nChamps de Parcelle :", champs_parcelle)
    # essai statut_fiscal si present
    for candidat in ("statut_fiscal",):
        if candidat in champs_parcelle:
            try:
                from django.db.models import Count
                repartition = Parcelle.objects.values(candidat).annotate(n=Count("id")).order_by("-n")
                print(f"Repartition de Parcelle.{candidat} :", list(repartition))
            except Exception as exc:
                print("Erreur repartition statut_fiscal :", exc)

# ------------------------------------------------------------
titre("C) GROUPES / ROLES")
# ------------------------------------------------------------
from django.contrib.auth.models import Group
print("Groupes Django existants :", list(Group.objects.values_list("name", flat=True)))

# ------------------------------------------------------------
titre("D) MODELES CITES DANS LE MEMOIRE (existence)")
# ------------------------------------------------------------
noms_a_verifier = [
    "Proprietaire", "Propriétaire", "Zone", "TypeTaxe", "Paiement",
    "CategorieInfrastructure", "Citoyen",
    "DemandeImmatriculation", "DemandeMutation", "DemandeMorcellementFusion",
    "DemandeExoneration", "DemandeService", "DeclarationFiscale",
    "RecoursFiscal", "Recours", "Redressement", "PlanPaiement",
    "EcheancePaiement", "Echeance", "Signalement", "ProfilAgent", "JournalAudit",
]
for nom in noms_a_verifier:
    modele = get_model_souple(["foncier", "citoyens"], [nom])
    if modele is not None:
        print(f"{nom:30s} -> TROUVE ({modele._meta.app_label}.{modele.__name__})")
    else:
        print(f"{nom:30s} -> introuvable")

# ------------------------------------------------------------
titre("E) JOURNAL D'AUDIT")
# ------------------------------------------------------------
JournalAudit = get_model_souple(["foncier"], ["JournalAudit"])
if JournalAudit is not None:
    champs_audit = [f.name for f in JournalAudit._meta.get_fields()]
    print("Champs de JournalAudit :", champs_audit)
    print("Nombre d'entrees actuelles :", JournalAudit.objects.count())
else:
    print("JournalAudit : MODELE INTROUVABLE")

# Recherche des signaux pre_save/post_save/post_delete dans le code
import os
def chercher_dans_fichiers(racine, motif, extensions=(".py",)):
    resultats = []
    for dossier, _, fichiers in os.walk(racine):
        if "/migrations" in dossier.replace("\\", "/") or "venv" in dossier:
            continue
        for fichier in fichiers:
            if fichier.endswith(extensions):
                chemin = os.path.join(dossier, fichier)
                try:
                    with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                        contenu = f.read()
                except Exception:
                    continue
                if motif in contenu:
                    resultats.append(chemin)
    return resultats

fichiers_signaux = chercher_dans_fichiers(".", "post_save") + chercher_dans_fichiers(".", "pre_save")
fichiers_signaux = sorted(set(fichiers_signaux))
print("\nFichiers contenant 'pre_save'/'post_save' :", fichiers_signaux)

# ------------------------------------------------------------
titre("F) ENDPOINTS API ATTENDUS")
# ------------------------------------------------------------
endpoints_attendus = [
    "api/parcelles/", "api/parcelles/toutes/", "api/parcelles/admin/",
    "api/zones/", "api/sections/", "api/limites/", "api/parcelles/bounds/",
]
for chemin_urls in ("foncier/urls.py",):
    try:
        with io.open(chemin_urls, "r", encoding="utf-8") as f:
            contenu_urls = f.read()
        for ep in endpoints_attendus:
            present = ep in contenu_urls or ep.rstrip("/") in contenu_urls
            print(f"{ep:30s} -> {'present' if present else 'ABSENT'} dans {chemin_urls}")
    except Exception as exc:
        print(f"Erreur lecture {chemin_urls} :", exc)

# Recherche de ST_Simplify dans le code applicatif
fichiers_simplify = chercher_dans_fichiers(".", "ST_Simplify") + chercher_dans_fichiers(".", "simplify")
print("\nFichiers mentionnant ST_Simplify/simplify :", sorted(set(fichiers_simplify)))

# ------------------------------------------------------------
titre("G) BACKENDS DE PAIEMENT (simulation ou reel ?)")
# ------------------------------------------------------------
chemin_gateway = "foncier/paiement_gateway.py"
try:
    with io.open(chemin_gateway, "r", encoding="utf-8") as f:
        contenu_gateway = f.read()
    import re
    classes_backend = re.findall(r"class (\w*Backend\w*)", contenu_gateway)
    print("Classes de backend trouvees dans paiement_gateway.py :", classes_backend)
    print("Contient 'manuel' / 'demo' / 'simulation' :",
          any(mot in contenu_gateway.lower() for mot in ["manuel", "demo", "simulation"]))
except Exception as exc:
    print("Erreur lecture paiement_gateway.py :", exc)

from django.conf import settings
for cle in ("PAIEMENT_WAVE_API_KEY", "PAIEMENT_ORANGE_MERCHANT_KEY", "PAIEMENT_ORANGE_CLIENT_ID", "PAIEMENT_ORANGE_CLIENT_SECRET"):
    valeur = getattr(settings, cle, None)
    print(f"settings.{cle} configure (non vide) : {bool(valeur)}")

# ------------------------------------------------------------
titre("H) GENERATION PDF (ReportLab)")
# ------------------------------------------------------------
fichiers_reportlab = chercher_dans_fichiers(".", "reportlab")
print("Fichiers important/utilisant reportlab :", sorted(set(fichiers_reportlab)))

mots_cles_pdf = ["quitus", "attestation", "releve", "extrait_cadastral", "recu"]
for mot in mots_cles_pdf:
    fichiers = chercher_dans_fichiers(".", mot)
    print(f"Fichiers mentionnant '{mot}' :", sorted(set(fichiers))[:10])

# ------------------------------------------------------------
titre("I) AUTHENTIFICATION DEUX FACTEURS CITOYEN")
# ------------------------------------------------------------
fichiers_otp = chercher_dans_fichiers(".", "otp") + chercher_dans_fichiers(".", "OTP")
print("Fichiers mentionnant 'otp' :", sorted(set(fichiers_otp)))

# ------------------------------------------------------------
titre("J) SIGNALEMENT CITOYEN")
# ------------------------------------------------------------
Signalement = get_model_souple(["foncier", "citoyens"], ["Signalement"])
if Signalement is not None:
    champs_signal = [f.name for f in Signalement._meta.get_fields()]
    print("Champs de Signalement :", champs_signal)
else:
    print("Signalement : MODELE INTROUVABLE")

# ------------------------------------------------------------
titre("K) SRID DES COUCHES SPATIALES")
# ------------------------------------------------------------
for nom, modele in [("Parcelle", Parcelle), ("Infrastructure", Infrastructure)]:
    if modele is None:
        continue
    for champ in modele._meta.get_fields():
        if hasattr(champ, "srid"):
            print(f"{nom}.{champ.name} -> SRID declare : {champ.srid}, type : {type(champ).__name__}")

print("\nFIN")