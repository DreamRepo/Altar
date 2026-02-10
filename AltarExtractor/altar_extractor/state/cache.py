"""
In-memory cache for sharing data between routes.
"""

from typing import Dict, List

# Simple in-memory cache to pass data to the pygwalker page
PYGWALKER_CACHE: Dict[str, List[Dict]] = {}

