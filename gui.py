"""
Application Manager - Controls the flow between windows
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon
from src.ui import ManualWindow
from src.ui import LandingWindow
from src.ui import BrowseWindow


class AppManager:
    """Manages the application flow between windows."""

    def __init__(self):
        # Reuse existing QApplication if one exists (Qt only allows one per process)
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # Set application icon
        # Handle PyInstaller temporary directory path
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

        # Set application font
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)

        # Import here to avoid circular imports

        self.landing_window = LandingWindow()
        self.manual_window = None
        self.browse_window = None

        # Connect navigation signals
        self.landing_window.browse_clicked.connect(self.show_browse_mode)
        self.landing_window.manual_clicked.connect(self.show_manual_mode)

        # Show landing window
        self.landing_window.showMaximized()

    def show_browse_mode(self):
        """Show browse mode window."""

        if self.browse_window is None:
            self.browse_window = BrowseWindow(self)
            self.browse_window.back_clicked.connect(self.show_landing)

        self.landing_window.hide()
        self.browse_window.showMaximized()

    def show_manual_mode(self):
        """Show manual mode window."""

        if self.manual_window is None:
            self.manual_window = ManualWindow(self)
            self.manual_window.back_clicked.connect(self.show_landing)

        self.landing_window.hide()
        self.manual_window.showMaximized()

    def show_landing(self):
        """Return to landing window."""
        if self.browse_window:
            self.browse_window.hide()
        if self.manual_window:
            self.manual_window.hide()
        self.landing_window.showMaximized()

    def run(self):
        """Start the Qt event loop."""
        return self.app.exec()


if __name__ == '__main__':
    manager = AppManager()
    exit_code = manager.run()
    sys.exit(exit_code)

