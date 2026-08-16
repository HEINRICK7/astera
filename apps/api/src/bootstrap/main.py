"""Official API entrypoint.

Composition remains owned by the Runtime bootstrap so the API does not create
a second Kernel, Event Bus, or infrastructure container.
"""
from apps.runtime.src.bootstrap.main import create_app, lifespan

__all__ = ["create_app", "lifespan"]
