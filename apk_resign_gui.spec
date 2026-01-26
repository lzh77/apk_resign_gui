# -*- mode: python ; coding: utf-8 -*-
"""
Spec file for APK Resign GUI Application
This spec file defines how PyInstaller should package the application
"""

# CAUTION: Please do not use __file__ variable in this file
# It is not reliable inside PyInstaller analysis

import sys
import os
from pathlib import Path

# --- Analysis ---
a = Analysis(
    ['main.py'],
    pathex=[os.path.dirname(os.path.realpath(globals().get('__file__', sys.argv[0])))],
    binaries=[],
    datas=[
        ('icon.ico', '.')  # Include icon file in the root of the executable
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# --- Executable ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='apk_resign_gui',         # 可执行文件名
    debug=False,                   # 是否启用调试
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                      # 是否使用UPX压缩
    upx_exclude=[],                # UPX排除列表
    runtime_tmpdir=None,           # 运行时临时目录
    console=False,                 # 是否显示控制台窗口 (False for GUI apps)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',               # 图标文件路径
)