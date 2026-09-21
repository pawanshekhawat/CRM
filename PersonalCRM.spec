# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('E:\\CRM\\ui', 'ui'), ('E:\\CRM\\app\\modules\\messaging\\assets', 'app/modules/messaging/assets')]
binaries = [('C:\\Python314\\python3.dll', '.'), ('C:\\Python314\\python314.dll', '.'), ('C:\\Python314\\vcruntime140.dll', '.'), ('C:\\Python314\\vcruntime140_1.dll', '.'), ('C:\\Python314\\DLLs\\libcrypto-3.dll', '.'), ('C:\\Python314\\DLLs\\libffi-8.dll', '.'), ('C:\\Python314\\DLLs\\libssl-3.dll', '.'), ('C:\\Python314\\DLLs\\sqlite3.dll', '.'), ('C:\\Python314\\DLLs\\tcl86t.dll', '.'), ('C:\\Python314\\DLLs\\tk86t.dll', '.'), ('C:\\Python314\\DLLs\\zlib1.dll', '.')]
hiddenimports = ['app.core.base', 'app.core.config', 'app.core.database', 'app.core.signals', 'app.core.updater', 'app.models.course', 'app.models.custom_fields', 'app.models.message_template', 'app.models.staff', 'app.models.student', 'app.modules.courses.controllers', 'app.modules.staff.controllers', 'app.modules.students.controllers', 'app.modules.students.reports', 'app.modules.messaging.controllers', 'app.bridge', 'app.bridge.crm_bridge', 'app.bridge.students_bridge', 'app.bridge.courses_bridge', 'app.bridge.staff_bridge', 'app.bridge.finance_bridge', 'app.bridge.messaging_bridge', 'app.bridge.reports_bridge', 'app.bridge.updater_bridge', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickControls2', 'PySide6.QtQuickLayouts', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtPrintSupport', 'sqlalchemy.dialects.sqlite', 'reportlab', 'reportlab.lib.pagesizes', 'reportlab.platypus', 'reportlab.lib.styles', 'reportlab.lib.colors', 'openpyxl', 'PIL', 'PIL.Image']
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['E:\\CRM\\app\\main.py'],
    pathex=['E:\\CRM'],
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
    name='PersonalCRM',
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
)
