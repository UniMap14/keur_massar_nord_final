import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection

# List all tables
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print("Tables disponibles :")
    for table in tables:
        print(f"  - {table[0]}")

# Check for shapefile-related tables
print("\n\nRecherce de tables contenant 'shap' ou géométrie:")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND (table_name ILIKE '%shap%' OR data_type ILIKE '%geom%')
        ORDER BY table_name, ordinal_position;
    """)
    cols = cursor.fetchall()
    if cols:
        for col in cols:
            print(f"  Table: {col[0]}, Colonne: {col[1]}, Type: {col[2]}")
    else:
        print("  Aucune table shapefile trouvée")

# Show all tables with geometry columns
print("\n\nToutes les colonnes avec géométrie:")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND data_type LIKE '%geometry%'
        ORDER BY table_name;
    """)
    geom_cols = cursor.fetchall()
    if geom_cols:
        for col in geom_cols:
            print(f"  Table: {col[0]}, Colonne: {col[1]}, Type: {col[2]}")
