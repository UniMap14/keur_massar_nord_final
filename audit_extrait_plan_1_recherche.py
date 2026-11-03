# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_extrait_plan_1_recherche.py', encoding='utf-8').read())"

Recherche de tout ce qui concerne la generation du document "extrait de
plan" / "extrait du plan cadastral" dans le projet, pour voir le code et
le(s) template(s) PDF existants avant de les adapter au vrai modele.
"""
import os

MOTS_CLES = [
    "extrait_plan", "extrait de plan", "extrait du plan", "ExtraitPlan",
    "PLAN POUR AUTORISATION", "plan_pour_autorisation",
]

racine = "."
trouvailles = []
for dossier, sous_dossiers, fichiers in os.walk(racine):
    sous_dossiers[:] = [d for d in sous_dossiers if d not in (
        "venv", ".git", "__pycache__", "node_modules", "staticfiles", "media"
    )]
    for nomf in fichiers:
        if not nomf.endswith((".py", ".html")):
            continue
        chemin = os.path.join(dossier, nomf)
        try:
            with open(chemin, "r", encoding="utf-8", errors="replace") as f:
                contenu = f.read()
        except Exception:
            continue
        bas = contenu.lower()
        for motif in MOTS_CLES:
            if motif.lower() in bas:
                trouvailles.append(chemin)
                break

trouvailles = sorted(set(trouvailles))
print("=" * 100)
print("Fichiers mentionnant 'extrait de plan' (ou variantes) :")
print("=" * 100)
for t in trouvailles:
    print(t)
print()

print("=" * 100)
print("Types de demande existants (DemandeService / TypeDemande) contenant 'plan'")
print("=" * 100)
import foncier.models as m
for td in m.TypeDemande.objects.all():
    if "plan" in (td.nom or "").lower() or "plan" in (td.code or "").lower():
        print(f"- code={td.code!r} nom={td.nom!r} categorie={getattr(td, 'categorie', None)!r}")
print()

print("=" * 100)
print("Toutes les categories/codes de TypeDemande (pour contexte)")
print("=" * 100)
for td in m.TypeDemande.objects.all():
    print(f"- code={td.code!r} nom={td.nom!r} categorie={getattr(td, 'categorie', None)!r}")