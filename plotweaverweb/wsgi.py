"""
WSGI config for plotweaverweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plotweaverweb.settings')

application = get_wsgi_application()

# If WhiteNoise is installed, wrap the application to serve static files
try:
	from whitenoise import WhiteNoise
	application = WhiteNoise(application, root=str(Path(__file__).resolve().parent.parent / 'staticfiles'))
except Exception:
	pass
