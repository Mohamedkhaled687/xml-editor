"""
Browse Mode Window - Load XML from file browser
"""
import os
from PySide6.QtWidgets import QPushButton, QLineEdit, QFileDialog, QMessageBox, QLabel, QVBoxLayout, QHBoxLayout, \
    QWidget

from .base_xml_window import BaseXMLWindow

# Utilities imports
from ..utils import file_io


class BrowseWindow(BaseXMLWindow):
    """Browse mode window for loading XML from files."""

    def __init__(self, main_window) -> None:
        self.file_path_box: QLineEdit = QLineEdit()
        self.main_window = main_window

        super().__init__(
            window_title="🌐 SocialX XML Parser - Browse Mode",
            mode_name="Browse mode"
        )

    def _setup_input_section(self, parent_layout: QVBoxLayout) -> None:
        """Set up the file browser input section."""
        # File selection area
        file_widget = QWidget()
        file_widget.setObjectName("filePanel")
        file_layout = QVBoxLayout(file_widget)
        file_layout.setContentsMargins(20, 20, 20, 20)
        file_layout.setSpacing(10)

        file_title = QLabel("Load XML Data")
        file_title.setStyleSheet("""
            QLabel {
                color: rgba(200, 210, 220, 255);
                font-size: 22px;
                font-weight: bold;
            }
        """)
        file_layout.addWidget(file_title)

        file_input_layout = QHBoxLayout()
        self.file_path_box.setPlaceholderText("/path/to/your/file.xml")
        self.file_path_box.setObjectName("fileInput")
        self.file_path_box.setMinimumHeight(40)

        browse_btn = QPushButton("📁 Browse")
        browse_btn.setObjectName("browseFileBtn")
        browse_btn.setMinimumHeight(40)
        browse_btn.setMinimumWidth(120)
        browse_btn.clicked.connect(self.browse)

        upload_btn = QPushButton("⬆ Upload")
        upload_btn.setObjectName("uploadBtn")
        upload_btn.setMinimumHeight(40)
        upload_btn.setMinimumWidth(180)
        upload_btn.clicked.connect(self.upload)

        file_input_layout.addWidget(self.file_path_box)
        file_input_layout.addWidget(browse_btn)
        file_input_layout.addWidget(upload_btn)

        file_layout.addLayout(file_input_layout)
        parent_layout.addWidget(file_widget)

    def _get_panel_selector(self) -> str:
        """Return the panel selector for stylesheet."""
        return "#filePanel, #resultPanel, #opsPanel"

    def _get_initialization_message(self) -> str:
        """Return the initialization message."""
        return "Ready to load XML file."

    def browse(self) -> None:
        """Handle file browsing with format validation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select XML File",
            "",
            "XML files (*.xml);;Text files (*.txt)"
        )

        if not file_path:
            return  # User canceled dialog

        # Validate extension
        _, ext = os.path.splitext(file_path)

        if self.file_path_box and (ext.lower() == ".xml" or ext.lower() == ".txt"):
            self.file_path_box.setText(file_path)
        else:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please select a valid XML (.xml) file or Text (.txt) file.\n The selected " + ext.lower() + " extension is unacceptable"
            )
            return

    def upload(self) -> None:
        if not self.file_path_box.text():
            QMessageBox.warning(self, "No File", "Please select an XML file first.")
            return

        success, result = file_io.read_file(self.file_path_box.text())
        if not success:
            QMessageBox.critical(self, "Read Error", result)
            return

        try:
            if "<" in result and ">" in result:
                # Update ITSELF
                self.is_xml = True
                self.is_compressed = False
                # Update Parent if it exists and supports these attributes
                if self.main_window and hasattr(self.main_window, "is_xml"):
                    self.main_window.is_xml = True
            else:
                self.is_xml = False
                self.is_compressed = True
                if self.main_window and hasattr(self.main_window, "is_compressed"):
                    self.main_window.is_compressed = True

            self.xml_controller.set_xml_string(result)
            self.graph_controller.set_xml_data(result)
        except Exception as e:
            QMessageBox.warning(self, "XML Error", str(e))
            return

        self.input_text = result
        QMessageBox.information(self, "Success", "XML file loaded successfully.")

