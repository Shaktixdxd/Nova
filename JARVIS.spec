# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\.env', '.'), ('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\DataVoice.html', '.'), ('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\JARVIS AI.code-workspace', '.'), ('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\Requirements.txt', '.'), ('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\Backend', 'Backend/'), ('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\Data', 'Data/'), ('C:\\Users\\manth\\OneDrive\\Desktop\\JARVIS reworked\\JARVIS\\Frontend', 'Frontend/')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='JARVIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\manth\\Downloads\\007_IronMan_2x_44222.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JARVIS',
)
