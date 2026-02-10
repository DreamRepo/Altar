# -*- mode: python ; coding: utf-8 -*-
"""
Build script for creating the AltarSender executable.

Cross-platform: works on Windows, Linux, and macOS.
Run this with: python build_exe.py
"""

import subprocess
import sys
import os
import platform

# Get customtkinter path for bundling themes
import customtkinter

ctk_path = os.path.dirname(customtkinter.__file__)

# Determine the path separator for --add-data based on platform
# Windows uses ';', Linux/macOS use ':'
path_sep = ";" if platform.system() == "Windows" else ":"

# PyInstaller command
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name=AltarSender",
    "--onefile",
    "--windowed",  # No console window for GUI app
    "--noconfirm",
    # Add customtkinter themes/assets (platform-specific separator)
    f"--add-data={ctk_path}{path_sep}customtkinter",
    # Hidden imports that PyInstaller might miss
    "--hidden-import=customtkinter",
    "--hidden-import=sacred",
    "--hidden-import=sacred.observers",
    "--hidden-import=pymongo",
    "--hidden-import=pandas",
    "--hidden-import=numpy",
    "--hidden-import=openpyxl",
    "--hidden-import=boto3",
    "--hidden-import=botocore",
    "--hidden-import=minio",
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    # Collect all submodules for packages that need it
    "--collect-all=customtkinter",
    "--collect-all=sacred",
    # Entry point
    "app.py"
]

print(f"Building executable for {platform.system()}...")
print(" ".join(cmd))
subprocess.run(cmd, check=True)

# Platform-specific output info
if platform.system() == "Windows":
    exe_name = "AltarSender.exe"
elif platform.system() == "Darwin":
    exe_name = "AltarSender.app (or AltarSender binary)"
else:
    exe_name = "AltarSender"

print(f"\n[OK] Build complete! Executable is in the 'dist' folder: {exe_name}")

