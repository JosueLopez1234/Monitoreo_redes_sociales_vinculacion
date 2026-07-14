# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

datas = [

    ('web/templates', 'web/templates'),

    ('web/static', 'web/static'),

    ('web/datos_uleam.db', 'web'),

]

datas += collect_data_files('reportlab')

a = Analysis(

    ['web/app.py'],

    pathex=['.'],

    binaries=[],

    datas=datas,

    hiddenimports=[

        'reportlab',

        'reportlab.pdfbase',

        'reportlab.platypus',

        'openpyxl',

        'csv',

        'sqlite3',

        'jinja2',

        'flask',

    ],

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

    a.binaries,

    a.datas,

    [],

    name='AgroSocialAnalytics',

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

    icon='web/static/img/logo_uleam.ico'

)

coll = COLLECT(

    exe,

    a.binaries,

    a.zipfiles,

    a.datas,

    strip=False,

    upx=True,

    upx_exclude=[],

    name='AgroSocialAnalytics'

)