from foncier.models import CarteThematique
for c in CarteThematique.objects.order_by('ordre', '-date_ajout'):
    print(f"--- id={c.id} ordre={c.ordre} ---")
    print("TITRE:", c.titre)
    print("EXPLICATION:", c.explication)
    print()