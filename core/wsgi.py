"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import inspect
import os

if not hasattr(inspect, "markcoroutinefunction"):
    def markcoroutinefunction(func):
        func._is_coroutine = getattr(inspect, "_is_coroutine", None)
        return func
    inspect.markcoroutinefunction = markcoroutinefunction

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
