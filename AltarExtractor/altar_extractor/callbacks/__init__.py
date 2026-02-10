"""
Callbacks for AltarExtractor.
"""

from .connection import register_connection_callbacks
from .ui import register_ui_callbacks
from .filters import register_filters_callbacks
from .experiments import register_experiments_callbacks
from .metrics import register_metrics_callbacks
from .pygwalker import register_pygwalker

__all__ = [
    "register_connection_callbacks",
    "register_ui_callbacks",
    "register_filters_callbacks",
    "register_experiments_callbacks",
    "register_metrics_callbacks",
    "register_pygwalker",
]

