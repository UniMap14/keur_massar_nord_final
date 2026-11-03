# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_zones5.py', encoding='utf-8').read())"
"""
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name ILIKE '%keur_massar%'
        ORDER BY table_name
    """)
    tables = [r[0] for r in cursor.fetchall()]
    print("Tables trouvees contenant 'keur_massar' :", tables)
    print()

    for t in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{t}"')
            n = cursor.fetchone()[0]
            print(f"  {t} : {n} lignes")
        except Exception as e:
            print(f"  {t} : erreur -> {e}")
    print()

    cursor.execute("SELECT COUNT(*) FROM foncier_zone")
    print("foncier_zone (table Django Zone) :", cursor.fetchone()[0], "lignes")