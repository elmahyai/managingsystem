"""
WSGI config for workSystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#from whitenoise.django import DjangoWhiteNoise
#from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workSystem.settings')

application = get_wsgi_application()
#application = DjangoWhiteNoise(application)


