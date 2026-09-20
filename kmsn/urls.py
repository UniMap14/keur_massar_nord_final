"""
URL configuration for kmsn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for kmsn project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from foncier.views import home_page

urlpatterns = [
    path('', home_page, name='home'),
    path('home/', home_page, name='home_page'),
    path('index.html', home_page, name='index_html'),
    path('admin/', admin.site.urls),
    path('', include('foncier.urls')),
    path("comptes/", include("comptes.urls")),
    path('gestion/', include('foncier.dashboard_urls')),
    path("citoyens/", include("citoyens.urls")),
    path("jeunes/", include("jeunesse.urls")),
]

# Sert les fichiers médias (CV, photos de signalement...) en développement.
# En production, c'est le serveur web (nginx, etc.) qui doit s'en charger.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "KEUR MASSAR NORD — Administration Foncière & Fiscale"
admin.site.site_title = "KEUR MASSAR NORD Admin"
admin.site.index_title = "Tableau de bord administrateur"