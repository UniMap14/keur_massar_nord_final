# ============================================================
# importer_infrastructures.py
#
# Importe le recensement d'infrastructures reel (table PostgreSQL
# "RECENSEMENT_INFRASTRUCTURE_FINAL", deja importee via pgAdmin --
# 133 lignes, 30 colonnes) dans les modeles CategorieInfrastructure /
# Infrastructure deja existants du projet.
#
# Categorisation enrichie : les sous-types autrefois regroupes sous un
# "Autre" generique (Banque, Banque islamique, Cimetiere, Station
# service...) ont maintenant chacun leur propre categorie, avec une
# icone et une couleur distinctes -- pour un affichage plus parlant
# sur le geoportail (chaque type d'infrastructure aura son propre
# "autocollant").
#
# Reexecutable sans risque : chaque infrastructure est identifiee par
# un id_shp unique (INF-<id>) ; un import ne cree jamais de doublon
# si relance.
#
# UTILISATION :
#   python importer_infrastructures.py
# ============================================================

import os
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import connection
from foncier.models import CategorieInfrastructure, Infrastructure

NOM_TABLE = "RECENSEMENT_INFRASTRUCTURE_FINAL"

CATEGORIES = {
    "administration": ("administration", "Administration", "fa-landmark", "#6b4a35"),
    "autre":          ("autre", "Autre", "fa-circle-question", "#766c5d"),
    "commerce":       ("commerce", "Commerce", "fa-store", "#c9982e"),
    "education":      ("education", "Éducation", "fa-graduation-cap", "#3468a8"),
    "energie":        ("energie", "Énergie", "fa-bolt", "#b9740b"),
    "environnement":  ("environnement", "Environnement", "fa-leaf", "#2f7a4f"),
    "religion":       ("religion", "Religion", "fa-mosque", "#8a6d3b"),
    "sante":          ("sante", "Santé", "fa-heart-pulse", "#b23b2e"),
    "securite":       ("securite", "Sécurité", "fa-shield-halved", "#3c2a20"),
    "socio-communautaire": ("socio_communautaire", "Socio-communautaire", "fa-people-group", "#6b4a35"),
    "sport et loisirs": ("sport_loisirs", "Sport et loisirs", "fa-futbol", "#2f7a4f"),
    "transport":      ("transport", "Transport", "fa-bus", "#3468a8"),
}

DETAILS_AUTRE = {
    "banque":            ("banque", "Banque", "fa-building-columns", "#1e5f8a"),
    "banque islamique":  ("banque", "Banque", "fa-building-columns", "#1e5f8a"),
    "cimetiere":         ("cimetiere", "Cimetière", "fa-cross", "#5c5c5c"),
    "station service":   ("station_service", "Station-service", "fa-gas-pump", "#b9740b"),
    "veterinaire":       ("veterinaire", "Vétérinaire", "fa-paw", "#8a6d3b"),
    "croix rouge":       ("croix_rouge", "Croix-Rouge", "fa-truck-medical", "#b23b2e"),
    "service d'hygiene": ("hygiene", "Service d'hygiène", "fa-broom", "#2f7a4f"),
}


def sans_accent(texte):
    remplacements = str.maketrans("éèêëàâäîïôöùûüç", "eeeeaaaiioouuuc")
    return texte.lower().translate(remplacements)


def normaliser_categorie(type_brut, sous_type_brut):
    """Retourne (code, label, icone, couleur) pour un Type_infra brut."""
    brut = (type_brut or "").strip()
    if not brut:
        return CATEGORIES["autre"]

    m = re.match(r"^Autre\s*\((.+)\)$", brut, re.IGNORECASE)
    if m:
        detail = sans_accent(m.group(1).strip())
        if detail in ("preciser", ""):
            detail = sans_accent((sous_type_brut or "").strip())
        return DETAILS_AUTRE.get(detail, CATEGORIES["autre"])

    if brut.lower() == "autre":
        return CATEGORIES["autre"]

    base_norm = sans_accent(brut)
    return CATEGORIES.get(base_norm, CATEGORIES["autre"])


def construire_notes(d):
    morceaux = []

    if d.get("Sous_type"):
        morceaux.append(f"Sous-type : {d['Sous_type']}")
    if d.get("Autres_inf"):
        morceaux.append(d["Autres_inf"])
    if d.get("Nom_respon"):
        morceaux.append(f"Responsable : {d['Nom_respon']}")
    if d.get("Nombre_emp"):
        morceaux.append(f"Employés : {int(d['Nombre_emp'])}")
    if d.get("Horaires"):
        morceaux.append(f"Horaires : {d['Horaires']}")
    if d.get("Garde_nuit") and (d["Garde_nuit"] or "").strip().lower() not in ("", "non"):
        morceaux.append(f"Garde de nuit : {d['Garde_nuit']}")
    if d.get("Telephone_"):
        morceaux.append(f"Téléphone : {int(d['Telephone_'])}")
    if d.get("Nombre_tal"):
        morceaux.append(f"Talibés : {int(d['Nombre_tal'])}")
    if d.get("Nombre_sal"):
        morceaux.append(f"Salles de classe : {int(d['Nombre_sal'])}")
    if d.get("Salle_acco") and (d["Salle_acco"] or "").strip().lower() not in ("", "non"):
        morceaux.append(f"Salle d'accouchement : {d['Salle_acco']}")
    if d.get("Salle_hosp") and (d["Salle_hosp"] or "").strip().lower() not in ("", "non"):
        morceaux.append(f"Salle d'hospitalisation : {d['Salle_hosp']}")
    if d.get("Ambulance") and (d["Ambulance"] or "").strip().lower() not in ("", "non"):
        morceaux.append(f"Ambulance : {d['Ambulance']}")
    if d.get("Nombre_amb"):
        morceaux.append(f"Nombre d'ambulances : {int(d['Nombre_amb'])}")
    if d.get("Nombre_lit"):
        morceaux.append(f"Lits : {int(d['Nombre_lit'])}")
    if d.get("Nombre_med"):
        morceaux.append(f"Médecins : {int(d['Nombre_med'])}")
    if d.get("Nombre_per"):
        morceaux.append(f"Personnel : {int(d['Nombre_per'])}")
    if d.get("Nombre_pat"):
        morceaux.append(f"Patients/jour : {int(d['Nombre_pat'])}")
    if d.get("Vaccinatio") and (d["Vaccinatio"] or "").strip().lower() not in ("", "non"):
        morceaux.append(f"Vaccination : {d['Vaccinatio']}")
    if d.get("Consultati") and (d["Consultati"] or "").strip().lower() not in ("", "non"):
        morceaux.append(f"Consultations : {d['Consultati']}")
    if d.get("Services_d"):
        morceaux.append(f"Services : {d['Services_d']}")
    if d.get("Nombre_lig"):
        morceaux.append(f"Lignes : {int(d['Nombre_lig'])}")

    return "\n".join(morceaux)


def main():
    with connection.cursor() as cursor:
        cursor.execute(f'''
            SELECT
                id, "Type_infra", "Sous_type", "Nom", "Nom_infras", "Autres_inf",
                "Nom_respon", "Nombre_emp", "Horaires", "Garde_nuit", "Telephone_",
                "Nombre_tal", "Nombre_sal", "Salle_acco", "Salle_hosp", "Ambulance",
                "Nombre_amb", "Nombre_lit", "Nombre_med", "Nombre_per", "Nombre_pat",
                "Vaccinatio", "Consultati", "Services_d", "Nombre_lig", "Date",
                ST_Y(ST_Transform(geom, 4326)) AS latitude,
                ST_X(ST_Transform(geom, 4326)) AS longitude
            FROM "{NOM_TABLE}"
            ORDER BY id
        ''')
        colonnes = [c[0] for c in cursor.description]
        lignes = [dict(zip(colonnes, row)) for row in cursor.fetchall()]

    print(f"{len(lignes)} ligne(s) trouvee(s) dans la table \"{NOM_TABLE}\".")

    n_crees = 0
    n_deja_present = 0
    n_categories_creees = 0

    for d in lignes:
        id_shp = f"INF-{d['id']}"

        if Infrastructure.objects.filter(id_shp=id_shp).exists():
            n_deja_present += 1
            continue

        nom = (d.get("Nom") or "").strip() or (d.get("Nom_infras") or "").strip()
        if not nom:
            nom = f"{d.get('Sous_type') or d.get('Type_infra') or 'Infrastructure'} — Keur Massar Nord"

        code, label, icone, couleur = normaliser_categorie(d.get("Type_infra"), d.get("Sous_type"))
        categorie, cree = CategorieInfrastructure.objects.get_or_create(
            code=code,
            defaults={"label": label, "icone": icone, "couleur": couleur},
        )
        if cree:
            n_categories_creees += 1

        Infrastructure.objects.create(
            id_shp=id_shp,
            categorie=categorie,
            nom=nom[:200],
            quartier="",
            statut="FONCTIONNEL",
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
            notes=construire_notes(d),
        )
        n_crees += 1

    print(f"=== Import termine ===")
    print(f"{n_crees} infrastructure(s) creee(s)")
    print(f"{n_deja_present} deja presente(s) (ignoree(s))")
    print(f"{n_categories_creees} nouvelle(s) categorie(s) creee(s)")


if __name__ == "__main__":
    main()