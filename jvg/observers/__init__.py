"""
jvg/observers/__init__.py — Пакет наблюдателей
"""

from .base import WorldObserver
from .git_observer import GitObserver
from .fake_observer import FakeObserver

__all__ = ['WorldObserver', 'GitObserver', 'FakeObserver']
