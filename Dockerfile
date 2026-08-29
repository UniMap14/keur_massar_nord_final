# ============================================================
# Dockerfile — déploiement en production (Render, ou tout autre
# hébergeur compatible Docker).
#
# Utiliser Docker garantit que GDAL/GEOS (nécessaires à
# django.contrib.gis) sont bien installés sur le serveur, sans avoir
# à les configurer manuellement comme sur Windows avec OSGeo4W.
# ============================================================

FROM python:3.11-slim

# Dépendances système : GDAL/GEOS/PROJ (cartographie), client PostgreSQL,
# et les outils de compilation nécessaires à psycopg2-binary le cas échéant.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Récupère tous les fichiers statiques (CSS/JS/images) au même endroit,
# pour que whitenoise puisse les servir directement.
RUN python manage.py collectstatic --noinput

# Render fournit la variable PORT automatiquement ; 8000 en repli pour
# les autres hébergeurs Docker.
EXPOSE 8000
CMD gunicorn kmsn.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120
