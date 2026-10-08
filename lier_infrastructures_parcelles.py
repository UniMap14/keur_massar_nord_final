import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection
from foncier.models import Infrastructure

def main():
    avant = Infrastructure.objects.filter(parcelle__isnull=False).count()

    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE foncier_infrastructure AS i
            SET parcelle_id = p.id
            FROM foncier_parcelle AS p
            WHERE i.latitude IS NOT NULL
              AND i.longitude IS NOT NULL
              AND i.parcelle_id IS NULL
              AND p.geom IS NOT NULL
              AND ST_Contains(
                    p.geom,
                    ST_Transform(
                        ST_SetSRID(ST_MakePoint(i.longitude, i.latitude), 4326),
                        ST_SRID(p.geom)
                    )
              )
        ''')

    apres = Infrastructure.objects.filter(parcelle__isnull=False).count()
    total = Infrastructure.objects.count()

    print(f"=== Jointure spatiale terminee ===")
    print(f"{apres - avant} nouvelle(s) infrastructure(s) liee(s) a une parcelle")
    print(f"Total : {apres} / {total} infrastructures liees a une parcelle")


if __name__ == "__main__":
    main()