# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_lenteur_parcelles.py', encoding='utf-8').read())"

Objectif : comprendre pourquoi la page "Parcelles" de l'admin est lente
(40588 parcelles en base) : absence de pagination ? requetes en trop
(N+1) ? absence d'index ?
"""
import inspect
import time
import foncier.dashboard_views as dv
import foncier.models as m

print("=" * 100)
print("1) Code de dashboard_parcelle_list")
print("=" * 100)
try:
    print(inspect.getsource(dv.dashboard_parcelle_list))
except Exception as e:
    print("Erreur :", e)
print()

print("=" * 100)
print("2) Nombre total de parcelles")
print("=" * 100)
print(m.Parcelle.objects.count())
print()

print("=" * 100)
print("3) Template utilise : pagination presente ?")
print("=" * 100)
import os
for chemin in [
    "foncier/templates/dashboard/parcelle_list.html",
    "foncier/templates/dashboard/generic_list_stub.html",
]:
    print("-" * 100)
    print(chemin, "-> existe :", os.path.exists(chemin))
    if os.path.exists(chemin):
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            contenu = f.read()
        print("contient 'Paginator' ou 'page_obj' ou 'paginator' :",
              "Paginator" in contenu or "page_obj" in contenu or "paginator" in contenu)
        print("longueur fichier :", len(contenu))
    print()

print("=" * 100)
print("4) Mesure reelle du temps d'execution de la requete utilisee par la vue")
print("=" * 100)
t0 = time.time()
qs = m.Parcelle.objects.select_related("proprietaire", "zone").order_by("-pk")
liste = list(qs[:1000])  # on simule un rendu (sans savoir si la vue pagine ou non)
t1 = time.time()
print(f"1000 premieres parcelles (select_related proprietaire+zone) : {t1 - t0:.3f}s")

t0 = time.time()
total = m.Parcelle.objects.count()
t1 = time.time()
print(f"COUNT(*) sur Parcelle ({total} lignes) : {t1 - t0:.3f}s")
print()

print("=" * 100)
print("5) Index existants sur foncier_parcelle (colonnes cles)")
print("=" * 100)
from django.db import connection
with connection.cursor() as cur:
    cur.execute("""
        SELECT indexname, indexdef FROM pg_indexes
        WHERE tablename = 'foncier_parcelle'
        ORDER BY indexname;
    """)
    for nom, definition in cur.fetchall():
        print(nom)
        print("  ", definition)