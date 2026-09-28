# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

project_root = os.path.dirname(SPEC)
source_root = os.path.join(project_root, "dist")

hiddenimports = []
for package in ("pyautogui", "pynput", "pystray"):
    hiddenimports += collect_submodules(package)

a = Analysis(
    [os.path.join(source_root, "run_autoclicker.py")],
    pathex=[source_root],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AutoClicker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=os.path.join(project_root, "assets", "autoclicker.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="AutoClicker",
)

