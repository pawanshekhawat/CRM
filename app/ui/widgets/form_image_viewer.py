import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap, QWheelEvent, QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.config import ADMISSION_FORMS_DIR, ROOT_DIR

class InteractiveGraphicsView(QGraphicsView):
    """QGraphicsView with smooth mouse-wheel zooming and drag-panning."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("""
            QGraphicsView {
                background-color: #0A0D14;
                border: 1px solid #1E293B;
                border-radius: 8px;
            }
        """)
        self._zoom_factor = 1.0

    def wheelEvent(self, event: QWheelEvent):
        """Zoom in/out with mouse wheel."""
        zoom_in_factor = 1.2
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom = zoom_in_factor
            self._zoom_factor *= zoom
        else:
            zoom = zoom_out_factor
            self._zoom_factor *= zoom

        self.scale(zoom, zoom)
        event.accept()

    def reset_zoom(self):
        self.resetTransform()
        self._zoom_factor = 1.0


class FullscreenFormDialog(QDialog):
    """Modal Fullscreen Lightbox for viewing scanned admission forms in ultra-high resolution."""

    def __init__(self, pixmap: QPixmap, title: str = "Admission Form Fullscreen View", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: #06080C;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Floating Top Toolbar
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 6, 12, 6)

        title_lbl = QLabel(f"📄 {title}")
        title_lbl.setStyleSheet("color: #F8FAFC; font-size: 15px; font-weight: 700;")
        top_bar.addWidget(title_lbl)

        top_bar.addStretch()

        btn_style = """
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #38BDF8;
            }
        """

        self.zoom_in_btn = QPushButton("➕ Zoom In")
        self.zoom_in_btn.setStyleSheet(btn_style)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        top_bar.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton("➖ Zoom Out")
        self.zoom_out_btn.setStyleSheet(btn_style)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        top_bar.addWidget(self.zoom_out_btn)

        self.fit_btn = QPushButton("⤢ Fit to Screen")
        self.fit_btn.setStyleSheet(btn_style)
        self.fit_btn.clicked.connect(self._fit_to_screen)
        top_bar.addWidget(self.fit_btn)

        self.actual_size_btn = QPushButton("1:1 Actual Size")
        self.actual_size_btn.setStyleSheet(btn_style)
        self.actual_size_btn.clicked.connect(self._actual_size)
        top_bar.addWidget(self.actual_size_btn)

        close_btn = QPushButton("✕ Close (Esc)")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF444422;
                color: #EF4444;
                border: 1px solid #EF444455;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.accept)
        top_bar.addWidget(close_btn)

        layout.addLayout(top_bar)

        # Interactive Graphics View
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)

        self.view = InteractiveGraphicsView(self)
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        self._fit_to_screen()

    def _zoom_in(self):
        self.view.scale(1.25, 1.25)

    def _zoom_out(self):
        self.view.scale(0.8, 0.8)

    def _actual_size(self):
        self.view.reset_zoom()

    def _fit_to_screen(self):
        self.view.resetTransform()
        if not self.pixmap_item.pixmap().isNull():
            self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)


class FormImageViewer(QWidget):
    """Reusable Admission Form Image Viewer Widget with Zoom, Pan, Fit, and Fullscreen."""

    form_uploaded = Signal(str) # Emits relative path of saved image

    def __init__(self, relative_form_path: Optional[str] = None, student_name: str = "Student", parent=None):
        super().__init__(parent)
        self.student_name = student_name
        self.relative_path = relative_form_path
        self._current_pixmap: Optional[QPixmap] = None

        self._build_ui()
        if self.relative_path:
            self.load_image(self.relative_path)
        else:
            self._show_empty_state()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # Control Toolbar Card
        self.toolbar_card = QFrame()
        self.toolbar_card.setObjectName("card")
        self.toolbar_card.setStyleSheet("""
            QFrame#card {
                background-color: #101520;
                border: 1px solid #1E293B;
                border-radius: 8px;
            }
        """)
        tb_layout = QHBoxLayout(self.toolbar_card)
        tb_layout.setContentsMargins(12, 8, 12, 8)
        tb_layout.setSpacing(8)

        self.info_lbl = QLabel(f"📄 Admission Form Slip: <b>{self.student_name}</b>")
        self.info_lbl.setStyleSheet("color: #CBD5E1; font-size: 13px;")
        tb_layout.addWidget(self.info_lbl)

        tb_layout.addStretch()

        btn_style = """
            QPushButton {
                background-color: #1E293B;
                color: #E2E8F0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #38BDF8;
                color: #38BDF8;
            }
        """

        self.zoom_in_btn = QPushButton("➕ Zoom In")
        self.zoom_in_btn.setStyleSheet(btn_style)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        tb_layout.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton("➖ Zoom Out")
        self.zoom_out_btn.setStyleSheet(btn_style)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        tb_layout.addWidget(self.zoom_out_btn)

        self.fit_btn = QPushButton("⤢ Fit View")
        self.fit_btn.setStyleSheet(btn_style)
        self.fit_btn.clicked.connect(self._fit_to_view)
        tb_layout.addWidget(self.fit_btn)

        self.actual_btn = QPushButton("1:1 Size")
        self.actual_btn.setStyleSheet(btn_style)
        self.actual_btn.clicked.connect(self._actual_size)
        tb_layout.addWidget(self.actual_btn)

        self.fullscreen_btn = QPushButton("⛶ Full Screen")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284C722;
                color: #38BDF8;
                border: 1px solid #0284C755;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        self.fullscreen_btn.clicked.connect(self._open_fullscreen)
        tb_layout.addWidget(self.fullscreen_btn)

        self.replace_btn = QPushButton("📁 Replace / Upload Form")
        self.replace_btn.setStyleSheet(btn_style)
        self.replace_btn.clicked.connect(self._on_upload_form)
        tb_layout.addWidget(self.replace_btn)

        self.main_layout.addWidget(self.toolbar_card)

        # Graphic Scene & View
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.view = InteractiveGraphicsView(self)
        self.view.setScene(self.scene)
        self.main_layout.addWidget(self.view, stretch=1)

        # Empty State Placeholder Container
        self.empty_card = QFrame()
        self.empty_card.setObjectName("card")
        self.empty_card.setStyleSheet("""
            QFrame#card {
                background-color: #0D111A;
                border: 2px dashed #283347;
                border-radius: 12px;
            }
        """)
        empty_layout = QVBoxLayout(self.empty_card)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(12)

        icon_lbl = QLabel("📑")
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(icon_lbl)

        msg_lbl = QLabel("No Scanned Admission Form Attached")
        msg_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        msg_lbl.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(msg_lbl)

        sub_lbl = QLabel("You can attach the physical registration form image for instant digital viewing & zoom inspection.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(sub_lbl)

        upload_btn = QPushButton("📁 Attach Admission Form Image")
        upload_btn.setObjectName("primaryBtn")
        upload_btn.setStyleSheet("padding: 8px 18px; font-weight: 700; font-size: 13px;")
        upload_btn.clicked.connect(self._on_upload_form)
        empty_layout.addWidget(upload_btn, alignment=Qt.AlignCenter)

        self.main_layout.addWidget(self.empty_card, stretch=1)
        self.empty_card.hide()

    def load_image(self, relative_or_abs_path: str):
        """Loads and displays the admission form image."""
        self.relative_path = relative_or_abs_path
        
        # Resolve path
        path = Path(relative_or_abs_path)
        if not path.is_absolute():
            # Check relative to ADMISSION_FORMS_DIR or ROOT_DIR
            p1 = ADMISSION_FORMS_DIR / relative_or_abs_path
            p2 = ROOT_DIR / relative_or_abs_path
            if p1.exists():
                path = p1
            elif p2.exists():
                path = p2

        if not path.exists():
            self._show_empty_state()
            return

        pix = QPixmap(str(path))
        if pix.isNull():
            self._show_empty_state()
            return

        self._current_pixmap = pix
        self.pixmap_item.setPixmap(pix)
        self.scene.setSceneRect(QRectF(pix.rect()))
        
        self.empty_card.hide()
        self.view.show()
        self.toolbar_card.show()
        self._fit_to_view()

    def _show_empty_state(self):
        self._current_pixmap = None
        self.pixmap_item.setPixmap(QPixmap())
        self.view.hide()
        self.toolbar_card.hide()
        self.empty_card.show()

    def _zoom_in(self):
        self.view.scale(1.2, 1.2)

    def _zoom_out(self):
        self.view.scale(0.8, 0.8)

    def _actual_size(self):
        self.view.reset_zoom()

    def _fit_to_view(self):
        self.view.resetTransform()
        if self._current_pixmap and not self._current_pixmap.isNull():
            self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def _open_fullscreen(self):
        if not self._current_pixmap or self._current_pixmap.isNull():
            return
        dlg = FullscreenFormDialog(self._current_pixmap, title=f"Admission Form — {self.student_name}", parent=self)
        dlg.exec()

    def _on_upload_form(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Admission Form Scanned Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff)",
        )
        if not file_path:
            return

        from app.modules.students.controllers import StudentController
        saved_rel_name = StudentController.save_admission_form_attachment(file_path)
        if saved_rel_name:
            self.load_image(saved_rel_name)
            self.form_uploaded.emit(saved_rel_name)
