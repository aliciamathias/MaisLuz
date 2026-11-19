"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import inspect
import os

if not hasattr(inspect, "markcoroutinefunction"):
    def markcoroutinefunction(func):
        func._is_coroutine = getattr(inspect, "_is_coroutine", None)
        return func
    inspect.markcoroutinefunction = markcoroutinefunction

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()
