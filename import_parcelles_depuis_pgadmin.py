# ============================================================
# import_parcelles_depuis_pgadmin.py
#
# À utiliser APRÈS avoir chargé le shapefile dans PostgreSQL via
# l'outil "PostGIS Shapefile and DBF Loader" (table cible nommée
# "shp_import_parcelles", SRID 32628, noms de colonnes en minuscules
# — voir les instructions données avec ce script).
#
# Copie ensuite les données vers la table Django foncier_parcelle,
# avec :
#   - reprojection 32628 -> 4326 (ST_Transform)
#   - résolution du NICAD par ordre de fiabilité :
#       nicad_mx > numparc_mx > numero_lot > id_unique (toujours rempli)
#   - dédoublonnage via id_shp (ré-exécutable sans risque)
#   - un rapport CSV des 355 candidats de rattachement propriétaire
#     les plus fiables, à vérifier manuellement (jamais assignés
#     automatiquement)
#
# UTILISATION :  python import_parcelles_depuis_pgadmin.py
# ============================================================

import os
import csv

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection

TABLE_BRUTE = "keur_massar_nord_final"
RAPPORT_CSV = "parcelles_candidats_proprietaire_a_verifier.csv"


def main():
    with connection.cursor() as cursor:
        # Vérifie que la table brute existe bien avant d'aller plus loin.
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
            [TABLE_BRUTE],
        )
        if not cursor.fetchone()[0]:
            print(f"ERREUR : la table '{TABLE_BRUTE}' n'existe pas.")
            print("Vérifiez qu'elle a bien été créée par le PostGIS Shapefile Loader,")
            print("et que son nom correspond exactement (voir TABLE_BRUTE en haut du script).")
            return

        cursor.execute(f'SELECT COUNT(*) FROM "{TABLE_BRUTE}"')
        total_source = cursor.fetchone()[0]
        print(f"Table brute '{TABLE_BRUTE}' : {total_source} lignes trouvées.\n")

        # --- Copie principale : Parcelle, dédoublonnée sur id_shp ---
        # Les noms de colonnes ont gardé leur casse d'origine dans la table
        # brute (ID_UNIQUE, NICAD_MX, ...) : ils doivent être entre
        # guillemets doubles en SQL PostgreSQL pour être reconnus tels quels.
        cursor.execute(f"""
            INSERT INTO foncier_parcelle (id_shp, nicad, superficie, reference_arrete,
                                           occupation_sol, type_document, statut_fiscal,
                                           valeur_locative, montant_taxe_annuelle,
                                           adresse_parcelle, proprietaire_id, zone_id, geom)
            SELECT
                "ID_UNIQUE",
                COALESCE(
                    NULLIF(TRIM("NICAD_MX"), ''),
                    NULLIF(TRIM("NUMPARC_MX"), ''),
                    NULLIF(TRIM("Numero_lot"), ''),
                    "ID_UNIQUE"
                ) AS nicad,
                COALESCE("SUP_M2", 0),
                COALESCE(NULLIF(TRIM("Arrete"), ''), ''),
                COALESCE(NULLIF(TRIM("OCC_SOL"), ''), ''),
                'DELIB',
                'A_JOUR',
                0.00,
                0.00,
                '',
                NULL,
                NULL,
                ST_Multi(ST_Transform(geom, 4326))
            FROM "{TABLE_BRUTE}" src
            WHERE "ID_UNIQUE" NOT IN (
                SELECT id_shp FROM foncier_parcelle WHERE id_shp IS NOT NULL
            )
        """)
        n_importees = cursor.rowcount

        cursor.execute("SELECT COUNT(*) FROM foncier_parcelle")
        total_final = cursor.fetchone()[0]

        # --- Rapport des candidats de rattachement propriétaire fiables ---
        cursor.execute(f"""
            SELECT "ID_UNIQUE", "NICAD_MX", "TITULAIRE", "CODESEC_MX", "LOTISSE_MX"
            FROM "{TABLE_BRUTE}"
            WHERE "NIVEAU_CF" = 'CANDIDAT_UNIQUE_FORT'
        """)
        candidats = cursor.fetchall()

    if candidats:
        with open(RAPPORT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["id_shp", "nicad_matrice", "titulaire_matrice", "code_section", "lotissement"])
            writer.writerows(candidats)

    print("=== Résumé ===")
    print(f"  Parcelles importées cette fois : {n_importees}")
    print(f"  Total en base après import      : {total_final}")
    if candidats:
        print(f"  Candidats propriétaire à vérifier : {len(candidats)}")
        print(f"  -> voir le fichier {RAPPORT_CSV}")
    print()
    print("Pensez à supprimer la table brute une fois l'import vérifié :")
    print(f'  DROP TABLE "{TABLE_BRUTE}";')


if __name__ == "__main__":
    main()
