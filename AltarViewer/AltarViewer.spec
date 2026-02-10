# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/DataBase.ico', '.')],
    hiddenimports=[
        'customtkinter',
        'pymongo',
        'src.mongodb',
        'src.omniboard',
        'src.gui',
        'src.prefs',
        # Optional but recommended to ensure bundling when present
        'keyring',
        'dns',  # dnspython for mongodb+srv
        'platformdirs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Exclude Qt bindings we do not use to avoid PyInstaller's multiple-Qt error
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AltarViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/DataBase.ico',
)
