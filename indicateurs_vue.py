CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_calc = '''    context = {
        "total_parcelles": total_parcelles,
        "total_proprietaires": total_proprietaires,
        "total_taxes": total_taxes,
        "parcelles_en_retard": parcelles_en_retard,
        "top_retardaires": top_retardaires,
        "quartiers": quartiers,'''

nouveau_calc = '''    # --- Indicateurs de transparence (page d'accueil) : chiffres reels,
    # jamais inventes. Si aucun signalement n'existe encore, le taux de
    # resolution est affiche a 0 plutot que de provoquer une erreur.
    from .models import Infrastructure, Signalement
    nb_infrastructures_total = Infrastructure.objects.count()
    nb_signalements_total = Signalement.objects.count()
    nb_signalements_resolus = Signalement.objects.filter(statut='RESOLU').count()
    pct_signalements_resolus = (
        round((nb_signalements_resolus / nb_signalements_total) * 100)
        if nb_signalements_total > 0 else 0
    )

    context = {
        "total_parcelles": total_parcelles,
        "total_proprietaires": total_proprietaires,
        "total_taxes": total_taxes,
        "parcelles_en_retard": parcelles_en_retard,
        "top_retardaires": top_retardaires,
        "quartiers": quartiers,
        "nb_infrastructures_total": nb_infrastructures_total,
        "nb_signalements_resolus": nb_signalements_resolus,
        "pct_signalements_resolus": pct_signalements_resolus,'''

if "nb_infrastructures_total" in contenu:
    resultats.append("Vue : IGNORE (deja present)")
elif ancien_calc in contenu:
    contenu = contenu.replace(ancien_calc, nouveau_calc, 1)
    resultats.append("Vue : OK (indicateurs de transparence calcules)")
else:
    resultats.append("Vue : ERREUR bloc introuvable tel quel")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))