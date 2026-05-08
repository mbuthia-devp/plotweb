import os, sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','plotweaverweb.settings')
import django
django.setup()
from django.urls import resolve, Resolver404

paths=['/','/explore/','/signup/','/login/','/profile/','/write/','/admin/']
for p in paths:
    try:
        match = resolve(p)
        print(p, '->', match.view_name, match.func)
    except Resolver404 as e:
        print(p, '-> 404')
    except Exception as e:
        print(p, '-> ERROR', e)
