# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\CRM\\app\\main.py'],
    pathex=['E:\\CRM'],
    binaries=[],
    datas=[('E:\\CRM\\app\\modules\\messaging\\assets', 'app/modules/messaging/assets')],
    hiddenimports=['app.core.base', 'app.core.config', 'app.core.database', 'app.core.signals', 'app.core.updater', 'app.models.course', 'app.models.custom_fields', 'app.models.message_template', 'app.models.staff', 'app.models.student', 'app.modules.base_module', 'app.modules.registry', 'app.modules.courses.controllers', 'app.modules.courses.course_module', 'app.modules.courses.views.course_form_dialog', 'app.modules.courses.views.course_list_view', 'app.modules.staff.controllers', 'app.modules.staff.staff_module', 'app.modules.staff.views.batch_form_dialog', 'app.modules.staff.views.batch_roster_dialog', 'app.modules.staff.views.staff_detail_dialog', 'app.modules.staff.views.staff_form_dialog', 'app.modules.staff.views.staff_list_view', 'app.modules.students.controllers', 'app.modules.students.reports', 'app.modules.students.student_module', 'app.modules.students.views.custom_fields_dialog', 'app.modules.students.views.student_detail_view', 'app.modules.students.views.student_form_dialog', 'app.modules.students.views.student_list_view', 'app.modules.messaging.controllers', 'app.modules.messaging.messaging_module', 'app.modules.messaging.views.messaging_view', 'app.modules.messaging.views.dispatch_queue_dialog', 'app.modules.messaging.views.template_editor_dialog', 'app.ui.theme', 'app.ui.widgets.dynamic_fields', 'app.ui.widgets.form_image_viewer', 'app.ui.widgets.search_bar', 'app.ui.widgets.stat_card', 'app.ui.widgets.update_dialog', 'sqlalchemy.dialects.sqlite', 'reportlab', 'reportlab.lib.pagesizes', 'reportlab.platypus', 'reportlab.lib.styles', 'reportlab.lib.colors', 'openpyxl', 'PIL', 'PIL.Image', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtPrintSupport'],
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
