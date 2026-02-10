"""Main entry point for AltarViewer application."""
# Support both package execution (python -m src.main) and direct script runs (python src/main.py)
try:
    from .gui import MongoApp
except ImportError:
    from gui import MongoApp


def main():
    """Launch the AltarViewer application."""
    app = MongoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
