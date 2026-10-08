CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  <script src="{% static 'foncier/js/voice-guide.js' %}" defer></script>
</div>

<script src="{% static 'foncier/js/voice-guide.js' %}" defer></script>'''

nouveau = '''</div>

<script src="{% static 'foncier/js/voice-guide.js' %}" defer></script>'''

if ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : doublon de voice-guide.js supprime.")
elif contenu.count("voice-guide.js") == 1:
    print("IGNORE : un seul chargement deja present.")
else:
    print(f"A VERIFIER MANUELLEMENT : voice-guide.js trouve {contenu.count('voice-guide.js')} fois, structure differente de celle prevue.")