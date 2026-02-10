import multiprocessing
import sys

# Required for PyInstaller to handle multiprocessing correctly
if __name__ == "__main__":
    multiprocessing.freeze_support()

import customtkinter as ctk
from ui.app_view import AppView

ctk.set_appearance_mode("system")      # "light" | "dark" | "system"
ctk.set_default_color_theme("blue")    # "blue" | "green" | "dark-blue"
ctk.deactivate_automatic_dpi_awareness()  # prevent alpha flicker/opacity when moving between monitors

def main():
    app = AppView()
    app.mainloop()

if __name__ == "__main__":
    main()
