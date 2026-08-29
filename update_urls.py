from pathlib import Path
p = Path('foncier/urls.py')
txt = p.read_text(encoding='utf-8')
old = "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('', views.carte_geoportail, name='geoportail'),\n    path('api/parcelles/', views.api_parcelles_geojson, name='api_parcelles'),\n]\n"
new = "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('', views.carte_geoportail, name='geoportail'),\n    path('geoportail.html', views.carte_geoportail, name='geoportail_html'),\n    path('fiscalite/', views.fiscalite, name='fiscalite'),\n    path('fiscalite.html', views.fiscalite, name='fiscalite_html'),\n    path('api/parcelles/', views.api_parcelles_geojson, name='api_parcelles'),\n]\n"
if old in txt:
    p.write_text(txt.replace(old, new), encoding='utf-8')
    print('updated urls.py')
else:
    print('block not found')
