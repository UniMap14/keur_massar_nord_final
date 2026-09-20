# ============================================================
# import_parcelles_v3_kmn.py
#
# Importe les parcelles depuis la table "keur_massar_nord kmn" du
# schéma "kmn" (nouvelle version du shapefile, plus complète que les
# précédentes : occupation du sol et arrêté correctement renseignés).
#
# Colonnes source : id, geom, OBJECTID, "NUM PARCEL", "NUMERO LOT",
# TOPONYMIE, syscol, "N section", NICAD, "TITRE FONC", Arrete, OCC_SOL
#
# MAPPING :
#   - NICAD résolu par fiabilité : NICAD > "NUM PARCEL" > "NUMERO LOT" > OBJECTID
#   - OCC_SOL          -> occupation_sol (valeurs réelles : "Terrain Nu", "Bâtis"...)
#   - Arrete           -> reference_arrete
#   - "TITRE FONC"     -> si rempli, type_document = 'TF' ; sinon 'DELIB' par défaut
#   - TOPONYMIE        -> adresse_parcelle
#   - "N section", syscol -> non importés (pas de champ correspondant / redondant avec OCC_SOL)
#   - superficie       -> calculée depuis la géométrie (non fournie par le fichier)
#   - géométrie 3D (MultiPolygonZ) -> aplatie en 2D avant reprojection
#
# Réexécutable sans risque : dédoublonnage via id_shp = OBJECTID
# (avec élimination des OBJECTID dupliqués DANS le fichier source lui-même).
#
# UTILISATION :  python import_parcelles_v3_kmn.py
# ============================================================

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection

SCHEMA = "public"
TABLE = "keur_massar_nord kmn"
TABLE_QUALIFIEE = f'"{SCHEMA}"."{TABLE}"'


def main():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s)",
            [SCHEMA, TABLE],
        )
        if not cursor.fetchone()[0]:
            print(f"ERREUR : la table {TABLE_QUALIFIEE} n'existe pas.")
            return

        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_QUALIFIEE}")
        total_source = cursor.fetchone()[0]
        cursor.execute(f'SELECT COUNT(DISTINCT "OBJECTID") FROM {TABLE_QUALIFIEE}')
        total_distincts = cursor.fetchone()[0]
        n_doublons_source = total_source - total_distincts
        print(f"Table source {TABLE_QUALIFIEE} : {total_source} lignes trouvées.")
        if n_doublons_source:
            print(f"⚠️  {n_doublons_source} OBJECTID dupliqué(s) dans le fichier source : "
                  f"une seule occurrence de chaque sera conservée.")
        print()

        cursor.execute("SELECT COUNT(*) FROM foncier_parcelle")
        total_avant = cursor.fetchone()[0]

        cursor.execute(f"""
            INSERT INTO foncier_parcelle (id_shp, nicad, superficie, reference_arrete,
                                           section_cadastrale, numero_parcelle, numero_lot,
                                           numero_titre_foncier, occupation_sol, type_document, statut_fiscal,
                                           valeur_locative, montant_taxe_annuelle,
                                           adresse_parcelle, proprietaire_id, zone_id, geom)
            SELECT
                id_shp, nicad, superficie, reference_arrete, section_cadastrale,
                numero_parcelle, numero_lot, numero_titre_foncier, occupation_sol, type_document,
                statut_fiscal, valeur_locative, montant_taxe_annuelle, adresse_parcelle,
                proprietaire_id, zone_id, geom
            FROM (
                SELECT DISTINCT ON ("OBJECTID")
                    "OBJECTID"::text AS id_shp,
                    COALESCE(
                        NULLIF(TRIM("NICAD"), ''),
                        NULLIF(TRIM("NUM PARCEL"), ''),
                        NULLIF(TRIM("NUMERO LOT"), ''),
                        "OBJECTID"::text
                    ) AS nicad,
                    ROUND(ST_Area(ST_Transform(ST_Force2D(geom), 4326)::geography)::numeric, 2) AS superficie,
                    COALESCE(NULLIF(TRIM("Arrete"), ''), '') AS reference_arrete,
                    COALESCE(NULLIF(TRIM("N section"), ''), '') AS section_cadastrale,
                    COALESCE(NULLIF(TRIM("NUM PARCEL"), ''), '') AS numero_parcelle,
                    COALESCE(NULLIF(TRIM("NUMERO LOT"), ''), '') AS numero_lot,
                    COALESCE(NULLIF(TRIM("TITRE FONC"), ''), '') AS numero_titre_foncier,
                    COALESCE(NULLIF(TRIM("OCC_SOL"), ''), '') AS occupation_sol,
                    CASE WHEN NULLIF(TRIM("TITRE FONC"), '') IS NOT NULL THEN 'TF' ELSE 'DELIB' END AS type_document,
                    'A_JOUR' AS statut_fiscal,
                    0.00 AS valeur_locative,
                    0.00 AS montant_taxe_annuelle,
                    COALESCE(NULLIF(TRIM("TOPONYMIE"), ''), '') AS adresse_parcelle,
                    NULL::integer AS proprietaire_id,
                    NULL::bigint AS zone_id,
                    ST_Multi(ST_Transform(ST_Force2D(geom), 4326)) AS geom
                FROM {TABLE_QUALIFIEE}
                ORDER BY "OBJECTID"
            ) src
            ON CONFLICT (id_shp) DO UPDATE SET
                nicad = EXCLUDED.nicad,
                superficie = EXCLUDED.superficie,
                reference_arrete = EXCLUDED.reference_arrete,
                section_cadastrale = EXCLUDED.section_cadastrale,
                numero_parcelle = EXCLUDED.numero_parcelle,
                numero_lot = EXCLUDED.numero_lot,
                numero_titre_foncier = EXCLUDED.numero_titre_foncier,
                occupation_sol = EXCLUDED.occupation_sol,
                type_document = EXCLUDED.type_document,
                adresse_parcelle = EXCLUDED.adresse_parcelle,
                geom = EXCLUDED.geom
        """)
        n_traitees = cursor.rowcount

        cursor.execute("SELECT COUNT(*) FROM foncier_parcelle")
        total_final = cursor.fetchone()[0]
        n_importees = total_final - total_avant
        n_mises_a_jour = n_traitees - n_importees

        cursor.execute("SELECT COUNT(*) FROM foncier_parcelle")
        total_final = cursor.fetchone()[0]

        cursor.execute("""
            SELECT occupation_sol, COUNT(*) FROM foncier_parcelle
            GROUP BY occupation_sol ORDER BY COUNT(*) DESC
        """)
        repartition_occ_sol = cursor.fetchall()

    print("=== Résumé ===")
    print(f"  Nouvelles parcelles insérées : {n_importees}")
    print(f"  Parcelles existantes mises à jour (valeurs corrigées) : {n_mises_a_jour}")
    print(f"  Total en base après import      : {total_final}")
    print()
    print("  (statut fiscal, montants, propriétaire et zone déjà assignés")
    print("   manuellement n'ont PAS été écrasés par cette mise à jour.)")
    print()
    print("Répartition occupation du sol :")
    for valeur, n in repartition_occ_sol:
        print(f"  {valeur or '(vide)'}: {n}")
    print()
    print("⚠️  Rappel :")
    print("  - type_document='TF' déduit automatiquement quand TITRE FONC est rempli, sinon 'DELIB' par défaut.")


if __name__ == "__main__":
    main()