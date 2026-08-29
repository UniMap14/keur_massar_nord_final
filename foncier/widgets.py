# ============================================================
# foncier/widgets.py
#
# Widget de saisie de géométrie 100% custom, basé sur Leaflet.js.
#
# En plus du dessin du polygone, la carte affiche deux couches de
# contexte en lecture seule (récupérées via les API GeoJSON déjà
# existantes dans foncier/views.py) :
#   - les zones/quartiers du shapefile importé (Zone)
#   - les parcelles déjà enregistrées (Parcelle), pour éviter de
#     redessiner par-dessus une parcelle existante
#
# En mode modification, la parcelle en cours d'édition est exclue
# de cette couche de contexte (elle est déjà affichée par le
# polygone modifiable lui-même).
# ============================================================

from django import forms
from django.urls import reverse_lazy


class LeafletPolygonWidget(forms.Textarea):
    """
    Remplace OSMWidget pour les champs PolygonField/GeometryField.
    Utilisation :
        widgets = {"geom": LeafletPolygonWidget()}

    Pour exclure la parcelle en cours d'édition de la couche de
    contexte (mode modification), définir après instanciation :
        form.fields["geom"].widget.exclude_pk = parcelle.pk
    """

    template_name = "dashboard/widgets/leaflet_polygon.html"

    class Media:
        css = {
            "all": (
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                "https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css",
            )
        }
        js = (
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js",
        )

    def __init__(
        self,
        attrs=None,
        default_lon=-17.3100,
        default_lat=14.7900,
        default_zoom=14,
        parcelles_url=None,
        zones_url=None,
    ):
        default_attrs = {"class": "leaflet-polygon-raw"}
        if attrs:
            default_attrs.update(attrs)
        self.default_lon = default_lon
        self.default_lat = default_lat
        self.default_zoom = default_zoom
        # Résolus paresseusement (reverse_lazy) pour ne pas exiger que
        # toutes les URLs du projet soient déjà chargées à l'import.
        self.parcelles_url = parcelles_url or reverse_lazy("api_parcelles")
        self.zones_url = zones_url or reverse_lazy("api_zones")
        # Définie depuis la vue en mode "modifier" (voir dashboard_views.py)
        self.exclude_pk = None
        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget_id = context["widget"]["attrs"].get("id") or f"id_{name}"
        context["widget"]["map_id"] = f"{widget_id}_map"
        context["widget"]["default_lon"] = self.default_lon
        context["widget"]["default_lat"] = self.default_lat
        context["widget"]["default_zoom"] = self.default_zoom
        context["widget"]["parcelles_url"] = str(self.parcelles_url)
        context["widget"]["zones_url"] = str(self.zones_url)
        context["widget"]["exclude_pk"] = self.exclude_pk if self.exclude_pk is not None else "null"
        return context