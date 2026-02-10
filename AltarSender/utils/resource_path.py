"""
Helper for PyInstaller resource paths.

When running as a bundled executable, PyInstaller extracts data files to a
temporary folder referenced by sys._MEIPASS. This helper returns the correct
path whether running from source or from a bundled executable.

Usage:
    from utils.resource_path import resource_path
    
    icon_path = resource_path("assets/icon.ico")
    config_path = resource_path("config/settings.json")
"""

import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Path relative to the application root (e.g., "assets/icon.ico")
    
    Returns:
        Absolute path to the resource file
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled executable
        base_path = sys._MEIPASS
    else:
        # Running from source
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    return os.path.join(base_path, relative_path)





