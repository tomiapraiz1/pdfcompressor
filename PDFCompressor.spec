# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for PDF Compressor.

Bundles:
  - gswin64c.exe + gsdll64.dll  →  gs_bin/
  - Ghostscript lib files        →  gs_lib/
  - customtkinter theme assets
  - tkinterdnd2 DnD support

Build with:
    uv run pyinstaller PDFCompressor.spec
"""

import glob
import os
import sys
from pathlib import Path


# ── Locate Ghostscript installation ──────────────────────────────────────────

def _find_gs_root() -> Path:
    candidates = glob.glob(r"C:\Program Files\gs\gs*") + \
                 glob.glob(r"C:\Program Files (x86)\gs\gs*")
    if not candidates:
        raise RuntimeError(
            "Ghostscript installation not found under C:\\Program Files\\gs\\. "
            "Run the GitHub Actions workflow or install Ghostscript manually."
        )
    return Path(sorted(candidates)[-1])   # newest version wins


gs_root = _find_gs_root()
gs_bin_dir  = gs_root / "bin"
gs_lib_dir  = gs_root / "lib"


# Binaries: exe + all DLLs from the bin directory
gs_binaries = [
    (str(f), "gs_bin")
    for f in gs_bin_dir.iterdir()
    if f.suffix.lower() in (".exe", ".dll")
]

# Data: every file in the lib directory (PostScript init files, fonts, etc.)
gs_lib_data = [
    (str(f), "gs_lib")
    for f in gs_lib_dir.iterdir()
    if f.is_file()
]


# ── Analysis ─────────────────────────────────────────────────────────────────

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=gs_binaries,
    datas=gs_lib_data,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy stdlib/third-party modules we never use
        "matplotlib", "numpy", "scipy", "pandas",
        "PIL", "Pillow",
        "IPython", "notebook",
        "xmlrpc", "pydoc", "doctest",
        "unittest",
        "email.mime",
        "http.server",
        "multiprocessing",
        "sqlite3",
        "ssl",
        "csv",
        "ftplib",
        "imaplib",
        "poplib",
        "smtplib",
        "telnetlib",
        "nntplib",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # onedir mode
    name="PDFCompressor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                # compress binaries with UPX when available
    upx_exclude=[
        # UPX can corrupt some DLLs; exclude Ghostscript ones to be safe
        "gswin64c.exe",
        "gsdll64.dll",
    ],
    console=False,           # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["gswin64c.exe", "gsdll64.dll"],
    name="PDFCompressor",   # → dist/PDFCompressor/
)
