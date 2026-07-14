# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

datas = [

    ('web/templates', 'web/templates'),

    ('web/static', 'web/static'),

    ('web/datos_uleam.db', 'web'),

]

datas += collect_data_files('reportlab')

a = Analysis(

    ['web/run.py'],

    pathex=['.'],

    binaries=[],

    datas=datas,

    hiddenimports=[

        'flask',

        'jinja2',

        'sqlite3',

        'csv',

        'openpyxl',

        'reportlab',

        'reportlab.pdfbase',

        'reportlab.platypus',

        'waitress',

        'database',

        'pdf_generator',

        'excel_generator',

        'csv_generator',

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

    [],

    exclude_binaries=True,

    name='AgroSocialAnalytics',

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

    icon='web/static/img/logo_uleam.ico',

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