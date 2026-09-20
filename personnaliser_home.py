CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    c = f.read()

def wrap_between(contenu, marqueur_debut, marqueur_fin, condition, description):
    idx_debut = contenu.find(marqueur_debut)
    if idx_debut == -1:
        print(f"IGNORE ({description}) : marqueur de debut introuvable.")
        return contenu
    idx_fin = contenu.find(marqueur_fin, idx_debut)
    if idx_fin == -1:
        print(f"IGNORE ({description}) : marqueur de fin introuvable.")
        return contenu
    avant = contenu[:idx_debut]
    bloc = contenu[idx_debut:idx_fin]
    apres = contenu[idx_fin:]
    if avant.rstrip().endswith("{% if " + condition + " %}"):
        print(f"DEJA FAIT ({description}).")
        return contenu
    nouveau = avant + "{% if " + condition + " %}\n" + bloc + "{% endif %}\n" + apres
    print(f"OK ({description}).")
    return nouveau

def wrap_exact(contenu, texte_exact, condition, description):
    if texte_exact not in contenu:
        print(f"IGNORE ({description}) : texte exact introuvable.")
        return contenu
    remplace = "{% if " + condition + " %}" + texte_exact + "{% endif %}"
    if remplace in contenu:
        print(f"DEJA FAIT ({description}).")
        return contenu
    contenu = contenu.replace(texte_exact, remplace, 1)
    print(f"OK ({description}).")
    return contenu

c = wrap_between(
    c,
    '  <div class="kpi-card tone-green">',
    '  <div class="kpi-card tone-gold">',
    "peut_fiscal",
    "KPI recouvrement + restes a recouvrer",
)

c = wrap_between(
    c,
    '  <div class="kpi-card tone-gold">\n    <div class="kpi-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>',
    '  <div class="kpi-card tone-blue">',
    "peut_fiscal",
    "KPI contentieux fonciers",
)

c = c.replace(
    '  <div class="kpi-card tone-blue">',
    '  <div class="kpi-card tone-blue">\n'
    '    <div class="kpi-icon"><i class="fa-solid fa-map"></i></div>\n'
    '    <div class="label">Total parcelles cadastrees</div>\n'
    '    <div class="value">{{ nb_parcelles }}</div>\n'
    '  </div>\n\n'
    '  <div class="kpi-card tone-blue">',
    1,
)
c = wrap_between(
    c,
    '  <div class="kpi-card tone-blue">',
    '  <a href="{% url \'dashboard_message_list\' %}" class="kpi-card tone-gold"',
    "peut_technique",
    "KPI proprietaires + total parcelles",
)

c = wrap_between(
    c,
    "<!-- ============ TAUX DE RECOUVREMENT ============ -->",
    "<!-- ============ GRAPHIQUES ============ -->",
    "peut_fiscal",
    "Panel taux de recouvrement",
)

c = wrap_between(
    c,
    "<!-- ============ GRAPHIQUES ============ -->",
    "<!-- ============ ACTIONS RAPIDES ============ -->",
    "peut_fiscal",
    "Panels graphiques",
)

c = wrap_exact(
    c,
    '<a href="{% url \'dashboard_parcelle_create\' %}" class="btn btn-primary btn-sm"><i class="fa-solid fa-plus"></i>Nouvelle parcelle</a>',
    "peut_technique",
    "Bouton nouvelle parcelle",
)

c = wrap_between(
    c,
    '<a href="{% url \'dashboard_parcelle_list\' %}?statut_fiscal=EN_RETARD" class="btn btn-outline btn-sm"><i class="fa-solid fa-clock-rotate-left"></i>Voir les retardataires</a>',
    '  </div>\n</div>\n\n<div class="panel">\n  <div class="panel-header">\n    <h2><i class="fa-solid fa-receipt">',
    "peut_fiscal",
    "Boutons retardataires + messages",
)

c = wrap_between(
    c,
    '<div class="panel">\n  <div class="panel-header">\n    <h2><i class="fa-solid fa-receipt">',
    '<div class="panel">\n  <div class="panel-header">\n    <h2><i class="fa-solid fa-scale-unbalanced">',
    "peut_fiscal",
    "Panel derniers paiements",
)

c = wrap_between(
    c,
    '<div class="panel">\n  <div class="panel-header">\n    <h2><i class="fa-solid fa-scale-unbalanced">',
    "<script>",
    "peut_fiscal",
    "Panel parcelles en retard",
)

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("\n=== Termine. ===")