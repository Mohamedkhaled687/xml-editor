"""
Enhanced Graph Visualization Window - Complete implementation for social network visualization
Supports multiple layout algorithms, interactive features, and image export
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QComboBox, QSpinBox, QCheckBox,
                              QGroupBox, QFileDialog, QMessageBox, QSlider, QTabWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np


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
        # Update most active user display
        self._update_most_active_group()
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
        self.setWindowTitle("Social Network Graph Visualization - Advanced")
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
        main_layout.addWidget(graph_container, 3)
        main_layout.addWidget(control_panel, 1)
    
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
        title_label = QLabel("🔗 Social Network Graph Visualization")
        title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        
        self.info_label = QLabel(
            f"Nodes: {self.metrics.get('num_nodes', 0)} | "
            f"Edges: {self.metrics.get('num_edges', 0)} | "
            f"Density: {self.metrics.get('density', 0):.3f}"
        )
        self.info_label.setStyleSheet("""
            color: rgba(200, 220, 240, 255);
            font-size: 13px;
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
                font-size: 13px;
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
                font-size: 12px;
            }
            QComboBox, QSpinBox {
                background-color: rgba(40, 60, 80, 180);
                border: 1px solid rgba(80, 120, 160, 120);
                border-radius: 4px;
                color: white;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(40, 60, 80, 200);
                color: white;
                selection-background-color: rgba(40, 100, 180, 200);
                border: 1px solid rgba(80, 120, 160, 120);
            }
            QPushButton {
                background: rgba(40, 100, 180, 200);
                border: 1px solid rgba(80, 150, 220, 180);
                border-radius: 5px;
                color: white;
                font-size: 12px;
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
                font-size: 12px;
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
        
        # Most Active User
        active_group = self._create_most_active_group()
        analysis_layout.addWidget(active_group)
        
        # Mutual Followers
        mutual_group = self._create_mutual_followers_group()
        analysis_layout.addWidget(mutual_group)
        
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
        self.layout_combo.setCurrentIndex(1)  # Default to Circular Layout
        self.layout_combo.currentIndexChanged.connect(self.on_layout_changed)
        layout.addWidget(self.layout_combo)
        
        return group
    
    def _create_visualization_group(self):
        """Create visualization settings group."""
        group = QGroupBox("Visualization Settings")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Show labels checkbox
        self.labels_checkbox = QCheckBox("Show Node Labels")
        self.labels_checkbox.setChecked(True)
        self.labels_checkbox.stateChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.labels_checkbox)
        
        # Node size by influence
        self.influence_checkbox = QCheckBox("Size by Influence (Followers)")
        self.influence_checkbox.setChecked(True)
        self.influence_checkbox.stateChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.influence_checkbox)
        
        # Node base size
        size_label = QLabel("Base Node Size:")
        layout.addWidget(size_label)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(100, 2000)
        self.size_spinbox.setValue(500)
        self.size_spinbox.setSingleStep(100)
        self.size_spinbox.valueChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.size_spinbox)
        
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
        self.color_combo.currentIndexChanged.connect(lambda: self.draw_graph())
        layout.addWidget(self.color_combo)
        
        return group
    
    def _create_statistics_group(self):
        """Create network statistics display group."""
        group = QGroupBox("Network Statistics")
        self.stats_layout = QVBoxLayout(group)
        self.stats_layout.setSpacing(8)
        
        # Create label to hold statistics
        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("font-size: 11px; line-height: 1.5;")
        self.stats_layout.addWidget(self.stats_label)
        
        return group
    
    def _update_statistics_group(self):
        """Update the statistics group with current metrics data."""
        if not hasattr(self, 'stats_label'):
            return
        
        # Build statistics text from metrics
        stats_text = f"""
<b>Network Metrics:</b><br>
• Nodes: {self.metrics.get('num_nodes', 0)}<br>
• Edges: {self.metrics.get('num_edges', 0)}<br>
• Density: {self.metrics.get('density', 0):.3f}<br>
• Avg Followers: {self.metrics.get('avg_in_degree', 0):.1f}<br>
• Avg Following: {self.metrics.get('avg_out_degree', 0):.1f}<br>
        """
        
        if 'most_influential' in self.metrics:
            inf = self.metrics['most_influential']
            stats_text += f"<br><b>Most Influential:</b><br>• {inf['name']}<br>  ({inf['followers']} followers)<br>"
        
        if 'most_active' in self.metrics:
            act = self.metrics['most_active']
            stats_text += f"<br><b>Most Active:</b><br>• {act['name']}<br>  (follows {act['following']})<br>"
        
        self.stats_label.setText(stats_text)
    
    def _create_most_active_group(self):
        """Create group to display most active user."""
        group = QGroupBox("Most Active User")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Create label to hold most active user info
        self.active_label = QLabel()
        self.active_label.setWordWrap(True)
        self.active_label.setStyleSheet("font-size: 11px; line-height: 1.5;")
        layout.addWidget(self.active_label)
        
        return group
    
    def _update_most_active_group(self):
        """Update the most active user display."""
        if not hasattr(self, 'active_label'):
            return
        
        active_text = "<b>Most Active User</b><br>"
        
        if 'most_active' in self.metrics:
            act = self.metrics['most_active']
            active_text += f"<br>• <b>{act['name']}</b><br>"
            active_text += f"  Follows: {act['following']} users"
        else:
            active_text += "No data available"
        
        self.active_label.setText(active_text)
    
    def _create_mutual_followers_group(self):
        """Create group for mutual followers analysis."""
        group = QGroupBox("Mutual Followers Analysis")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Instructions
        instructions = QLabel("Select users to find mutual followers:")
        instructions.setStyleSheet("font-size: 10px; color: rgba(150, 180, 220, 255);")
        layout.addWidget(instructions)
        
        # User selection combo boxes (show 2 users)
        users_list = sorted(list(self.nodes.values())) if self.nodes else []
        
        # User 1
        user1_layout = QHBoxLayout()
        user1_layout.addWidget(QLabel("User 1:"))
        self.mutual_user1_combo = QComboBox()
        self.mutual_user1_combo.addItems(users_list)
        user1_layout.addWidget(self.mutual_user1_combo)
        layout.addLayout(user1_layout)
        
        # User 2
        user2_layout = QHBoxLayout()
        user2_layout.addWidget(QLabel("User 2:"))
        self.mutual_user2_combo = QComboBox()
        self.mutual_user2_combo.addItems(users_list)
        if len(users_list) > 1:
            self.mutual_user2_combo.setCurrentIndex(1)
        user2_layout.addWidget(self.mutual_user2_combo)
        layout.addLayout(user2_layout)
        
        # Find mutual followers button
        find_mutual_btn = QPushButton("🔍 Find Mutual Followers")
        find_mutual_btn.clicked.connect(self.find_mutual_followers)
        layout.addWidget(find_mutual_btn)
        
        # Results display
        self.mutual_label = QLabel("No results yet")
        self.mutual_label.setWordWrap(True)
        self.mutual_label.setStyleSheet("font-size: 10px; line-height: 1.4;")
        layout.addWidget(self.mutual_label)
        
        return group
    
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
        
        # Find user IDs from names
        user1_id = None
        user2_id = None
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
        
        # Format results
        result_text = f"<b>Mutual Followers between {user1_name} and {user2_name}:</b><br>"
        
        if mutual_followers:
            result_text += f"<br>Found {len(mutual_followers)} mutual follower(s):<br>"
            for follower_id in sorted(mutual_followers):
                follower_name = self.nodes.get(follower_id, follower_id)
                result_text += f"• {follower_name}<br>"
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
        
        # Highlight selected users if any
        if self.selected_users:
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
        
        # Highlight mutual followers
        if self.selected_mutual_followers:
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
        
        # Draw labels if enabled
        if self.labels_checkbox.isChecked():
            labels = {node: self.nodes.get(node, node) for node in self.graph.nodes()}
            nx.draw_networkx_labels(
                self.graph, pos, labels, ax=ax,
                font_size=10,
                font_weight='bold',
                font_color='red'
            )
        
        # Set title
        ax.set_title(
            f"Social Network Graph - {self.current_layout.replace('_', ' ').title()} Layout\n"
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
            "social_network_graph.png",
            "PNG Image (*.png);;JPEG Image (*.jpg);;PDF Document (*.pdf);;SVG Image (*.svg)"
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

                