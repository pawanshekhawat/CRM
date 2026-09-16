import webbrowser
from typing import Optional
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.config import APP_NAME, APP_VERSION
from app.core.updater import (
    UpdateCheckWorker,
    UpdateDownloadWorker,
    UpdateInfo,
    apply_update_and_restart,
    fetch_update_info,
)


class UpdateDialog(QDialog):
    """
    Modern dark-themed Software Update Dialog.
    Displays release version comparisons, changelog, USB data safety guarantees,
    download progress tracking, and 1-click update installation.
    """

    def __init__(self, update_info: Optional[UpdateInfo] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.update_info: UpdateInfo = update_info or UpdateInfo()
        self.check_worker: Optional[UpdateCheckWorker] = None
        self.download_worker: Optional[UpdateDownloadWorker] = None
        self.downloaded_file_path: Optional[str] = None

        self.setWindowTitle(f"{APP_NAME} - Software Update")
        self.setMinimumSize(560, 460)
        self.resize(600, 500)
        self._build_ui()

        if update_info:
            self._render_update_info(update_info)
        else:
            self._start_check_for_updates()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # 1. Header Card
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_frame.setStyleSheet("""
            QFrame#card {
                background-color: #131823;
                border: 1px solid #1F293D;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(14, 12, 14, 12)
        h_layout.setSpacing(12)

        icon_lbl = QLabel("🚀")
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        h_layout.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        self.title_lbl = QLabel(f"<b>{APP_NAME} Updates</b>")
        self.title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #F8FAFC; background: transparent;")
        info_col.addWidget(self.title_lbl)

        self.version_badge_lbl = QLabel(f"Current Version: <b>v{APP_VERSION}</b>")
        self.version_badge_lbl.setStyleSheet("font-size: 11.5px; color: #94A3B8; background: transparent;")
        info_col.addWidget(self.version_badge_lbl)
        h_layout.addLayout(info_col, 1)

        self.status_pill = QLabel("Checking...")
        self.status_pill.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 4px 12px; font-size: 11px; color: #E2E8F0; font-weight: 600;")
        h_layout.addWidget(self.status_pill)

        main_layout.addWidget(header_frame)

        # 2. Data Privacy & USB Offline Guarantee Box
        privacy_box = QFrame()
        privacy_box.setStyleSheet("background-color: #064E3B22; border: 1px solid #05966955; border-radius: 8px; padding: 8px 12px;")
        p_layout = QHBoxLayout(privacy_box)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.setSpacing(8)

        p_icon = QLabel("🔒")
        p_icon.setStyleSheet("font-size: 14px; background: transparent;")
        p_layout.addWidget(p_icon)

        p_text = QLabel(
            "<b>USB Offline Guarantee:</b> All student records, fees, and photo attachments stay strictly "
            "on your USB flash drive. Updating will <b>never</b> overwrite or delete your database data."
        )
        p_text.setStyleSheet("color: #34D399; font-size: 11px; background: transparent;")
        p_text.setWordWrap(True)
        p_layout.addWidget(p_text, 1)

        main_layout.addWidget(privacy_box)

        # 3. Changelog / Release Notes Box
        main_layout.addWidget(QLabel("<b>What's New in this Release:</b>"))

        self.notes_box = QTextEdit()
        self.notes_box.setReadOnly(True)
        self.notes_box.setMinimumHeight(130)
        self.notes_box.setStyleSheet("""
            QTextEdit {
                background-color: #0F131C;
                border: 1px solid #1F293D;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                color: #E2E8F0;
                line-height: 1.45;
            }
        """)
        main_layout.addWidget(self.notes_box, 1)

        # 4. Download Progress Bar (Hidden by default)
        self.progress_container = QWidget()
        self.progress_container.setVisible(False)
        prog_layout = QVBoxLayout(self.progress_container)
        prog_layout.setContentsMargins(0, 0, 0, 0)
        prog_layout.setSpacing(4)

        self.progress_lbl = QLabel("Downloading update: 0%...")
        self.progress_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        prog_layout.addWidget(self.progress_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1E2330;
                border: 1px solid #283042;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 3px;
            }
        """)
        prog_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_container)

        # 5. Dialog Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.github_btn = QPushButton("🌐 View on GitHub")
        self.github_btn.setToolTip("Open GitHub releases page in web browser")
        self.github_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #CBD5E1;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        self.github_btn.clicked.connect(self._on_view_github_clicked)
        btn_layout.addWidget(self.github_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        self.update_btn = QPushButton("🚀 Update Now")
        self.update_btn.setEnabled(False)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: #FFFFFF;
                border: 1px solid #047857;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 12.5px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #10B981;
                border-color: #059669;
            }
            QPushButton:disabled {
                background-color: #1E293B;
                color: #64748B;
                border-color: #334155;
            }
        """)
        self.update_btn.clicked.connect(self._on_update_clicked)
        btn_layout.addWidget(self.update_btn)

        main_layout.addLayout(btn_layout)

    def _start_check_for_updates(self):
        """Starts background update check."""
        self.status_pill.setText("Checking...")
        self.status_pill.setStyleSheet("background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; border-radius: 12px; padding: 4px 12px; font-size: 11px;")
        self.notes_box.setHtml("<i>Connecting to GitHub repository to check for software updates...</i>")

        self.check_worker = UpdateCheckWorker(self)
        self.check_worker.update_found.connect(self._render_update_info)
        self.check_worker.up_to_date.connect(self._render_update_info)
        self.check_worker.check_failed.connect(self._on_check_failed)
        self.check_worker.start()

    def _render_update_info(self, info: UpdateInfo):
        """Updates the dialog elements with fetched release info."""
        self.update_info = info

        if info.is_update_available:
            self.title_lbl.setText(f"<b>🎉 New Update Available: v{info.latest_version}</b>")
            self.version_badge_lbl.setText(f"Current: <b>v{APP_VERSION}</b> ➔ Latest: <b style='color:#34D399;'>v{info.latest_version}</b>")
            self.status_pill.setText(f"✨ v{info.latest_version} Available")
            self.status_pill.setStyleSheet("background-color: #10B9811F; color: #34D399; border: 1px solid #10B98155; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;")
            self.update_btn.setEnabled(True)
            self.update_btn.setText(f"🚀 Update to v{info.latest_version}")
        else:
            self.title_lbl.setText(f"<b>{APP_NAME} is Up to Date</b>")
            self.version_badge_lbl.setText(f"Current Version: <b>v{APP_VERSION}</b> (Latest)")
            self.status_pill.setText("✅ Up to Date")
            self.status_pill.setStyleSheet("background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 600;")
            self.update_btn.setEnabled(False)
            self.update_btn.setText("Up to Date")

        # Format Changelog HTML
        html_lines = ["<ul style='margin-left: -20px; line-height: 1.6;'>"]
        if info.changelog:
            for item in info.changelog:
                html_lines.append(f"<li>{item}</li>")
        else:
            html_lines.append(f"<li>{info.title or 'General improvements and bug fixes.'}</li>")
        html_lines.append("</ul>")

        if info.release_date:
            html_lines.insert(0, f"<p style='color: #94A3B8; margin-bottom: 8px;'><b>Released on:</b> {info.release_date}</p>")

        self.notes_box.setHtml("".join(html_lines))

    def _on_check_failed(self, error_msg: str):
        self.status_pill.setText("Offline / Check Failed")
        self.status_pill.setStyleSheet("background-color: #7C2D122A; color: #FED7AA; border: 1px solid #9A3412; border-radius: 12px; padding: 4px 12px; font-size: 11px;")
        self.notes_box.setHtml(f"<p style='color: #F87171;'>Could not check for updates online: {error_msg}</p><p style='color: #94A3B8;'>Please verify your internet connection or check GitHub directly.</p>")
        self.update_btn.setEnabled(False)

    def _on_view_github_clicked(self):
        url = self.update_info.download_url or f"https://github.com/{self.update_info.github_repo}/releases"
        QDesktopServices.openUrl(QUrl(url))

    def _on_update_clicked(self):
        if not self.update_info.download_url:
            QMessageBox.information(
                self,
                "Manual Download Required",
                f"Please download the latest release directly from GitHub:\nhttps://github.com/{self.update_info.github_repo}/releases/latest",
            )
            self._on_view_github_clicked()
            return

        # Start Download
        self.update_btn.setEnabled(False)
        self.update_btn.setText("Downloading...")
        self.progress_container.setVisible(True)
        self.progress_lbl.setText("Downloading update package...")

        self.download_worker = UpdateDownloadWorker(
            download_url=self.update_info.download_url,
            file_name=self.update_info.file_name or f"PersonalCRM_v{self.update_info.latest_version}.zip",
            parent=self,
        )
        self.download_worker.progress.connect(self._on_download_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.download_failed.connect(self._on_download_failed)
        self.download_worker.start()

    def _on_download_progress(self, downloaded: int, total: int, percentage: float):
        self.progress_bar.setValue(int(percentage))
        d_mb = downloaded / (1024 * 1024)
        t_mb = total / (1024 * 1024) if total > 0 else 0
        if total > 0:
            self.progress_lbl.setText(f"Downloading update: {percentage:.1f}% ({d_mb:.1f} MB of {t_mb:.1f} MB)...")
        else:
            self.progress_lbl.setText(f"Downloading update: {d_mb:.1f} MB downloaded...")

    def _on_download_finished(self, file_path: str):
        self.downloaded_file_path = file_path
        self.progress_lbl.setText("✅ Download completed!")
        self.progress_bar.setValue(100)

        QMessageBox.information(
            self,
            "Update Ready to Install",
            f"🎉 Update to v{self.update_info.latest_version} has downloaded successfully!\n\n"
            f"Click OK to close the application and apply the update.\n"
            f"Then simply double-click 'PersonalCRM.exe' on your pen drive to open the updated version.\n\n"
            f"🔒 All student records, fees, and photo attachments remain 100% safe on your drive.",
        )

        try:
            apply_update_and_restart(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Update Installation Error", f"Failed to apply update: {e}")
            self.update_btn.setEnabled(True)
            self.update_btn.setText("Retry Update")


    def _on_download_failed(self, error_msg: str):
        self.progress_container.setVisible(False)
        self.update_btn.setEnabled(True)
        self.update_btn.setText("Retry Download")
        QMessageBox.warning(
            self,
            "Download Failed",
            f"Failed to download the update package:\n{error_msg}\n\nYou can also download it manually from GitHub.",
        )
