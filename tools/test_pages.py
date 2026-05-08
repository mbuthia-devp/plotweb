import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so Django can import the project package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Run from project root
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plotweaverweb.settings')
import django
django.setup()
from django.test import Client

client = Client()

paths = ['/', '/explore/', '/signup/', '/login/', '/profile/', '/write/', '/admin/']

results = []
for p in paths:
    try:
        resp = client.get(p)
        status = resp.status_code
        location = resp.get('Location', '')
        results.append((p, status, location))
    except Exception as e:
        results.append((p, 'ERROR', str(e)))

for r in results:
    print(r)
