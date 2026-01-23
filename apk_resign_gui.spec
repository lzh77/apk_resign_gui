# -*- mode: python ; coding: utf-8 -*-

# 可执行文件的基本配置
block_cipher = None

a = Analysis(
    ['main.py'],  # 主入口文件
    pathex=[],    # 模块搜索路径
    binaries=[],  # 额外的二进制文件
    datas=[       # 数据文件，如资源、配置等
        ('icon.ico', '.'),  # 包含图标文件
    ],
    hiddenimports=[],  # 隐式导入的模块
    hookspath=[],      # Hook脚本路径
    hooksconfig={},    # Hook配置
    runtime_hooks=[],  # 运行时Hook
    excludes=[],       # 排除的模块
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 根据操作系统设置不同的PEP兼容性标志
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='apk_resign_gui',  # 可执行文件名称
    debug=False,           # 调试模式
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,              # 使用UPX压缩
    upx_exclude=[],        # UPX排除列表
    runtime_tmpdir=None,   # 运行时临时目录
    console=False,         # 是否显示控制台窗口（False表示GUI应用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',       # 图标文件路径
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='apk_resign_gui',  # 收集文件的根目录名
)