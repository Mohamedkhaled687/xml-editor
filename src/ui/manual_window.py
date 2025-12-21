"""
Manual Mode Window - Load XML from manual input
"""
from PySide6.QtWidgets import QPushButton, QTextEdit, QMessageBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from .base_xml_window import BaseXMLWindow


class ManualWindow(BaseXMLWindow):
    """Manual mode window for loading XML from manual text input."""

    def __init__(self, main_window) -> None:
        self.input_text_box: QTextEdit = QTextEdit()
        self.main_window = main_window

        super().__init__(
            window_title="🌐 SocialX XML Parser - Manual Mode",
            mode_name="Manual mode"
        )

    def _setup_input_section(self, parent_layout: QVBoxLayout) -> None:
        """Set up the text editor input section."""
        # Text area
        text_widget = QWidget()
        text_widget.setObjectName("textPanel")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(20, 20, 20, 20)
        text_layout.setSpacing(10)

        text_title_layout = QHBoxLayout()
        text_title_layout.setContentsMargins(5, 5, 5, 5)
        text_title_layout.setSpacing(40)

        text_title = QLabel("Enter XML Data")
        text_title.setStyleSheet("""
            QLabel {
                color: rgba(200, 210, 220, 255);
                font-size: 22px;
                font-weight: bold;
            }
        """)

        upload_btn = QPushButton("⬆ Upload")
        upload_btn.setObjectName("uploadBtn")
        upload_btn.setMinimumHeight(40)
        upload_btn.setMaximumWidth(150)
        upload_btn.clicked.connect(self.upload)

        text_title_layout.addWidget(text_title)
        text_title_layout.addWidget(upload_btn)

        text_layout.addLayout(text_title_layout)

        self.input_text_box.setPlaceholderText("Enter your SocialX XML Data here")
        self.input_text_box.setObjectName("textInput")
        self.input_text_box.setMinimumHeight(40)

        text_layout.addWidget(self.input_text_box, 1)
        parent_layout.addWidget(text_widget)

    def _get_panel_selector(self) -> str:
        """Return the panel selector for stylesheet."""
        return "#textPanel, #resultPanel, #opsPanel"

    def _get_initialization_message(self) -> str:
        """Return the initialization message."""
        return "Ready to load XML text."

    def upload(self) -> None:
        """Handle XML text upload and parsing (manual input)."""
        self.input_text = self.input_text_box.toPlainText().strip()
        if not self.input_text:
            QMessageBox.warning(
                self,
                "No Data",
                "Please enter valid XML data first."
            )
            return

        try:
            if "<" in self.input_text and ">" in self.input_text:
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

            self.xml_controller.set_xml_string(self.input_text)
            self.graph_controller.set_xml_data(self.input_text)
        except Exception as e:
            QMessageBox.warning(
                self,
                "XML Error",
                str(e)
            )
            return

        QMessageBox.information(
            self,
            "Success",
            "XML data parsed successfully.\nData is ready for operations."
        )
