from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget

class BaseModule(ABC):
    """Abstract Base Class for CRM Modules (Students, Fees, Staff, Inquiries, etc.)."""
    
    @property
    @abstractmethod
    def module_id(self) -> str:
        """Unique module identifier (e.g. 'students')."""
        pass

    @property
    @abstractmethod
    def module_name(self) -> str:
        """Display name of the module (e.g. 'Students & Admissions')."""
        pass

    @property
    def module_icon(self) -> str:
        """Emoji or SVG icon identifier."""
        return "📁"

    @property
    def sort_order(self) -> int:
        """Ordering in the main navigation menu."""
        return 100

    def initialize(self):
        """Called during application bootstrap for module-level setup."""
        pass

    def shutdown(self):
        """Called during application exit."""
        pass

    @abstractmethod
    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        """Instantiates and returns the main view widget for this module."""
        pass
