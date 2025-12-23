"""
Enhanced Graph Visualization Window - Complete implementation for social network visualization
Supports multiple layout algorithms, interactive features, and image export
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QComboBox, QSpinBox, QCheckBox,
                               QGroupBox, QFileDialog, QMessageBox, QTabWidget, QSizePolicy,
                               QListWidget, QListWidgetItem)
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use('QtAgg')


class GraphVisualizationWindow(QWidget):
    """
    Advanced window for visualizing social network graphs.
    Features:
    - Multiple layout algorithms (spring, circular, shell, kamada-kawai)
    - Interactive controls for customization
    - Node size based on followers/influence
    - Color coding for different user types
    - Export to various image formats
    - Network statistics display
    """

    def __init__(self, nodes, edges, main_window_size, parent=None):
        super().__init__(parent)
        self.nodes = nodes  # {user_id: user_name}
        self.edges = edges  # [(from_id, to_id)] where from_id follows to_id
        self.main_window_size = main_window_size

        # Graph settings
        self.current_layout = "circular"
        self.show_labels = True
        self.show_node_size_by_influence = True
        self.node_color_scheme = "influence"
        self.edge_width = 2.0
        self.node_base_size = 800

        # Track selected users for highlighting
        self.selected_users = set()
        self.selected_mutual_followers = set()
        # Suggested follow targets (highlighted in graph)
        self.suggested_users = set()

        # Graph and metrics should be provided by the controller
        # They are stored separately here for visualization purposes
        self.graph = None
        self.metrics = {
            'num_nodes': 0,
            'num_edges': 0,
            'density': 0,
            'avg_in_degree': 0,
            'avg_out_degree': 0,
            'in_degrees': {},
            'out_degrees': {}
        }
        self.info_label = None

        self.setup_ui()
        # Set graph data after UI is created so info_label exists
        self.set_graph_data(nodes, edges)

    def set_graph_data(self, nodes: dict, edges: list, G=None, metrics=None) -> None:
        """Set graph data for visualization. Can optionally use precomputed graph and metrics from controller."""
        self.nodes = nodes
        self.edges = edges

        if G is not None and metrics is not None:
            # Use precomputed graph and metrics from controller
            self.graph = G
            self.metrics = metrics
        else:
            # Build locally if not provided
            self._build_local_graph()

        # Update info label with new metrics
        self._update_info_label()
        # Update statistics display
        self._update_statistics_group()
        # Update statistics display
        self._update_statistics_group()
        # Refresh selectors and textual labels according to current label mode
        try:
            self._refresh_user_selectors()
        except Exception:
            pass
        try:
            # Ensure instruction texts and groups are updated
            self.on_label_mode_changed()
        except Exception:
            # Fallback to drawing if handler fails
            self.draw_graph()

    def _update_info_label(self) -> None:
        """Update the title bar info label with current metrics."""
        if self.info_label is not None:
            self.info_label.setText(
                f"Nodes: {self.metrics.get('num_nodes', 0)} | "
                f"Edges: {self.metrics.get('num_edges', 0)} | "
                f"Density: {self.metrics.get('density', 0):.3f}"
            )

    def _build_local_graph(self) -> None:
        """Build a local NetworkX graph for visualization if not provided by controller."""
        import networkx as nx
        import numpy as np

        G = nx.DiGraph()

        # Add all nodes
        for node_id, node_name in self.nodes.items():
            G.add_node(str(node_id), name=node_name)

        # Add all edges
        for from_id, to_id in self.edges:
            if str(from_id) in G.nodes() and str(to_id) in G.nodes():
                G.add_edge(str(from_id), str(to_id))

        self.graph = G
        self._calculate_local_metrics()

    def _calculate_local_metrics(self) -> None:
        """Calculate metrics locally if not provided by controller."""
        import networkx as nx
        import numpy as np

        if self.graph is None:
            self.metrics = {}
            return

        metrics = {}

        # Basic metrics
        metrics['num_nodes'] = self.graph.number_of_nodes()
        metrics['num_edges'] = self.graph.number_of_edges()
        metrics['density'] = nx.density(self.graph)

        # Degree metrics
        in_degrees = dict(self.graph.in_degree())
        out_degrees = dict(self.graph.out_degree())

        metrics['avg_in_degree'] = np.mean(list(in_degrees.values())) if in_degrees else 0
        metrics['avg_out_degree'] = np.mean(list(out_degrees.values())) if out_degrees else 0

        # Most influential
        if in_degrees:
            most_influential_id = max(in_degrees, key=in_degrees.get)
            metrics['most_influential'] = {
                'id': most_influential_id,
                'name': self.nodes.get(most_influential_id, 'Unknown'),
                'followers': in_degrees[most_influential_id]
            }

        # Most active
        if out_degrees:
            most_active_id = max(out_degrees, key=out_degrees.get)
            metrics['most_active'] = {
                'id': most_active_id,
                'name': self.nodes.get(most_active_id, 'Unknown'),
                'following': out_degrees[most_active_id]
            }

        metrics['in_degrees'] = in_degrees
        metrics['out_degrees'] = out_degrees

        self.metrics = metrics

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("SocialX Graph Visualization - Advanced")
        self.resize(self.main_window_size)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side - Graph canvas
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        graph_layout.setSpacing(0)

        # Title bar
        title_bar = self._create_title_bar()
        graph_layout.addWidget(title_bar)

        # Matplotlib canvas
        self.figure = Figure(figsize=(12, 8), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)

        # Right side - Control panel
        control_panel = self._create_control_panel()

        # Add to main layout
        main_layout.addWidget(graph_container, 5)
        main_layout.addWidget(control_panel, 2)

    def _create_title_bar(self):
        """Create the title bar with graph information."""
        title_bar = QWidget()
        title_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 60, 90, 255),
                    stop:1 rgba(40, 80, 120, 255));
                border-bottom: 2px solid rgba(100, 150, 200, 255);
            }
        """)
        title_bar.setFixedHeight(60)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 10, 20, 10)

        # Title and info
        title_label = QLabel("🔗 SocialX Graph Visualization")
        title_label.setStyleSheet("""
            background-color: transparent;
            color: rgba(200, 220, 240, 255);
            font-size: 18px;
            font-weight: bold;
        """)

        self.info_label = QLabel(
            f"Nodes: {self.metrics.get('num_nodes', 0)} | "
            f"Edges: {self.metrics.get('num_edges', 0)} | "
            f"Density: {self.metrics.get('density', 0):.3f}"
        )
        self.info_label.setStyleSheet("""
            background-color: transparent;  
            color: rgba(200, 220, 240, 255);
            font-size: 18px;
            font-weight: bold;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.info_label)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(232, 17, 35, 200);
                border-radius: 3px;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        return title_bar
    
    def _create_control_panel(self):
        """Create the control panel with all settings."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(25, 35, 50, 255),
                    stop:1 rgba(20, 30, 45, 255));
            }
            QGroupBox {
                color: rgba(150, 200, 255, 255);
                font-weight: bold;
                font-size: 20px;
                border: 1px solid rgba(80, 120, 160, 150);
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: rgba(200, 220, 240, 255);
                font-size: 18px;
                font-weight: bold;
            }
            QSpinBox {
                background-color: rgba(40, 60, 80, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 4px;
                color: white;
                padding-left: 6px;
                padding-right: 26px;
                font-size: 16px;
                font-weight: bold;
            }  
            QComboBox{
                background-color: rgba(40, 60, 80, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 4px;
                color: white;
                padding-left: 5px;
                padding-right: 25px;  
                min-height: 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QComboBox::drop-down{
                border: none;   
                background: qlineargradient(
                    x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(60, 80, 100, 200),
                    stop:1 rgba(120, 160, 200, 220)
                );
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid rgba(80, 120, 160, 120);
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 2px;
                background-color: white;  
            }
            QComboBox QAbstractItemView {
                background-color: rgba(40, 60, 80, 200);
                color: rgba(200, 220, 240, 255);
                selection-background-color: rgba(40, 100, 180, 200);
                border: 1px solid rgba(80, 120, 160, 120);
            }
            QPushButton {
                background: rgba(40, 100, 180, 200);
                border: 1px solid rgba(80, 150, 220, 180);
                border-radius: 5px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: rgba(60, 120, 200, 230);
            }
            QPushButton:pressed {
                background: rgba(30, 80, 150, 200);
            }
            QCheckBox {
                color: rgba(200, 220, 240, 255);
                font-size: 16px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 3px;
                background: rgba(40, 60, 80, 180);
            }
            QCheckBox::indicator:checked {
                background: rgba(40, 100, 180, 255);
            }
            QTabWidget {
                background: transparent;
            }
            QTabBar {
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(40, 60, 80, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-bottom: none;
                border-radius: 4px 4px 0px 0px;
                color: rgba(150, 200, 255, 255);
                padding: 8px 15px;
                margin-right: 2px;
                font-size: 16px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: rgba(40, 100, 180, 200);
                border: 1px solid rgba(80, 150, 220, 180);
            }
            QTabBar::tab:hover:!selected {
                background: rgba(50, 80, 120, 200);
            }
            QTabWidget::pane {
                border: 1px solid rgba(80, 120, 160, 150);
            }
        """)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(15)
        
        # Create tabs for different panels
        tabs = QTabWidget()
        
        # Tab 1: Settings
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(15)
        
        # Layout settings
        layout_group = self._create_layout_group()
        settings_layout.addWidget(layout_group)
        
        # Visualization settings
        viz_group = self._create_visualization_group()
        settings_layout.addWidget(viz_group)
        
        settings_layout.addStretch()
        tabs.addTab(settings_widget, "⚙️ Settings")
        
        # Tab 2: Analysis
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setSpacing(15)
        
        # Mutual Followers
        mutual_group = self._create_mutual_followers_group()
        analysis_layout.addWidget(mutual_group)

        # Follow Suggestions
        suggestions_group = self._create_follow_suggestions_group()
        analysis_layout.addWidget(suggestions_group)
        
        analysis_layout.addStretch()
        tabs.addTab(analysis_widget, "📊 Analysis")
        
        # Tab 3: Statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(15)
        
        # Network statistics
        stats_group = self._create_statistics_group()
        stats_layout.addWidget(stats_group)
        
        stats_layout.addStretch()
        tabs.addTab(stats_widget, "📈 Statistics")
        
        panel_layout.addWidget(tabs)
        
        # Export button
        export_btn = QPushButton("💾 Export Graph as Image")
        export_btn.clicked.connect(self.export_graph)
        panel_layout.addWidget(export_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Redraw Graph")
        refresh_btn.clicked.connect(self.draw_graph)
        panel_layout.addWidget(refresh_btn)
        
        return panel
    
    def _create_layout_group(self):
        """Create layout algorithm selection group."""
        group = QGroupBox("Layout Algorithm")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        label = QLabel("Choose layout:")
        layout.addWidget(label)
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems([
            "Spring Layout (Force-directed)",
            "Circular Layout",
            "Shell Layout",
            "Kamada-Kawai Layout",
            "Random Layout"
        ])
        self.layout_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.layout_combo.setCurrentIndex(1)  # Default to Circular Layout
        self.layout_combo.currentIndexChanged.connect(self.on_layout_changed)
        layout.addWidget(self.layout_combo)
        
        return group
    
    def _create_visualization_group(self):
        """Create visualization settings group."""
        group = QGroupBox("Visualization Settings")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Label display mode: None / Names / IDs
        labels_mode_label = QLabel("Modes:")
        labels_mode_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(labels_mode_label)

        self.labels_mode_combo = QComboBox()
        self.labels_mode_combo.addItems(["Names", "IDs"])
        self.labels_mode_combo.setCurrentIndex(1)  # Default to IDs
        self.labels_mode_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.labels_mode_combo.currentIndexChanged.connect(self.on_label_mode_changed)
        layout.addWidget(self.labels_mode_combo)
        # Node size by influence
        self.influence_checkbox = QCheckBox("Size by Influence (Followers)")
        self.influence_checkbox.setChecked(True)
        self.influence_checkbox.stateChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.influence_checkbox)
        
        # Node base size
        size_label = QLabel("Base Node Size:")
        layout.addWidget(size_label)

        spin_container = QWidget()
        spin_layout = QHBoxLayout(spin_container)
        spin_layout.setContentsMargins(0, 0, 0, 0)
        spin_layout.setSpacing(3)

        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(100, 2000)
        self.size_spinbox.setSingleStep(100)
        self.size_spinbox.setValue(500)
        self.size_spinbox.setFixedSize(300, 30)
        self.size_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        self.size_spinbox.valueChanged.connect(self.draw_graph)

        btn_up = QPushButton("▲")
        btn_up.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(60, 80, 100, 200);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 4px;
                padding: 0px;
                color: rgba(200, 220, 240, 255);
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: rgba(80, 100, 120, 220);
            }
            
            QPushButton:pressed {
                background-color: rgba(40, 100, 180, 255);
            }
            """
        )
        btn_down = QPushButton("▼")
        btn_down.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(60, 80, 100, 200);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 4px;
                padding: 0px;
                color: rgba(200, 220, 240, 255);
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: rgba(80, 100, 120, 220);
            }

            QPushButton:pressed {
                background-color: rgba(40, 100, 180, 255);
            }
            """
        )

        btn_up.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_down.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        btn_up.clicked.connect(
            lambda: self.size_spinbox.setValue(
                self.size_spinbox.value() + self.size_spinbox.singleStep()
            )
        )

        btn_down.clicked.connect(
            lambda: self.size_spinbox.setValue(
                self.size_spinbox.value() - self.size_spinbox.singleStep()
            )
        )

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(2)

        btn_layout.addWidget(btn_up)
        btn_layout.addWidget(btn_down)

        spin_layout.addWidget(self.size_spinbox)
        spin_layout.addLayout(btn_layout)

        layout.addWidget(spin_container)

        # Color scheme
        color_label = QLabel("Color Scheme:")
        layout.addWidget(color_label)
        
        self.color_combo = QComboBox()
        self.color_combo.addItems([
            "By Influence (Blue gradient)",
            "By Activity (Green gradient)",
            "Uniform (Steel Blue)",
            "Random Colors"
        ])
        self.color_combo.setCurrentIndex(2)  # Default to Uniform
        self.color_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.color_combo.currentIndexChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.color_combo)
        
        # Font color for labels
        font_color_label = QLabel("Font Color:")
        font_color_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(font_color_label)

        self.font_color_combo = QComboBox()
        self.font_color_combo.addItems(["White","Black","Red", "Blue", "Green", "Gray"])
        # Default to White
        self.font_color_combo.setCurrentIndex(0)
        self.font_color_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.font_color_combo.currentIndexChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.font_color_combo)
        
        return group
    
    def _create_statistics_group(self):
        """Create network statistics display group."""
        group = QGroupBox("Network Statistics")
        self.stats_layout = QVBoxLayout(group)
        self.stats_layout.setSpacing(8)
        
        # Create label to hold statistics
        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("font-size: 16px; line-height: 2;")
        self.stats_layout.addWidget(self.stats_label)
        
        return group
    
    def _update_statistics_group(self):
        """Update the statistics group with current metrics data."""
        if not hasattr(self, 'stats_label'):
            return
        
        # Build statistics text from metrics
        stats_text = f"""
<b><b>Network Metrics:</b></b><br>
\t• <b>Nodes</b>: {self.metrics.get('num_nodes', 0)}<br>
\t• <b>Edges</b>: {self.metrics.get('num_edges', 0)}<br>
\t• <b>Density</b>: {self.metrics.get('density', 0):.3f}<br>
\t• <b>Avg Followers</b>: {self.metrics.get('avg_in_degree', 0):.1f}<br>
\t• <b>Avg Following</b>: {self.metrics.get('avg_out_degree', 0):.1f}<br>
        """
        
        if 'most_influential' in self.metrics and self.metrics['most_influential']:
            inf_data = self.metrics['most_influential']
            # Defensive check: if it's a dict (old format), wrap in list
            if isinstance(inf_data, dict):
                inf_list = [inf_data]
            else:
                inf_list = inf_data
            
            if inf_list:
                followers_count = inf_list[0]['followers']
                stats_text += f"<br><b>Most Influential ({followers_count} followers):</b><br>"
                
                mode = getattr(self, 'labels_mode_combo', None).currentText() if hasattr(self, 'labels_mode_combo') else 'Names'
                
                for inf in inf_list:
                    display_inf = (f"User ID: {inf['id']}" if mode == 'IDs' else inf['name'])
                    stats_text += f"\t• {display_inf}<br>"
        
        if 'most_active' in self.metrics and self.metrics['most_active']:
            act_data = self.metrics['most_active']
            # Defensive check: if it's a dict (old format), wrap in list
            if isinstance(act_data, dict):
                act_list = [act_data]
            else:
                act_list = act_data

            if act_list:
                following_count = act_list[0]['following']
                stats_text += f"<br><b>Most Active ({following_count} following):</b><br>"
                
                mode = getattr(self, 'labels_mode_combo', None).currentText() if hasattr(self, 'labels_mode_combo') else 'Names'
                
                for act in act_list:
                    display_act = (f"User ID: {act['id']}" if mode == 'IDs' else act['name'])
                    stats_text += f"\t• {display_act}<br>"
        
        self.stats_label.setText(stats_text)

    def on_label_mode_changed(self, index=None):
        """Handle label mode changes: refresh selectors, update label texts, and redraw."""
        try:
            self._refresh_user_selectors()
        except Exception:
            pass
        # Update textual displays to match mode
        try:
            self._update_statistics_group()
        except Exception:
            pass
        # Clear suggestions when switching label mode to avoid stale entries/highlights
        try:
            if hasattr(self, 'suggestions_list'):
                self.suggestions_list.clear()
        except Exception:
            pass
        # Reset highlight color selection when modes change
        try:
            if hasattr(self, 'suggestions_color_combo'):
                self.suggestions_color_combo.blockSignals(True)
                self.suggestions_color_combo.setCurrentIndex(-1)
        finally:
            if hasattr(self, 'suggestions_color_combo'):
                self.suggestions_color_combo.blockSignals(False)
        # also clear suggested_users set used for highlighting
        try:
            self.suggested_users = set()
        except Exception:
            pass

        if hasattr(self, 'mutual_label') and "No results yet" not in self.mutual_label.text():
            try:
                self.find_mutual_followers()
            except Exception:
                pass
        
        self.draw_graph()

    def _refresh_user_selectors(self):
        """Update combo boxes and selector labels to show IDs or Names depending on label mode."""
        mode = getattr(self, 'labels_mode_combo', None).currentText() if hasattr(self, 'labels_mode_combo') else 'Names'

        # Build items
        ids = [str(k) for k in self.nodes.keys()] if self.nodes else []
        names = [v for v in self.nodes.values()] if self.nodes else []
        items = ids if mode == 'IDs' else names

        # Update mutual selectors
        if hasattr(self, 'mutual_user1_combo'):
            try:
                self.mutual_user1_combo.blockSignals(True)
                current_idx = self.mutual_user1_combo.currentIndex()
                self.mutual_user1_combo.clear()
                self.mutual_user1_combo.addItems(items)
                
                # Restore index if valid, otherwise default
                if current_idx >= 0 and current_idx < len(items):
                     self.mutual_user1_combo.setCurrentIndex(current_idx)
                else:
                     self.mutual_user1_combo.setCurrentIndex(0 if len(items) > 0 else -1)
            finally:
                self.mutual_user1_combo.blockSignals(False)

        if hasattr(self, 'mutual_user2_combo'):
            try:
                self.mutual_user2_combo.blockSignals(True)
                current_idx = self.mutual_user2_combo.currentIndex()
                self.mutual_user2_combo.clear()
                self.mutual_user2_combo.addItems(items)
                
                # Restore index if valid, otherwise default
                if current_idx >= 0 and current_idx < len(items):
                     self.mutual_user2_combo.setCurrentIndex(current_idx)
                else:
                     self.mutual_user2_combo.setCurrentIndex(1 if len(items) > 1 else (0 if len(items) == 1 else -1))
            finally:
                self.mutual_user2_combo.blockSignals(False)

        # Update suggestions selector (keep placeholder behavior)
        if hasattr(self, 'suggestions_user_combo'):
            try:
                self.suggestions_user_combo.blockSignals(True)
                self.suggestions_user_combo.clear()
                self.suggestions_user_combo.addItems(items)
                self.suggestions_user_combo.setCurrentIndex(-1)
                ph = 'Select a user ID' if mode == 'IDs' else 'Select a user'
                self.suggestions_user_combo.setPlaceholderText(ph)
            finally:
                self.suggestions_user_combo.blockSignals(False)

        # Update label text widgets
        if hasattr(self, 'mutual_user1_label'):
            self.mutual_user1_label.setText('User ID 1:' if mode == 'IDs' else 'User 1:')
        if hasattr(self, 'mutual_user2_label'):
            self.mutual_user2_label.setText('User ID 2:' if mode == 'IDs' else 'User 2:')
        if hasattr(self, 'suggestions_user_label'):
            self.suggestions_user_label.setText('User ID:' if mode == 'IDs' else 'User:')
        # Update instruction texts and group titles to reflect 'User ID' when in IDs mode
        if hasattr(self, 'mutual_instructions'):
            self.mutual_instructions.setText('Select user IDs to find mutual followers:' if mode == 'IDs' else 'Select users to find mutual followers:')
        if hasattr(self, 'suggestions_instructions'):
            self.suggestions_instructions.setText('Select a user id to see follow suggestions:' if mode == 'IDs' else 'Select a user to see follow suggestions:')

    def _create_mutual_followers_group(self):
        """Create group for mutual followers analysis."""
        group = QGroupBox("Mutual Followers Analysis")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Instructions
        self.mutual_instructions = QLabel("Select users to find mutual followers:")
        self.mutual_instructions.setStyleSheet("font-size: 14px; color: rgba(150, 180, 220, 255);")
        layout.addWidget(self.mutual_instructions)
        
        # User selection combo boxes (show 2 users) - respect label mode
        mode = getattr(self, 'labels_mode_combo', None).currentText() if hasattr(self, 'labels_mode_combo') else 'Names'
        if self.nodes:
            users_list = sorted([str(k) for k in self.nodes.keys()]) if mode == 'IDs' else sorted(list(self.nodes.values()))
        else:
            users_list = []
        
        # User 1
        user1_layout = QHBoxLayout()
        self.mutual_user1_label = QLabel("User 1:")
        self.mutual_user1_label.setStyleSheet("font-size: 18px; line-height: 2;")
        user1_layout.addWidget(self.mutual_user1_label)
        self.mutual_user1_combo = QComboBox()
        self.mutual_user1_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.mutual_user1_combo.addItems(users_list)
        user1_layout.addWidget(self.mutual_user1_combo)
        layout.addLayout(user1_layout)
        
        # User 2
        user2_layout = QHBoxLayout()
        self.mutual_user2_label = QLabel("User 2:")
        self.mutual_user2_label.setStyleSheet("font-size: 18px; line-height: 2;")
        user2_layout.addWidget(self.mutual_user2_label)
        self.mutual_user2_combo = QComboBox()
        self.mutual_user2_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.mutual_user2_combo.addItems(users_list)
        if len(users_list) > 1:
            self.mutual_user2_combo.setCurrentIndex(1)
        user2_layout.addWidget(self.mutual_user2_combo)
        layout.addLayout(user2_layout)
        
        # Find mutual followers button
        find_mutual_btn = QPushButton("🔍 Find Mutual Followers")
        find_mutual_btn.clicked.connect(self.find_mutual_followers)
        layout.addWidget(find_mutual_btn)
        
        # Highlight toggle
        self.mutual_highlight_check = QCheckBox("Highlight on Graph")
        self.mutual_highlight_check.setChecked(True)
        self.mutual_highlight_check.setStyleSheet("font-size: 14px; color: rgba(150, 180, 220, 255);")
        self.mutual_highlight_check.stateChanged.connect(self.draw_graph)
        layout.addWidget(self.mutual_highlight_check)
        
        # Results display
        self.mutual_label = QLabel("No results yet")
        self.mutual_label.setWordWrap(True)
        self.mutual_label.setStyleSheet("font-size: 16px; line-height: 2;")
        layout.addWidget(self.mutual_label)
        
        return group


    def _create_follow_suggestions_group(self):
        """Create group that suggests users to follow for a selected user.
        Suggestion logic: gather users followed by the selected user's followers
        (i.e., people that many of your followers also follow). Excludes the
        user themself and users the user already follows.
        """
        group = QGroupBox("Follow Suggestions")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        self.suggestions_instructions = QLabel("Select a user to see follow suggestions:")
        self.suggestions_instructions.setStyleSheet("font-size: 14px; color: rgba(150, 180, 220, 255);")
        layout.addWidget(self.suggestions_instructions)

        mode = getattr(self, 'labels_mode_combo', None).currentText() if hasattr(self, 'labels_mode_combo') else 'Names'
        if self.nodes:
            users_list = sorted([str(k) for k in self.nodes.keys()]) if mode == 'IDs' else sorted(list(self.nodes.values()))
        else:
            users_list = []

        user_layout = QHBoxLayout()
        self.suggestions_user_label = QLabel("User:")
        self.suggestions_user_label.setStyleSheet("font-size: 18px; line-height: 2;")
        user_layout.addWidget(self.suggestions_user_label)

        self.suggestions_user_combo = QComboBox()
        self.suggestions_user_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.suggestions_user_combo.addItems(users_list)
        
        # Proper placeholder
        self.suggestions_user_combo.setPlaceholderText("Select a user")
        self.suggestions_user_combo.setCurrentIndex(-1)
        self.suggestions_user_combo.currentIndexChanged.connect(self.find_follow_suggestions)
        user_layout.addWidget(self.suggestions_user_combo)
        layout.addLayout(user_layout)
        # Highlight color chooser for suggestions
        color_layout = QHBoxLayout()
        color_label = QLabel("Highlight color:")
        color_label.setStyleSheet("font-size: 16px; line-height: 2;")
        color_layout.addWidget(color_label)

        self.suggestions_color_combo = QComboBox()
        self.suggestions_color_combo.addItems(["Orange", "Purple", "Cyan"])
        self.suggestions_color_combo.setPlaceholderText("Select Color")
        self.suggestions_color_combo.setCurrentIndex(-1)  # Default None
        self.suggestions_color_combo.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )
        self.suggestions_color_combo.currentIndexChanged.connect(self.draw_graph)
        color_layout.addWidget(self.suggestions_color_combo)
        layout.addLayout(color_layout)

        # Use a list widget so long suggestion lists are scrollable and names
        # are shown in full instead of being clipped in a QLabel.
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(180)
        layout.addWidget(self.suggestions_list)

        return group


    def find_follow_suggestions(self):
        """Compute and display follow suggestions for the selected user.

        Algorithm:
        - Let U be the selected user.
        - Let F = followers(U) (predecessors in the DiGraph).
        - For each f in F, collect S_f = successors(f) (who f follows).
        - Candidate set C = union of all S_f.
        - Exclude U and any user already followed by U (successors(U)).
        - Score candidates by how many f in F follow them (frequency).
        - Sort by score desc and show top suggestions.
        """
        if not hasattr(self, 'suggestions_user_combo'):
            return

        # If no real user is selected (placeholder shown), clear suggestions
        idx = self.suggestions_user_combo.currentIndex()
        user_name = self.suggestions_user_combo.currentText()
        if idx == -1 or not user_name:
            self.suggestions_list.clear()
            # Reset highlight color when no user is selected
            try:
                if hasattr(self, 'suggestions_color_combo'):
                    self.suggestions_color_combo.blockSignals(True)
                    self.suggestions_color_combo.setCurrentIndex(-1)
            finally:
                if hasattr(self, 'suggestions_color_combo'):
                    self.suggestions_color_combo.blockSignals(False)
            return

        # Determine user id depending on label mode
        mode = getattr(self, 'labels_mode_combo', None).currentText() if hasattr(self, 'labels_mode_combo') else 'Names'
        user_id = None
        if mode == 'IDs':
            user_id = str(user_name)
        else:
            for uid, uname in self.nodes.items():
                if uname == user_name:
                    user_id = str(uid)
                    break

        if user_id is None:
            self.suggestions_list.clear()
            return

        if self.graph is None or user_id not in self.graph:
            self.suggestions_list.clear()
            return

        followers = set(self.graph.predecessors(user_id))

        # Collect candidates and count frequency
        # Use followers-of-followers: for each follower f in followers,
        # consider predecessors(f) (people who follow f) as candidates.
        candidate_counts = {}
        for f in followers:
            for cand in self.graph.predecessors(f):
                candidate_counts[cand] = candidate_counts.get(cand, 0) + 1

        # Exclude the user and users already followed by the user
        already_following = set(self.graph.successors(user_id))
        excluded = already_following | {user_id}

        # Build filtered list
        filtered = [(cand, cnt) for cand, cnt in candidate_counts.items() if cand not in excluded]
        if not filtered:
            self.suggestions_list.clear()
            self.suggestions_list.addItem(QListWidgetItem("No suggestions found"))
            self.suggested_users = set()
            self.draw_graph()
            return

        # Sort by frequency desc
        filtered.sort(key=lambda x: x[1], reverse=True)

        # Build display text (top 10) with robust name resolution
        def _resolve_name(nid):
            if nid in self.nodes:
                return self.nodes[nid]
            for k, v in self.nodes.items():
                if str(k) == str(nid):
                    return v
            return str(nid)

        top = filtered[:10]
        # Populate list widget (show IDs with 'UserID:' prefix if mode==IDs, otherwise names)
        self.suggestions_list.clear()
        suggested_ids = []
        for cand, _ in top:
            if mode == 'IDs':
                display = f"UserID: {cand}"
            else:
                display = _resolve_name(cand)
            self.suggestions_list.addItem(QListWidgetItem(display))
            suggested_ids.append(str(cand))

        # Store suggested ids for highlighting and redraw
        self.suggested_users = set(suggested_ids)
        self.draw_graph()
    
    def find_mutual_followers(self):
        """Find and display mutual followers between selected users."""
        if not hasattr(self, 'mutual_user1_combo'):
            return
        
        # Get selected user names
        user1_name = self.mutual_user1_combo.currentText()
        user2_name = self.mutual_user2_combo.currentText()
        
        if not user1_name or not user2_name:
            self.mutual_label.setText("Please select both users")
            return
        
        # Determine user IDs depending on label mode
        # robustly check mode
        try:
            mode = self.labels_mode_combo.currentText()
        except AttributeError:
            mode = 'Names'

        user1_id = None
        user2_id = None
        if mode == 'IDs':
            user1_id = str(user1_name)
            user2_id = str(user2_name)
        else:
            for uid, uname in self.nodes.items():
                if uname == user1_name:
                    user1_id = uid
                if uname == user2_name:
                    user2_id = uid
        
        if not user1_id or not user2_id:
            self.mutual_label.setText("Selected users not found")
            return
        
        if user1_id == user2_id:
            self.mutual_label.setText("Please select different users")
            return
        
        # Get mutual followers from graph (predecessors that are same for both)
        if self.graph is None:
            self.mutual_label.setText("No graph data available")
            return
        
        user1_followers = set(self.graph.predecessors(user1_id)) if user1_id in self.graph else set()
        user2_followers = set(self.graph.predecessors(user2_id)) if user2_id in self.graph else set()
        
        mutual_followers = user1_followers & user2_followers
        
        # Store selected users for highlighting in graph
        self.selected_users = {user1_id, user2_id}
        self.selected_mutual_followers = mutual_followers
        
        # Format results - show IDs if mode==IDs
        display_user1 = (f"User ID: {user1_id}" if mode == 'IDs' else user1_name)
        display_user2 = (f"User ID: {user2_id}" if mode == 'IDs' else user2_name)
        result_text = f"<b>Mutual Followers between {display_user1} and {display_user2}:</b><br>"

        if mutual_followers:
            result_text += f"<br>Found {len(mutual_followers)} mutual follower(s):<br>"
            for follower_id in sorted(mutual_followers):
                # Ensure we show ID if mode is IDs, ignoring node name
                if mode == 'IDs':
                    follower_display = f"User ID: {follower_id}"
                else:
                    follower_display = self.nodes.get(follower_id, follower_id)
                result_text += f"• {follower_display}<br>"
        else:
            result_text += "<br>No mutual followers found"
        
        self.mutual_label.setText(result_text)
        
        # Redraw graph to highlight selected users
        self.draw_graph()
    
    def on_layout_changed(self, index):
        """Handle layout algorithm change."""
        layout_map = {
            0: "spring",
            1: "circular",
            2: "shell",
            3: "kamada_kawai",
            4: "random"
        }
        self.current_layout = layout_map[index]
        self.draw_graph()
    
    def get_layout_positions(self):
        """Calculate node positions based on selected layout algorithm."""
        if self.graph.number_of_nodes() == 0:
            return {}
        
        try:
            if self.current_layout == "spring":
                pos = nx.spring_layout(self.graph, k=1.5, iterations=50, seed=42)
            elif self.current_layout == "circular":
                pos = nx.circular_layout(self.graph)
            elif self.current_layout == "shell":
                pos = nx.shell_layout(self.graph)
            elif self.current_layout == "kamada_kawai":
                pos = nx.kamada_kawai_layout(self.graph)
            elif self.current_layout == "random":
                pos = nx.random_layout(self.graph, seed=42)
            else:
                pos = nx.spring_layout(self.graph, k=1.5, iterations=50, seed=42)
            return pos
        except:
            # Fallback to circular if layout fails
            return nx.circular_layout(self.graph)
    
    def get_node_sizes(self):
        """Calculate node sizes based on influence (followers)."""
        if not self.influence_checkbox.isChecked():
            return [self.size_spinbox.value()] * self.graph.number_of_nodes()
        
        in_degrees = self.metrics.get('in_degrees', {})
        base_size = self.size_spinbox.value()
        
        # Calculate sizes based on followers (in-degree)
        sizes = []
        max_followers = max(in_degrees.values()) if in_degrees.values() else 1
        
        for node in self.graph.nodes():
            followers = in_degrees.get(node, 0)
            # Scale size: minimum 50% of base, maximum 200% of base
            scale = 0.5 + 1.5 * (followers / max_followers) if max_followers > 0 else 1
            sizes.append(base_size * scale)
        
        return sizes
    
    def get_node_colors(self):
        """Calculate node colors based on selected scheme."""
        scheme_index = self.color_combo.currentIndex()
        
        if scheme_index == 0:  # By Influence (Blue gradient)
            in_degrees = self.metrics.get('in_degrees', {})
            max_influence = max(in_degrees.values()) if in_degrees.values() else 1
            # Use 0.3 to 1.0 range for better visibility (avoid very light colors)
            colors = [0.3 + 0.7 * (in_degrees.get(node, 0) / max_influence) for node in self.graph.nodes()]
            return colors
        
        elif scheme_index == 1:  # By Activity (Green gradient)
            out_degrees = self.metrics.get('out_degrees', {})
            max_activity = max(out_degrees.values()) if out_degrees.values() else 1
            # Use 0.3 to 1.0 range for better visibility (avoid very light colors)
            colors = [0.3 + 0.7 * (out_degrees.get(node, 0) / max_activity) for node in self.graph.nodes()]
            return colors
        
        elif scheme_index == 2:  # Uniform
            return ['#4A90D9'] * self.graph.number_of_nodes()
        
        else:  # Random colors
            np.random.seed(42)
            return np.random.rand(self.graph.number_of_nodes())
    
    def draw_graph(self):
        """Draw the network graph with current settings."""
        # Clear the figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if self.graph is None or self.graph.number_of_nodes() == 0:
            ax.text(0.5, 0.5, 'No nodes to display',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=16, color='gray')
            self.canvas.draw()
            return
        
        # Get layout positions
        pos = self.get_layout_positions()
        
        # Get node sizes and colors
        node_sizes = self.get_node_sizes()
        node_colors = self.get_node_colors()
        
        # Determine color map
        scheme_index = self.color_combo.currentIndex()
        if scheme_index == 0:
            cmap = plt.cm.Blues
            vmin, vmax = 0.3, 1
        elif scheme_index == 1:
            cmap = plt.cm.Greens
            vmin, vmax = 0.3, 1
        else:
            cmap = None
            vmin, vmax = None, None
        
        # Calculate margin based on node sizes (to make arrows end at node edge)
        # The margin is approximately sqrt(node_size) / 2 for circular nodes
        avg_node_size = sum(node_sizes) / len(node_sizes) if node_sizes else 500
        node_margin = (avg_node_size ** 0.5) / 2
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph, pos, ax=ax,
            arrows=True,
            arrowsize=20,
            arrowstyle='-|>',
            edge_color='#555555',
            width=self.edge_width,
            alpha=0.7,
            connectionstyle='arc3,rad=0.1',
            node_size=node_sizes,
            min_source_margin=node_margin,
            min_target_margin=node_margin
        )
        
        # Draw nodes
        if cmap:
            nx.draw_networkx_nodes(
                self.graph, pos, ax=ax,
                node_color=node_colors,
                node_size=node_sizes,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                alpha=1.0,
                edgecolors='#333333',
                linewidths=2.5
            )
        else:
            nx.draw_networkx_nodes(
                self.graph, pos, ax=ax,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=1.0,
                edgecolors='#333333',
                linewidths=2.5
            )
        
        # Highlight selected users if any (and enabled)
        should_highlight_mutual = True
        if hasattr(self, 'mutual_highlight_check'):
             should_highlight_mutual = self.mutual_highlight_check.isChecked()

        if self.selected_users and should_highlight_mutual:
            selected_nodes = [n for n in self.selected_users if n in self.graph.nodes()]
            if selected_nodes:
                # Use the same size as the actual node
                all_nodes_list = list(self.graph.nodes())
                selected_sizes = [node_sizes[all_nodes_list.index(n)] for n in selected_nodes]
                nx.draw_networkx_nodes(
                    self.graph.subgraph(selected_nodes), pos, ax=ax,
                    node_color='#FF6B6B',
                    node_size=selected_sizes,
                    alpha=1.0,
                    edgecolors='#333333',
                    linewidths=3
                )
        
        # Highlight mutual followers (and enabled)
        if self.selected_mutual_followers and should_highlight_mutual:
            mutual_nodes = [n for n in self.selected_mutual_followers if n in self.graph.nodes()]
            if mutual_nodes:
                # Use the same size as the actual node
                all_nodes_list = list(self.graph.nodes())
                mutual_sizes = [node_sizes[all_nodes_list.index(n)] for n in mutual_nodes]
                nx.draw_networkx_nodes(
                    self.graph.subgraph(mutual_nodes), pos, ax=ax,
                    node_color='#50C878',
                    node_size=mutual_sizes,
                    alpha=1.0,
                    edgecolors='#333333',
                    linewidths=3
                )

        # Highlight follow suggestions (color selectable)
        if hasattr(self, 'suggested_users') and self.suggested_users:
            # Determine color from combo (if present)
            color_name = None
            if hasattr(self, 'suggestions_color_combo'):
                color_name = self.suggestions_color_combo.currentText()

            color_map = {
                'Orange': '#FFA500',
                'Purple': '#A020F0',
                'Cyan': '#00CED1'
            }

            if color_name is None or color_name == 'None':
                highlight_color = None
            else:
                highlight_color = color_map.get(color_name, '#FFA500')

            if highlight_color:
                suggested_nodes = [n for n in self.suggested_users if n in self.graph.nodes()]
                if suggested_nodes:
                    all_nodes_list = list(self.graph.nodes())
                    suggested_sizes = [node_sizes[all_nodes_list.index(n)] for n in suggested_nodes]
                    nx.draw_networkx_nodes(
                        self.graph.subgraph(suggested_nodes), pos, ax=ax,
                        node_color=highlight_color,
                        node_size=suggested_sizes,
                        alpha=1.0,
                        edgecolors='#333333',
                        linewidths=3
                    )
        
        # Draw labels according to selected label mode (None / Names / IDs)
        labels_mode = getattr(self, 'labels_mode_combo', None)
        mode = labels_mode.currentText() if labels_mode is not None else 'Names'

        if mode == 'IDs':
            labels = {node: node for node in self.graph.nodes()}
        else:
            labels = {node: self.nodes.get(node, node) for node in self.graph.nodes()}
        # Determine font color from combo if present
        font_color_name = None
        if hasattr(self, 'font_color_combo'):
            font_color_name = self.font_color_combo.currentText()

        color_map = {
            'Black': 'black',
            'White': 'white',
            'Red': 'red',
            'Blue': 'blue',
            'Green': 'green',
            'Gray': 'gray'
        }

        font_color = color_map.get(font_color_name, 'red')

        nx.draw_networkx_labels(
            self.graph, pos, labels, ax=ax,
            font_size=10,
            font_weight='bold',
            font_color=font_color
        )
        
        # Set title
        ax.set_title(
            f"SocialX Graph - {self.current_layout.replace('_', ' ').title()} Layout\n"
            f"({self.graph.number_of_nodes()} users, {self.graph.number_of_edges()} connections)",
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        
        # Remove axes
        ax.axis('off')
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Refresh canvas
        self.canvas.draw()
    
    def export_graph(self):
        """Export the current graph as an image file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph Image",
            "socialx_graph.jpg",
            "JPEG Image (*.jpg);;PNG Image (*.png);;PDF Document (*.pdf);;SVG Image (*.svg)"
        )
        
        if file_path:
            try:
                # Save with high DPI for better quality
                self.figure.savefig(
                    file_path,
                    dpi=300,
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Graph exported successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export graph:\n{str(e)}"
                )

                