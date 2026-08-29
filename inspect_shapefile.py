import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection

# Inspect the shapefile table structure
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'keur_massar_nord_arret_003_008_014'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    print("Colonnes de la table 'keur_massar_nord_arret_003_008_014':")
    for col in columns:
        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
        print(f"  - {col[0]:20} | Type: {col[1]:20} | {nullable}")

# Sample some data
print("\n\nExemples de données (5 premières lignes):")
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM keur_massar_nord_arret_003_008_014 LIMIT 5;")
    columns = [desc[0] for desc in cursor.description]
    print("  Colonnes:", ", ".join(columns))
    for row in cursor.fetchall():
        print(f"  {row}")
