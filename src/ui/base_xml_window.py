"""
Base XML Window - Provides common functionality for XML-related UI windows.
"""
from typing import Optional, Dict, List, Tuple, Any
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QLineEdit, QFileDialog,
                               QMessageBox, QLabel, QDialog)
from PySide6.QtCore import Qt, Signal, QSize

# Controller imports
from ..controllers import XMLController
# from ..controllers import DataController, GraphController  # TODO: Implement these controllers if needed

# UI window imports
from .code_viewer_window import CodeViewerWindow
# from .graph_visualization_window import GraphVisualizationWindow  # TODO: Implement if needed

# utilities imports
from ..utils import file_io

# Parent Imports
from abc import abstractmethod


class BaseXMLWindow(QMainWindow):
    """Base class for XML-related UI windows with shared functionality."""

    back_clicked = Signal()

    def __init__(self, window_title: str, mode_name: str) -> None:
        super().__init__()

        # Initialize controllers
        self.xml_controller: XMLController = XMLController()
        # self.data_controller: DataController = DataController()  # TODO: Implement DataController
        # self.graph_controller: GraphController = GraphController()  # TODO: Implement GraphController

        self.input_text: str = ""
        self.output_text: str = ""
        self.result_text_box: QTextEdit = QTextEdit()

        self.window_title: str = window_title
        self.mode_name: str = mode_name

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle(self.window_title)
        self.setMinimumSize(1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Top bar with back button
        top_bar = QHBoxLayout()

        back_btn = QPushButton("← Back to Home")
        back_btn.setObjectName("backBtn")
        back_btn.setMinimumHeight(40)
        back_btn.setMinimumWidth(150)
        back_btn.clicked.connect(self.back_clicked.emit)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # Container for the grid layout
        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(15)

        main_layout.addLayout(sub_layout)

        # Left side - input section + Operation Log
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(15)

        # Input section (to be implemented by subclasses)
        self._setup_input_section(left_layout)

        # Result (Read-Only) area
        result_widget = QWidget()
        result_widget.setObjectName("resultPanel")
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(20, 20, 20, 20)
        result_layout.setSpacing(15)

        result_title = QLabel("Operation Result")
        result_title.setStyleSheet("""
            QLabel {
                color: rgba(100, 230, 255, 255);
                font-size: 22px;
                font-weight: bold;
            }
        """)

        save_btn = QPushButton("⬆ Save")
        save_btn.setObjectName("saveBtn")
        save_btn.setMinimumHeight(40)
        save_btn.setMaximumWidth(150)
        save_btn.clicked.connect(self.save)

        result_title_layout = QHBoxLayout()
        result_title_layout.setContentsMargins(20, 20, 20, 20)
        result_title_layout.setSpacing(40)

        result_title_layout.addWidget(result_title)
        result_title_layout.addWidget(save_btn)

        result_layout.addLayout(result_title_layout)

        self.result_text_box.setReadOnly(True)
        self.result_text_box.setObjectName("resultText")

        result_layout.addWidget(self.result_text_box)
        left_layout.addWidget(result_widget)

        sub_layout.addWidget(left_widget)

        # Right side - Operations
        ops_widget = QWidget()
        ops_widget.setObjectName("opsPanel")
        ops_layout = QVBoxLayout(ops_widget)
        ops_layout.setContentsMargins(20, 20, 20, 20)
        ops_layout.setSpacing(15)

        ops_title = QLabel("Operations")
        ops_title.setStyleSheet("""
            QLabel {
                color: rgba(100, 230, 255, 255);
                font-size: 20px;
                font-weight: bold;
            }
        """)
        ops_layout.addWidget(ops_title)

        parsing_ops = [
            ("📋 Validate XML Structure", self.validate_xml),
            ("🛠️ Correct Errors", self.correct_errors),
            ("✨ Format XML", self.format_xml),
            ("📦 Compress File", self.compress),
            ("📂 Decompress File", self.decompress),
            ("✂️ Minify XML", self.minify),
            ("📄 Export to JSON", self.export_to_json),
            ("🕸️ Visualize Network Graph", self.visualize_network),
            ("📊 Show Users Statistics", self.show_user_stats),
            ("🔍 Search for Topic/Posts", self.search)
        ]

        for text, handler in parsing_ops:
            btn = QPushButton(text)
            btn.setObjectName("operationBtn")
            btn.setMinimumHeight(42)
            btn.clicked.connect(handler)
            ops_layout.addWidget(btn)

        ops_layout.addStretch()

        sub_layout.addWidget(ops_widget)

    @abstractmethod
    def _setup_input_section(self, parent_layout: QVBoxLayout) -> None:
        """
        Abstract method to set up the input section.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _setup_input_section")

    @abstractmethod
    def _get_panel_selector(self) -> str:
        """
        Abstract method to get the panel selector for stylesheet.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _get_panel_selector")

    @abstractmethod
    def _get_initialization_message(self) -> str:
        """
        Abstract method to get the initialization message.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _get_initialization_message")

    def apply_stylesheet(self) -> None:
        """Apply modern stylesheet matching landing page."""
        panel_selector = self._get_panel_selector()
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgba(10, 15, 30, 255),
                                           stop:1 rgba(15, 25, 40, 255));
            }}

            {panel_selector} {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgba(20, 35, 55, 200),
                                           stop:1 rgba(15, 25, 45, 200));
                border: 2px solid rgba(100, 150, 200, 100);
                border-radius: 15px;
            }}

            #fileInput, #textInput {{
                background-color: rgba(30, 45, 65, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 8px;
                color: rgba(220, 230, 240, 255);
                padding: 10px;
                font-size: 13px;
            }}

            #resultText {{
                background-color: rgba(15, 20, 35, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 8px;
                color: rgba(220, 230, 240, 255);
                padding: 12px;
                font-size: 12px;
            }}

            #backBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(60, 80, 100, 200),
                                           stop:1 rgba(80, 100, 120, 200));
                border: 2px solid rgba(100, 150, 200, 150);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 15px;
            }}

            #backBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(80, 100, 120, 230),
                                           stop:1 rgba(100, 120, 140, 230));
            }}

            #browseFileBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(40, 120, 200, 200),
                                           stop:1 rgba(60, 140, 220, 200));
                border: 2px solid rgba(80, 160, 240, 200);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}

            #browseFileBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(60, 140, 220, 230),
                                           stop:1 rgba(80, 160, 240, 230));
            }}

            #uploadBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(50, 150, 255, 200),
                                           stop:1 rgba(80, 180, 255, 200));
                border: 2px solid rgba(100, 200, 255, 255);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}

            #uploadBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(70, 170, 255, 230),
                                           stop:1 rgba(100, 200, 255, 230));
            }}
            
            #saveBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(50, 150, 255, 200),
                                           stop:1 rgba(80, 180, 255, 200));
                border: 2px solid rgba(100, 200, 255, 255);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}

            #saveBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(70, 170, 255, 230),
                                           stop:1 rgba(100, 200, 255, 230));
            }}

            #operationBtn {{
                background: rgba(40, 70, 110, 180);
                border: 1px solid rgba(80, 120, 180, 150);
                border-radius: 8px;
                color: rgba(200, 220, 240, 255);
                font-size: 13px;
                text-align: left;
                padding-left: 15px;
            }}

            #operationBtn:hover {{
                background: rgba(60, 90, 130, 200);
                border: 1px solid rgba(100, 150, 200, 180);
                color: white;
            }}

            #operationBtn:pressed {{
                background: rgba(30, 50, 80, 180);
            }}
        """)

    @abstractmethod
    def upload(self) -> None:
        """
        Handle file upload and parsing.

        overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement upload_and_parse")

    def save(self) -> None:
        """Save the result of the current operation to a file."""
        self.output_text = self.result_text_box.toPlainText().strip()
        if not self.output_text:
            QMessageBox.warning(
                self,
                "No Data",
                "There is no data to save."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Result",
            "",
            "Text Files (*.txt);; XML Files (*.xml);;JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return  # User canceled save dialog

        success, message = file_io.write_file(file_path, self.output_text)
        if not success:
            QMessageBox.critical(
                self,
                "Save Error",
                message
            )
            return

        QMessageBox.information(
            self,
            "Saved",
            "File saved successfully."
        )

    def error_event_handler(self) -> bool:
        """Centralized UI error handler."""
        if self.xml_controller is None:  # error in initializing controller
            QMessageBox.critical(
                self,
                "System Error",
                "XML controller is not initialized."
            )
            return False

        if not self.input_text or not self.input_text.strip():  # empty input or xml
            QMessageBox.warning(
                self,
                "No Input",
                "Please load or enter XML data before performing this operation."
            )
            return False

        if not self.xml_controller.get_xml_string():  # empty class attribute = no input was given
            QMessageBox.warning(
                self,
                "No XML Loaded",
                "XML data has not been processed yet.\nPlease upload or parse the XML first."
            )
            return False

        return True

    def validate_xml(self) -> None:
        """Validate XML structure."""
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.validate()
        self.result_text_box.setText(self.output_text)
        self.result_text_box.show()

    def correct_errors(self) -> None:
        """Parse user data and show statistics."""
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.autocorrect()
        self.result_text_box.setText(self.output_text)
        self.result_text_box.show()

    def format_xml(self) -> None:
        """Format/prettify XML file."""
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.format()
        self.result_text_box.setText(self.output_text)
        self.result_text_box.show()

    def compress(self) -> None:
        """Check for data integrity issues."""
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.compress_to_string()
        self.result_text_box.setText(self.output_text)
        self.result_text_box.show()

    def decompress(self) -> None:
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.decompress_from_string(self.input_text)
        self.result_text_box.setText(self.output_text)
        self.result_text_box.show()

    def minify(self) -> None:
        """View XML file content in code viewer."""
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.minify()
        self.result_text_box.setText(self.output_text)
        self.result_text_box.show()

    def export_to_json(self) -> None:
        """Export XML data to JSON format."""
        if not self.error_event_handler():
            return

        self.output_text = self.xml_controller.export_to_json()
        self.result_text_box.setText(str(self.output_text))
        self.result_text_box.show()

    def visualize_network(self) -> None:
        """Visualize network graph."""
        # if not self.graph_controller or not self.graph_controller.xml_data:
        #     QMessageBox.warning(self, "No Data", "Please upload and parse an XML file first.")
        #     return
        #
        # success, nodes, edges, error = self.graph_controller.build_graph()
        #
        # if success:
        #     try:
        #         graph_window = GraphVisualizationWindow(nodes, edges, self.size(), self)
        #         graph_window.show()
        #     except Exception as e:
        #         QMessageBox.critical(self, "Error", f"Failed to open graph visualization:\n{str(e)}")
        # else:
        #     QMessageBox.critical(self, "Graph Build Failed", f"Failed to build graph:\n{error}")

    def show_user_stats(self) -> None:
        """Show user statistics."""
        # if not self.data_controller or not self.data_controller.xml_data:
        #     QMessageBox.warning(self, "No Data", "Please upload and parse an XML file first.")
        #     return
        #
        # success, stats, error = self.data_controller.calculate_statistics()
        #
        # if success:
        #
        #     stats_text = (
        #         f"User Statistics:\n\n"
        #         f"Total Users: {stats.get('total_users', 0)}\n"
        #         f"Total Posts: {stats.get('total_posts', 0)}\n"
        #         f"Total Followers: {stats.get('total_followers', 0)}\n"
        #         f"Total Following: {stats.get('total_following', 0)}\n"
        #         f"Average Followers: {stats.get('avg_followers', 0):.2f}\n"
        #         f"Average Posts: {stats.get('avg_posts', 0):.2f}"
        #     )
        #     QMessageBox.information(self, "User Statistics", stats_text)
        # else:
        #     QMessageBox.critical(self, "Statistics Failed", f"Failed to calculate statistics:\n{error}")

    def search(self) -> None:
        """
        Opens a larger pop-up window with an input field,
        an output display area, and search buttons.
        """
        # 1. Create the Dialog Window
        dialog = QDialog(self)
        dialog.setWindowTitle("Search")
        dialog.setFixedSize(600, 450)  # Increased size

        # Apply the dark theme (updated to include QTextEdit styling)
        dialog.setStyleSheet("""
            QDialog {
                background-color: rgb(20, 35, 55);
                border: 2px solid rgba(100, 150, 200, 100);
            }
            QLineEdit {
                background-color: rgba(30, 45, 65, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 5px;
                color: white;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: rgba(15, 20, 35, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 5px;
                color: rgba(220, 230, 240, 255);
                padding: 10px;
                font-size: 13px;
            }
            QPushButton {
                background-color: rgba(40, 70, 110, 180);
                border: 1px solid rgba(80, 120, 180, 150);
                border-radius: 5px;
                color: white;
                padding: 6px 15px;
            }
            QPushButton:hover {
                background-color: rgba(60, 90, 130, 200);
            }
        """)

        # 2. Setup Layouts
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 3. Input Area
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter keyword to search...")
        layout.addWidget(search_input)

        # 4. Output Area (New Addition)
        result_area = QTextEdit()
        result_area.setReadOnly(True)
        result_area.setPlaceholderText("Search results will appear here...")
        layout.addWidget(result_area)

        # 5. Buttons Area (Bottom Right)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()  # Pushes buttons to the right
        btn_layout.setSpacing(10)  # Gap between buttons

        btn_topic = QPushButton("Search in Topic")
        btn_post = QPushButton("Search in Post")

        btn_layout.addWidget(btn_topic)
        btn_layout.addWidget(btn_post)

        layout.addLayout(btn_layout)

        # 6. Define Internal Helper Functions
        def on_search_topic():
            text = search_input.text().strip()
            if text:
                # Clear previous results
                result_area.clear()
                result_area.append(f"Searching for '{text}' in Topics...\n\n")
                # Call the main class function
                result = self.search_in_post(text, Type='topic')
                for i in range(len(result)):
                    result_area.append(result[i] + '\n\n')

        def on_search_post():
            text = search_input.text().strip()
            if text:
                result_area.clear()
                result_area.append(f"Searching for '{text}' in Posts...\n")

                result = self.search_in_post(text, Type='word')
                for i in range(len(result)):
                    result_area.append(result[i] + '\n')

        # 7. Connect Signals
        btn_topic.clicked.connect(on_search_topic)
        btn_post.clicked.connect(on_search_post)

        # 8. Execute the Dialog
        dialog.exec()

    def search_in_post(self, keyword: str, Type: str) -> Optional[List[str]]:
        """Placeholder logic for searching within topics."""
        # if Type =='word':
        #     return self.data_controller.search_in_posts(word = keyword)
        # else:
        #     return self.data_controller.search_in_posts(topic = keyword)
