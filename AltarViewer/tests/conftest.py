"""Test configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path so `import src.*` works
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))