"""
Commande d'import : lit la table brute importée depuis le shapefile
(arrete_kms_008_003_014_final) et crée/actualise les objets Parcelle
correspondants dans le modèle Django.

Traite les lignes par lots (bulk_create / bulk_update) plutôt qu'une
requête par ligne, ce qui est indispensable vu le volume (~40 000 lignes) :
une requête par ligne prendrait un temps très long.

Usage :
    python manage.py import_arrete_parcelles

Options :
    --dry-run          Affiche ce qui serait fait sans rien écrire en base.
    --batch-size 2000   Taille des lots (défaut : 2000).
"""
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from foncier.models import Parcelle

TABLE_SOURCE = "arrete_kms_008_003_014_final"

CHAMPS_A_METTRE_A_JOUR = ["superficie", "reference_arrete", "occupation_sol", "geom"]


def _formater_numero_lot(numero_lot_brut, objectid):
    """Retourne un nicad exploitable, avec un identifiant de secours si vide."""
    if numero_lot_brut is None:
        numero_lot = ""
    elif isinstance(numero_lot_brut, (int, float)) or hasattr(numero_lot_brut, "to_integral_value"):
        try:
            if float(numero_lot_brut) == int(numero_lot_brut):
                numero_lot = str(int(numero_lot_brut))
            else:
                numero_lot = str(numero_lot_brut).strip()
        except (TypeError, ValueError, OverflowError):
            numero_lot = str(numero_lot_brut).strip()
    else:
        numero_lot = str(numero_lot_brut).strip()

    if not numero_lot:
        numero_lot = f"SANS-LOT-{objectid}"
    return numero_lot


def _lire_geometrie(geom_wkb):
    if geom_wkb is None:
        return None
    # IMPORTANT : passer un memoryview, pas des bytes bruts. GEOSGeometry()
    # tente de décoder un objet `bytes` comme du texte (HEX WKB), ce qui
    # échoue sur du binaire WKB brut.
    geom = GEOSGeometry(memoryview(bytes(geom_wkb)))
    if isinstance(geom, Polygon):
        geom = MultiPolygon(geom)
    geom.srid = 4326
    return geom


class Command(BaseCommand):
    help = "Importe les parcelles depuis la table brute du shapefile importé (arrete_kms_008_003_014_final)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="N'écrit rien en base.")
        parser.add_argument("--batch-size", type=int, default=2000, help="Taille des lots (défaut 2000).")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        with connection.cursor() as cursor:
            cursor.execute(
                f'''
                SELECT "Numero_lot", "Superficie", "Arrete", "OCC_SOL", "OBJECTID",
                       ST_AsEWKB(ST_Force2D(geom)) AS geom_wkb
                FROM "{TABLE_SOURCE}"
                '''
            )
            colonnes = [col[0] for col in cursor.description]
            lignes = cursor.fetchall()

        total = len(lignes)
        self.stdout.write(f"{total} lignes trouvées dans {TABLE_SOURCE}.")

        # 1) Construire les données par nicad (dernier gagne en cas de doublon)
        donnees_par_nicad = {}
        for ligne in lignes:
            donnees = dict(zip(colonnes, ligne))
            numero_lot = _formater_numero_lot(donnees.get("Numero_lot"), donnees.get("OBJECTID"))

            try:
                superficie = float(donnees.get("Superficie") or 0)
            except (TypeError, ValueError):
                superficie = 0.0

            arrete_brut = donnees.get("Arrete")
            arrete = "" if arrete_brut is None else str(arrete_brut).strip()

            occ_sol_brut = donnees.get("OCC_SOL")
            occ_sol = "" if occ_sol_brut is None else str(occ_sol_brut).strip()

            geom = _lire_geometrie(donnees.get("geom_wkb"))

            donnees_par_nicad[numero_lot] = {
                "superficie": superficie,
                "reference_arrete": arrete,
                "occupation_sol": occ_sol,
                "geom": geom,
            }

        self.stdout.write(f"{len(donnees_par_nicad)} nicad(s) distinct(s) à traiter.")

        if dry_run:
            apercu = list(donnees_par_nicad.items())[:20]
            for nicad, vals in apercu:
                self.stdout.write(
                    f"[dry-run] {nicad} — superficie={vals['superficie']} — "
                    f"arrete='{vals['reference_arrete']}' — occ_sol='{vals['occupation_sol']}' — "
                    f"geom={'oui' if vals['geom'] else 'absente'}"
                )
            self.stdout.write(self.style.WARNING(
                f"Dry-run terminé (aperçu des 20 premiers sur {len(donnees_par_nicad)}). Rien n'a été écrit en base."
            ))
            return

        # 2) Traiter par lots
        nicads = list(donnees_par_nicad.keys())
        total_crees, total_maj = 0, 0

        for i in range(0, len(nicads), batch_size):
            lot_nicads = nicads[i:i + batch_size]

            with transaction.atomic():
                existantes = {
                    p.nicad: p for p in Parcelle.objects.filter(nicad__in=lot_nicads)
                }

                a_creer = []
                a_mettre_a_jour = []

                for nicad in lot_nicads:
                    vals = donnees_par_nicad[nicad]
                    if nicad in existantes:
                        obj = existantes[nicad]
                        obj.superficie = vals["superficie"]
                        obj.reference_arrete = vals["reference_arrete"]
                        obj.occupation_sol = vals["occupation_sol"]
                        obj.geom = vals["geom"]
                        a_mettre_a_jour.append(obj)
                    else:
                        a_creer.append(Parcelle(nicad=nicad, **vals))

                if a_creer:
                    Parcelle.objects.bulk_create(a_creer, batch_size=batch_size)
                if a_mettre_a_jour:
                    Parcelle.objects.bulk_update(a_mettre_a_jour, CHAMPS_A_METTRE_A_JOUR, batch_size=batch_size)

            total_crees += len(a_creer)
            total_maj += len(a_mettre_a_jour)
            self.stdout.write(f"Lot {i // batch_size + 1} : {len(a_creer)} créée(s), {len(a_mettre_a_jour)} mise(s) à jour.")

        self.stdout.write(self.style.SUCCESS(
            f"Import terminé : {total_crees} parcelle(s) créée(s), {total_maj} mise(s) à jour "
            f"({len(nicads)} nicad(s) distinct(s) traité(s) sur {total} lignes source)."
        ))