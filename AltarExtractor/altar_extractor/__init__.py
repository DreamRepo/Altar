"""
AltarExtractor - Sacred MongoDB Experiment Viewer

A Dash application for exploring Sacred experiment data stored in MongoDB.
"""

import os
import sys
import dash
import dash_bootstrap_components as dbc


def get_assets_path():
    """Get the correct assets folder path, handling PyInstaller bundles."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running as normal Python script
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'assets')


def create_app() -> tuple[dash.Dash, "dash.Dash.server"]:
    """
    Create and return a Dash app instance and its underlying Flask server.
    """
    assets_path = get_assets_path()
    
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder=assets_path,
        external_stylesheets=[
            dbc.themes.LUX,
            dbc.icons.BOOTSTRAP,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
        ],
    )
    return app, app.server

