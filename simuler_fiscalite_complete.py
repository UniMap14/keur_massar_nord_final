# -*- coding: utf-8 -*-
"""
Simule des donnees de test pour TOUTES les fonctionnalites admin encore
vides ou presque vides : declarations fiscales, recours, immatriculations,
plans de paiement, mutations, morcellement/fusion, signalements, messages
de contact, proprietaires.

Volontairement : rien n'est valide/traite ici (statut initial partout),
pour que l'administration puisse tester elle-meme tout le flux de
traitement (chef/agent) sur des dossiers reels.

Idempotent par seuil : si un modele a deja assez d'enregistrements, on
n'en rajoute pas.
"""
import random
import uuid

from django.contrib.auth.models import User
from citoyens.models import Citoyen
from foncier.models import (
    Parcelle, Taxation, Contribuable, Propriétaire,
    DeclarationFiscale, RecoursFiscal, DemandeImmatriculation,
    PlanPaiement, DemandeMutation, DemandeMorcellementFusion,
    Signalement, MessageContact,
)

random.seed(7)

PRENOMS_H = ['Mamadou','Ibrahima','Moussa','Ousmane','Abdoulaye','Cheikh','Modou','Alioune','Babacar','Amadou','Souleymane','Pape','Oumar','Idrissa','Mor','Malick','Serigne','Bassirou','Lamine','Yankhoba']
PRENOMS_F = ['Fatou','Aissatou','Awa','Ndeye','Khady','Mariama','Aminata','Coumba','Astou','Bineta','Mame','Sokhna','Adama','Rokhaya','Diarra','Fatimata','Dieynaba','Nogaye','Yacine','Maimouna']
NOMS = ['Ndiaye','Diop','Fall','Sow','Diallo','Ba','Gueye','Sarr','Seck','Mbaye','Cisse','Toure','Faye','Niang','Sy','Diagne','Kane','Thiam','Diouf','Sene','Camara','Dieng','Sakho','Wade','Gning','Dabo','Ndoye','Diatta','Coly','Mendy']
OPERATEURS = ['77','78','76','70','75']


def nom_complet():
    if random.random() < 0.5:
        return random.choice(PRENOMS_H), random.choice(NOMS)
    return random.choice(PRENOMS_F), random.choice(NOMS)


def telephone():
    return "{}{}".format(random.choice(OPERATEURS), random.randint(1000000, 9999999))


def cni():
    return str(random.randint(1000000000000, 1999999999999))


# ------------------------------------------------------------------
# 1. Proprietaire (lie a des parcelles qui n'en ont pas)
# ------------------------------------------------------------------
if Propriétaire.objects.count() < 30:
    parcelles_sans_proprio = list(
        Parcelle.objects.filter(proprietaire__isnull=True).order_by('?')[:30]
    )
    crees = 0
    for parcelle in parcelles_sans_proprio:
        prenom, nom = nom_complet()
        p = Propriétaire.objects.create(
            nom=nom, prenom=prenom, ni_cni=cni(),
            telephone=telephone(), adresse="Keur Massar Nord, Dakar",
        )
        parcelle.proprietaire = p
        parcelle.save(update_fields=['proprietaire'])
        crees += 1
    print("Proprietaire crees :", crees)
else:
    print("Proprietaire : deja suffisant, ignore")

# ------------------------------------------------------------------
# 2. DeclarationFiscale (a partir de Taxations existantes)
# ------------------------------------------------------------------
if DeclarationFiscale.objects.count() < 40:
    taxations = list(
        Taxation.objects.select_related('contribuable', 'parcelle', 'type_taxe')
        .order_by('?')[:40]
    )
    crees = 0
    for t in taxations:
        DeclarationFiscale.objects.create(
            contribuable=t.contribuable,
            parcelle=t.parcelle,
            type_taxe=t.type_taxe,
            annee_fiscale=t.annee_fiscale,
            occupation_declaree=random.choice(["Terrain Nu", "Bâti", "Zone de culture"]),
            commentaire_citoyen=random.choice([
                "Je declare l'occupation reelle de ma parcelle.",
                "Changement d'usage depuis l'an dernier.",
                "",
            ]),
        )
        crees += 1
    print("DeclarationFiscale creees :", crees)
else:
    print("DeclarationFiscale : deja suffisant, ignore")

# ------------------------------------------------------------------
# 3. RecoursFiscal (contestation d'une taxation)
# ------------------------------------------------------------------
if RecoursFiscal.objects.count() < 25:
    taxations = list(
        Taxation.objects.select_related('contribuable').order_by('?')[:25]
    )
    motifs = [
        "Le montant reclame ne correspond pas a la superficie reelle de ma parcelle.",
        "J'ai deja regle cette taxe l'an dernier, erreur de reconduction.",
        "Ma parcelle est en zone de culture, pas batie comme indique.",
        "Je conteste le taux applique a mon dossier.",
        "Erreur sur l'identite du contribuable rattache a cette parcelle.",
    ]
    crees = 0
    for t in taxations:
        RecoursFiscal.objects.create(
            taxation=t,
            contribuable=t.contribuable,
            niveau=1,
            motif=random.choice(motifs),
        )
        crees += 1
    print("RecoursFiscal crees :", crees)
else:
    print("RecoursFiscal : deja suffisant, ignore")

# ------------------------------------------------------------------
# 4. DemandeImmatriculation (parcelles jamais rattachees a un contribuable)
# ------------------------------------------------------------------
if DemandeImmatriculation.objects.count() < 30:
    parcelles_sans_taxation = list(
        Parcelle.objects.exclude(
            id__in=Taxation.objects.values_list('parcelle_id', flat=True)
        ).order_by('?')[:30]
    )
    crees = 0
    for parcelle in parcelles_sans_taxation:
        prenom, nom = nom_complet()
        DemandeImmatriculation.objects.create(
            nom=nom, prenom=prenom, ni_cni=cni(), telephone=telephone(),
            email="{}.{}@demo.local".format(prenom.lower(), nom.lower()),
            parcelle=parcelle,
            occupation_declaree=random.choice(["Terrain Nu", "Bâti", "Zone de culture"]),
        )
        crees += 1
    print("DemandeImmatriculation creees :", crees)
else:
    print("DemandeImmatriculation : deja suffisant, ignore")

# ------------------------------------------------------------------
# 5. PlanPaiement (echelonnement d'une taxation) — pas d'echeances
#    generees ici : elles le sont normalement a la validation par
#    l'agent (dashboard_plan_paiement_traiter).
# ------------------------------------------------------------------
if PlanPaiement.objects.count() < 30:
    taxations = list(
        Taxation.objects.select_related('contribuable').order_by('?')[:30]
    )
    motifs = [
        "Je souhaite etaler le paiement sur plusieurs mois.",
        "Difficulte financiere temporaire, demande d'echelonnement.",
        "Montant eleve, paiement en plusieurs fois souhaite.",
    ]
    crees = 0
    for t in taxations:
        PlanPaiement.objects.create(
            taxation=t,
            contribuable=t.contribuable,
            nombre_echeances=random.choice([2, 3, 4]),
            motif=random.choice(motifs),
        )
        crees += 1
    print("PlanPaiement crees :", crees)
else:
    print("PlanPaiement : deja suffisant, ignore")

# ------------------------------------------------------------------
# 6. DemandeMutation (transfert de propriete)
# ------------------------------------------------------------------
if DemandeMutation.objects.count() < 30:
    parcelles = list(Parcelle.objects.order_by('?')[:30])
    crees = 0
    for parcelle in parcelles:
        prenom, nom = nom_complet()
        DemandeMutation.objects.create(
            parcelle=parcelle,
            nouveau_nom=nom, nouveau_prenom=prenom,
            nouveau_cni=cni(), nouveau_telephone=telephone(),
            nouveau_email="{}.{}@demo.local".format(prenom.lower(), nom.lower()),
        )
        crees += 1
    print("DemandeMutation creees :", crees)
else:
    print("DemandeMutation : deja suffisant, ignore")

# ------------------------------------------------------------------
# 7. DemandeMorcellementFusion
# ------------------------------------------------------------------
if DemandeMorcellementFusion.objects.count() < 20:
    citoyens_users = list(User.objects.filter(citoyen__isnull=False).order_by('?')[:20])
    crees = 0
    for user in citoyens_users:
        type_op = random.choice(["MORCELLEMENT", "FUSION"])
        if type_op == "MORCELLEMENT":
            parcelles = list(Parcelle.objects.order_by('?')[:1])
            justification = "Je souhaite diviser cette parcelle entre mes heritiers."
        else:
            parcelles = list(Parcelle.objects.order_by('?')[:random.choice([2, 3])])
            justification = "Je souhaite regrouper ces parcelles contigues en une seule."
        if not parcelles:
            continue
        demande = DemandeMorcellementFusion.objects.create(
            demandeur=user,
            type_operation=type_op,
            justification=justification,
        )
        demande.parcelles_concernees.set(parcelles)
        crees += 1
    print("DemandeMorcellementFusion creees :", crees)
else:
    print("DemandeMorcellementFusion : deja suffisant, ignore")

# ------------------------------------------------------------------
# 8. Signalement (anomalies citoyennes sur la voie publique)
# ------------------------------------------------------------------
if Signalement.objects.count() < 25:
    sujets = [
        ("Lampadaire en panne", "L'eclairage public ne fonctionne plus depuis plusieurs jours."),
        ("Depot d'ordures sauvage", "Des dechets s'accumulent sur ce terrain vague."),
        ("Route degradee", "La chaussee presente de nombreux nids de poule."),
        ("Fuite d'eau sur la voie publique", "Une canalisation fuit depuis ce matin."),
        ("Caniveau bouche", "Les eaux stagnent faute d'ecoulement."),
        ("Panneau de signalisation manquant", "Le panneau a disparu au carrefour."),
        ("Arbre menacant de tomber", "Un arbre penche dangereusement vers la route."),
        ("Insecurite nocturne", "Zone mal eclairee, demande de renforcement."),
    ]
    lieux = [
        "Quartier Keur Massar Nord", "Pres du marche central", "Route de Boune",
        "Cite Djily Mbaye", "Quartier Aïnoumady", "Pres de l'ecole primaire",
        "Avenue principale", "Zone industrielle",
    ]
    crees = 0
    for i in range(25):
        titre, description = random.choice(sujets)
        statut = "RESOLU" if i < 3 else "EN_COURS"
        Signalement.objects.create(
            titre=titre,
            description=description,
            lieu=random.choice(lieux),
            statut=statut,
            latitude=14.78 + random.uniform(-0.03, 0.03),
            longitude=-17.33 + random.uniform(-0.03, 0.03),
            telephone=telephone() if random.random() < 0.6 else "",
        )
        crees += 1
    print("Signalement crees :", crees)
else:
    print("Signalement : deja suffisant, ignore")

# ------------------------------------------------------------------
# 9. MessageContact
# ------------------------------------------------------------------
if MessageContact.objects.count() < 20:
    sujets = [
        "Question sur ma taxation fonciere",
        "Demande d'information sur le NICAD",
        "Probleme de connexion a mon espace citoyen",
        "Reclamation sur un paiement",
        "Demande de rendez-vous avec le service cadastre",
        "Erreur sur mes informations personnelles",
        "Question sur une demande d'exoneration",
        "Félicitations pour le nouveau geoportail",
    ]
    crees = 0
    for i in range(20):
        prenom, nom = nom_complet()
        MessageContact.objects.create(
            nom="{} {}".format(prenom, nom),
            email="{}.{}@demo.local".format(prenom.lower(), nom.lower()),
            telephone=telephone() if random.random() < 0.7 else "",
            sujet=random.choice(sujets),
            message="Bonjour, je vous ecris au sujet de ma demande. Merci de me recontacter des que possible.",
        )
        crees += 1
    print("MessageContact crees :", crees)
else:
    print("MessageContact : deja suffisant, ignore")

print()
print("=== Termine ===")