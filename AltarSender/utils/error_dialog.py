"""
Centralized error display utilities for AltarSender.
Provides both popup dialogs and status label updates.
"""
import customtkinter as ctk
import traceback
from typing import Optional
import sys


class ErrorDialog(ctk.CTkToplevel):
    """A modal dialog to display error messages with full traceback."""
    
    def __init__(self, parent, title: str, message: str, details: str = ""):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Error icon and message
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="❌", font=("Segoe UI", 32)).grid(
            row=0, column=0, padx=(0, 12), pady=0
        )
        ctk.CTkLabel(
            header_frame, 
            text=message, 
            font=("Segoe UI", 14, "bold"),
            wraplength=500,
            justify="left"
        ).grid(row=0, column=1, sticky="w")
        
        # Details (traceback) in scrollable textbox
        if details:
            ctk.CTkLabel(self, text="Error Details:", font=("Segoe UI", 12)).grid(
                row=1, column=0, sticky="w", padx=16, pady=(8, 4)
            )
            details_box = ctk.CTkTextbox(self, font=("Consolas", 11), wrap="word")
            details_box.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 8))
            details_box.insert("1.0", details)
            details_box.configure(state="disabled")
            self.grid_rowconfigure(2, weight=1)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="e", padx=16, pady=(8, 16))
        
        ctk.CTkButton(
            btn_frame, 
            text="Copy to Clipboard", 
            width=140,
            command=lambda: self._copy_to_clipboard(f"{message}\n\n{details}")
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkButton(
            btn_frame, 
            text="Close", 
            width=100,
            command=self.destroy
        ).pack(side="left")
        
        # Focus and bind escape
        self.bind("<Escape>", lambda e: self.destroy())
        self.focus_set()
    
    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()


def show_error(parent, title: str, message: str, exception: Optional[Exception] = None):
    """
    Show an error dialog with optional exception details.
    
    Args:
        parent: The parent window (CTk or CTkToplevel)
        title: Dialog title
        message: Short error message
        exception: Optional exception to include traceback
    """
    details = ""
    if exception:
        details = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    ErrorDialog(parent, title, message, details)


def format_error_message(exception: Exception, prefix: str = "") -> str:
    """
    Format an exception into a user-friendly message string for status labels.
    
    Args:
        exception: The exception to format
        prefix: Optional prefix (e.g., "Error sending: ")
    
    Returns:
        Formatted error string like "❌ Error: TypeError: message"
    """
    return f"❌ {prefix}{exception.__class__.__name__}: {exception}"


def get_traceback(exception: Exception) -> str:
    """Get full traceback string from an exception."""
    return "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))


def log_error(exception: Exception, context: str = ""):
    """
    Log an error to stderr with full traceback.
    Useful for debugging while also showing UI errors.
    """
    if context:
        print(f"[ERROR] {context}", file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
