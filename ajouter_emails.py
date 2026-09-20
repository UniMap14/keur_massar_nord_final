import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.auth.models import User

EMAILS = {
    "citoyen1": "citoyen1@demo.local",
    "citoyen2": "citoyen2@demo.local",
    "citoyen3": "citoyen3@demo.local",
}

for username, email in EMAILS.items():
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"INTROUVABLE : {username}")
        continue
    user.email = email
    user.save(update_fields=["email"])
    print(f"OK : {username} -> email = {email}")