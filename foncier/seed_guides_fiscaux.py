# foncier/management/commands/seed_guides_fiscaux.py
from django.core.management.base import BaseCommand
from foncier.models import GuideFiscal


GUIDES = [
    dict(
        code="ir", sigle="IR", titre="Impôt sur le Revenu",
        categorie="IMPOTS_DIRECTS",
        resume="Impôt annuel sur les revenus des personnes physiques, calculé par tranches progressives.",
        qui_est_concerne="Toute personne physique domiciliée fiscalement au Sénégal, ou qui perçoit des revenus de source sénégalaise. Concerne notamment les revenus locatifs, salaires, pensions, bénéfices d'activités commerciales, industrielles ou agricoles.",
        taux_et_calcul="Barème progressif de 0 % à 40 %, appliqué au revenu net imposable après application du quotient familial (nombre de parts selon la situation familiale et le nombre d'enfants à charge).",
        modalites_declaration="Les contribuables au régime réel déclarent leurs revenus avant le 30 avril de l'année suivant la clôture de l'exercice. Les régimes CGU et CGF ont des échéances spécifiques (1er mars et 1er février).",
        sanctions="Amende fiscale de 200 000 FCFA par procès-verbal en cas de non-déclaration, sans exclure une procédure de taxation d'office.",
        references_legales="Loi n°2012-31 du 31/12/2012 portant Code Général des Impôts, modifiée. Article 173 pour le barème.",
        ordre=1,
    ),
    dict(
        code="is", sigle="IS", titre="Impôt sur les Sociétés",
        categorie="IMPOTS_DIRECTS",
        resume="Impôt annuel sur les bénéfices des personnes morales (sociétés).",
        qui_est_concerne="Les sociétés établies au Sénégal réalisant des activités imposables (article 4 du CGI).",
        taux_et_calcul="30 % du bénéfice fiscal (produits imposables moins charges déductibles). En cas d'exercice déficitaire, un impôt minimum forfaitaire de 0,5 % du chiffre d'affaires s'applique, plafonné à 5 000 000 FCFA.",
        modalites_declaration="Déclaration annuelle avant le 30 avril de l'année suivant la clôture de l'exercice fiscal.",
        sanctions="Amende fiscale de 200 000 FCFA constatée par procès-verbal, possibilité de taxation d'office.",
        references_legales="Loi n°2012-31 portant Code Général des Impôts, articles 4, 7 et suivants.",
        ordre=2,
    ),
    dict(
        code="cfpb", sigle="CFPB", titre="Contribution Foncière des Propriétés Bâties",
        categorie="CONTRIBUTIONS_LOCALES",
        resume="Impôt local dû sur les propriétés bâties (maisons, bureaux, usines...).",
        qui_est_concerne="Le propriétaire de l'immeuble au 1er janvier de l'année d'imposition, quel que soit son titre de propriété. En cas d'indivision, les copropriétaires/héritiers sont solidaires pour le paiement.",
        taux_et_calcul="5 % de la valeur locative annuelle de l'immeuble. Un abattement de 1 500 000 FCFA s'applique sur la valeur locative si le propriétaire occupe le bien comme résidence principale — si la valeur locative ne dépasse pas ce montant, la déclaration reste obligatoire mais rien n'est dû.",
        modalites_declaration="À déclarer chaque année auprès du service des impôts territorialement compétent ; toute mutation d'immeuble doit être signalée.",
        sanctions="",
        references_legales="Code Général des Impôts (CGI).",
        ordre=3,
    ),
    dict(
        code="cgf", sigle="CGF", titre="Contribution Globale Foncière",
        categorie="CONTRIBUTIONS_LOCALES",
        resume="Impôt synthétique simplifié pour les particuliers propriétaires bailleurs, représentant plusieurs impôts fonciers.",
        qui_est_concerne="Personnes physiques propriétaires d'immeubles mis en location (ou associées de sociétés civiles immobilières), dont le total des loyers annuels ne dépasse pas 30 millions de FCFA. Le régime est optionnel : le contribuable peut choisir le régime réel à la place.",
        taux_et_calcul="Calculé par tranches sur le revenu locatif brut annuel prévisionnel : 1/12e (1 mois de loyer) jusqu'à 12 000 000 FCFA ; 1,5/12e entre 12 000 001 et 18 000 000 FCFA ; 2/12e au-delà de 18 000 000 FCFA.",
        modalites_declaration="Déclaration avant le 1er février de chaque année, pour les loyers attendus dans l'année. Paiement en trois versements égaux (fin février, avril, juin), ou en un seul versement si le contribuable préfère.",
        sanctions="Toute situation particulière (dépassement du seuil, vacance locative, loyers impayés) doit être signalée à l'administration fiscale avec justificatifs, pour ajustement éventuel de l'impôt.",
        references_legales="Loi n°2018-10 du 30 mars 2018, modifiant le régime instauré en 2013.",
        ordre=4,
    ),
    dict(
        code="cgu", sigle="CGU", titre="Contribution Globale Unique",
        categorie="CONTRIBUTIONS_LOCALES",
        resume="Régime fiscal simplifié regroupant six impôts en un seul, pour les petits commerçants et prestataires individuels.",
        qui_est_concerne="Personnes physiques (entrepreneurs individuels) exerçant une activité commerciale ou de services, avec un chiffre d'affaires annuel ne dépassant pas 50 millions de FCFA. Exclut les professions libérales, les sociétés/GIE, et les activités de location ou gestion immobilière.",
        taux_et_calcul="2 % du chiffre d'affaires TTC pour la vente de biens (plancher 25 000 FCFA), 5 % pour les prestations de services (plancher 30 000 FCFA). Regroupe BIC, impôt minimum fiscal, CEL, TVA, contribution forfaitaire employeur, et licence de débit de boissons.",
        modalites_declaration="Déclaration annuelle avant fin février auprès du centre des services fiscaux compétent. Paiement en une fois ou en trois acomptes (mars et mai).",
        sanctions="",
        references_legales="Code Général des Impôts.",
        ordre=5,
    ),
    dict(
        code="cel", sigle="CEL", titre="Contribution Économique Locale",
        categorie="CONTRIBUTIONS_LOCALES",
        resume="Contribution locale due par les entreprises, composée de deux volets : valeur locative et valeur ajoutée.",
        qui_est_concerne="Toute personne exerçant une activité imposable au 1er janvier de l'année d'imposition (hors établissements financiers décentralisés pour le volet valeur ajoutée).",
        taux_et_calcul="Volet valeur locative (CEL-VL) : 15 % pour les locaux loués ou occupés gratuitement, 20 % pour les locaux/installations inscrits à l'actif du bilan. Volet valeur ajoutée (CEL-VA) : 1 % de la valeur ajoutée dégagée, avec un minimum de 0,15 % du chiffre d'affaires (0,075 % pour certains secteurs réglementés).",
        modalites_declaration="Déclaration au plus tard le 31 janvier pour la CEL-VL ; au plus tard le 30 avril pour la CEL-VA, en deux exemplaires auprès du service fiscal du siège de l'entreprise.",
        sanctions="",
        references_legales="Articles 285, 320-341 du Code Général des Impôts.",
        ordre=6,
    ),
    dict(
        code="nicad", sigle="NICAD", titre="Numéro d'Identification Cadastrale",
        categorie="FONCIER_CADASTRE",
        resume="Identifiant unique et obligatoire de toute parcelle de terrain au Sénégal.",
        qui_est_concerne="Toute parcelle de terrain, immatriculée ou non, quel que soit son statut juridique (domaine national, domaine public, propriété privée...).",
        taux_et_calcul="Le NICAD comporte 16 caractères : la première partie identifie la localisation administrative (région, département, arrondissement, commune) ; la seconde partie précise la section cadastrale et le numéro de la parcelle.",
        modalites_declaration="Le Certificat d'Identification Cadastrale (CIC) est délivré par le Bureau du Cadastre compétent dans les 5 jours ouvrés suivant la demande, sur présentation de l'état de droits réels et de l'extrait de plan. La création peut être initiée par le Bureau du Cadastre (lotissement administratif) ou par un géomètre-expert/notaire. Le CIC délivré est valable 6 mois. La délivrance est gratuite.",
        sanctions="",
        references_legales="Décret n°2012-396 du 27 mars 2012 instituant le NICAD.",
        ordre=7,
    ),
    dict(
        code="titre-foncier", sigle="TF", titre="Titre Foncier",
        categorie="FONCIER_CADASTRE",
        resume="Titre de propriété définitif et inattaquable sur un immeuble bâti ou non bâti.",
        qui_est_concerne="Tout acquéreur souhaitant obtenir un droit de propriété complet et durable sur un bien immobilier.",
        taux_et_calcul="Frais à prévoir chez le notaire : émoluments (honoraires), droits d'enregistrement (5 % du prix de vente ou de la valeur du bien), frais de formalité foncière (1 %), droits de timbre (2 000 FCFA/feuille), TVA sur les émoluments du notaire.",
        modalites_declaration="La procédure passe obligatoirement par un notaire territorialement compétent : réquisition d'un état de droits réels (3 jours, coût entre 500 et 1 500 FCFA), déclaration préalable de transaction (gratuite), établissement de l'acte de vente, puis dépôt du dossier de mutation à la Conservation foncière (délai réglementaire maximum de 30 jours) pour inscription définitive au livre foncier.",
        sanctions="",
        references_legales="Loi n°2011-07 du 30 mars 2011 portant régime de la propriété foncière ; Loi n°2013-04 du 8 juillet 2013 sur la déclaration préalable des transactions immobilières.",
        ordre=8,
    ),
    dict(
        code="quitus-fiscal", sigle="", titre="Quitus Fiscal",
        categorie="DEMARCHES",
        resume="Document attestant qu'un contribuable est à jour de ses obligations fiscales.",
        qui_est_concerne="Toute personne assujettie aux obligations de déclaration et de paiement d'impôts/taxes, notamment pour soumissionner à un marché public ou recevoir un paiement d'un comptable public.",
        taux_et_calcul="La délivrance du quitus fiscal est totalement gratuite.",
        modalites_declaration="Demande écrite adressée au chef du centre des services fiscaux territorialement compétent, accompagnée des pièces justificatives de la situation fiscale (décharges, quittances) et d'un timbre fiscal de 2 000 FCFA.",
        sanctions="",
        references_legales="",
        ordre=9,
    ),
    dict(
        code="declaration-existence", sigle="", titre="Déclaration d'Existence",
        categorie="DEMARCHES",
        resume="Formalité informant l'administration fiscale du démarrage d'une activité ou d'une entreprise.",
        qui_est_concerne="Toute personne physique ou morale qui ouvre un établissement, démarre une exploitation générant un revenu ou un bénéfice imposable (même exonéré), ou obtient un NINEA.",
        taux_et_calcul="La déclaration en elle-même est gratuite.",
        modalites_declaration="À adresser au centre des services fiscaux territorialement compétent, dans un délai de 20 jours à compter de l'ouverture de l'établissement. Pièces requises : document d'identification (CNI, registre de commerce...), NINEA, titre de propriété/jouissance/occupation établissant l'adresse ou le siège social.",
        sanctions="Amende sur procès-verbal, sans exclure une procédure de rappel de droits par taxation d'office en cas de défaut de déclaration.",
        references_legales="Code Général des Impôts.",
        ordre=10,
    ),
]


class Command(BaseCommand):
    help = "Remplit la table GuideFiscal avec le contenu des fiches DGID (IR, IS, CFPB, CGF, CGU, CEL, NICAD, TF, Quitus, Déclaration d'existence)."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for data in GUIDES:
            obj, was_created = GuideFiscal.objects.update_or_create(
                code=data["code"], defaults=data
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"Terminé : {created} guide(s) créé(s), {updated} mis à jour."
        ))