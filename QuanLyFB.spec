# -*- mode: python ; coding: utf-8 -*-
"""Một EXE duy nhất: Quản lý FB (GUI) + mở phiên Chrome (--session)."""
from PyInstaller.utils.hooks import collect_all

datas = [
    ('firebase-credentials.json.enc', '.'),
    ('logo.png', '.'),
    ('logo.ico', '.'),
]
binaries = []
hiddenimports = [
    'firebase_admin',
    'firebase_admin.credentials',
    'firebase_admin.firestore',
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'psutil',
    'security',
    'data_store',
    'playwright',
    'playwright.sync_api',
]

tmp_ret = collect_all('firebase_admin')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

tmp_ret = collect_all('playwright')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['data_editor.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='QuanLyFB',
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
    icon='logo.ico',
)
