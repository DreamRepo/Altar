"""
AltarExtractor - Sacred MongoDB Experiment Viewer

Main entry point for the application.
"""

import os
from altar_extractor import create_app
from altar_extractor.components.layout import build_layout
from altar_extractor.callbacks.connection import register_connection_callbacks
from altar_extractor.callbacks.ui import register_ui_callbacks
from altar_extractor.callbacks.filters import register_filters_callbacks
from altar_extractor.callbacks.experiments import register_experiments_callbacks
from altar_extractor.callbacks.metrics import register_metrics_callbacks
from altar_extractor.callbacks.pygwalker import register_pygwalker


def create_and_configure_app():
    """Create and configure the Dash application with all callbacks."""
    app, server = create_app()
    app.layout = build_layout()
    
    # Register all callbacks
    register_connection_callbacks(app)
    register_ui_callbacks(app)
    register_filters_callbacks(app)
    register_experiments_callbacks(app)
    register_metrics_callbacks(app)
    register_pygwalker(app, server)
    
    return app, server


# Create app instance for gunicorn
app, server = create_and_configure_app()


if __name__ == "__main__":
    debug_mode = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8050")), debug=debug_mode)