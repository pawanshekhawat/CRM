from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

class SearchBar(QWidget):
    """Search input field with debounce timer and clear action."""

    searched = Signal(str)

    def __init__(self, placeholder: str = "Search by Name, ID, Mobile, Aadhar, College...", debounce_ms: int = 250, parent=None):
        super().__init__(parent)
        self.debounce_ms = debounce_ms

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumWidth(280)
        layout.addWidget(self.input)

        # Debounce timer so fast typing doesn't spam DB queries
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(self.debounce_ms)
        self.timer.timeout.connect(self._emit_search)

        self.input.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        self.timer.start()

    def _emit_search(self):
        self.searched.emit(self.input.text().strip())

    def text(self) -> str:
        return self.input.text().strip()

    def clear(self):
        self.input.clear()
