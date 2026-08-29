import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection
from foncier.models import Zone

print("Importation des zones depuis le shapefile avec conversion de SRID...")

imported_count = 0
existing_count = 0

# Use raw SQL with ST_Transform to convert from SRID 32628 to 4326
with connection.cursor() as cursor:
    # First, check count
    cursor.execute("SELECT COUNT(*) FROM keur_massar_nord_arret_003_008_014")
    total = cursor.fetchone()[0]
    print(f"Total zones à importer : {total}\n")
    
    # Insert directly using SQL with ST_Transform
    cursor.execute("""
        INSERT INTO foncier_zone (id_shp, nom, layer, path, geom)
        SELECT id, nom, layer, path, ST_Transform(geom, 4326)
        FROM keur_massar_nord_final
        WHERE id NOT IN (SELECT id_shp FROM foncier_zone)
        ON CONFLICT (id_shp) DO NOTHING
    """)
    imported_count = cursor.rowcount
    
    # Check final count
    cursor.execute("SELECT COUNT(*) FROM foncier_zone")
    total_zones = cursor.fetchone()[0]

print(f"\n✓ Résumé:")
print(f"  - {imported_count} zones importées")
print(f"  - Total zones en BD : {total_zones}")


