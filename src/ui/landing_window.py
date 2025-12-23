# ==================== FILE 2: landing_window.py ====================
"""
Landing Window - Initial window for selecting input method
"""
import random
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPen, QPaintEvent, QResizeEvent


class AnimatedBackground(QWidget):
    """Widget that draws animated network nodes and connections with optimized performance."""

    CONNECTION_DISTANCE = 180  # Max distance for node connections
    GRID_CELL_SIZE = 180  # Spatial grid cell size for O(n) neighbor lookups

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.nodes: List[Dict[str, Any]] = []
        self._grid: Dict[tuple, List[Dict[str, Any]]] = {}
        self.init_nodes()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

        # Setup animation timer - 33ms for smooth 30 FPS
        self.timer: QTimer = QTimer(self)
        self.timer.timeout.connect(self._update_and_repaint)
        self.timer.start(33)

    def init_nodes(self) -> None:
        """Initialize optimized number of nodes for smooth animation."""
        # 70 nodes for good coverage on 1200x700 window - spatial grid keeps it smooth
        for _ in range(100):
            node = {
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'vx': random.uniform(-0.8, 0.8),
                'vy': random.uniform(-0.8, 0.8),
                'color': random.choice([
                    QColor(100, 200, 255, 180),
                    QColor(180, 100, 255, 180),
                    QColor(100, 255, 200, 180)
                ]),
                'size': random.randint(6, 12)
            }
            self.nodes.append(node)

    def _build_spatial_grid(self) -> None:
        """Build spatial hash grid for O(n) neighbor lookups instead of O(n²)."""
        self._grid.clear()
        for node in self.nodes:
            cell_x = int(node['x'] // self.GRID_CELL_SIZE)
            cell_y = int(node['y'] // self.GRID_CELL_SIZE)
            key = (cell_x, cell_y)
            if key not in self._grid:
                self._grid[key] = []
            self._grid[key].append(node)

    def _get_nearby_nodes(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get nodes in adjacent cells - O(1) lookup."""
        cell_x = int(node['x'] // self.GRID_CELL_SIZE)
        cell_y = int(node['y'] // self.GRID_CELL_SIZE)
        nearby = []
        # Check 3x3 grid of cells around current cell
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                key = (cell_x + dx, cell_y + dy)
                if key in self._grid:
                    nearby.extend(self._grid[key])
        return nearby

    def _update_and_repaint(self) -> None:
        """Update node positions and trigger repaint."""
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        for node in self.nodes:
            node['x'] += node['vx']
            node['y'] += node['vy']

            # Bounce off edges with slight randomization
            if node['x'] < 0 or node['x'] > w:
                node['vx'] *= -1
                node['x'] = max(0, min(w, node['x']))
            if node['y'] < 0 or node['y'] > h:
                node['vy'] *= -1
                node['y'] = max(0, min(h, node['y']))

        self._build_spatial_grid()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw rich gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(8, 12, 24))
        gradient.setColorAt(0.3, QColor(12, 20, 40))
        gradient.setColorAt(0.7, QColor(16, 28, 52))
        gradient.setColorAt(1, QColor(10, 16, 32))
        painter.fillRect(self.rect(), gradient)

        # Draw connections using spatial grid - O(n) instead of O(n²)
        drawn_connections = set()
        for node in self.nodes:
            nearby = self._get_nearby_nodes(node)
            for other in nearby:
                if other is node:
                    continue
                # Avoid drawing duplicate connections
                pair = (id(node), id(other)) if id(node) < id(other) else (id(other), id(node))
                if pair in drawn_connections:
                    continue

                dx = node['x'] - other['x']
                dy = node['y'] - other['y']
                dist_sq = dx * dx + dy * dy
                max_dist_sq = self.CONNECTION_DISTANCE ** 2

                if dist_sq < max_dist_sq:
                    drawn_connections.add(pair)
                    alpha = int(80 * (1 - dist_sq / max_dist_sq))
                    pen = QPen(QColor(120, 180, 255, alpha))
                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawLine(int(node['x']), int(node['y']),
                                     int(other['x']), int(other['y']))

        # Draw nodes with glow effect
        for node in self.nodes:
            size = node['size']
            painter.setPen(Qt.NoPen)

            # Outer glow
            radial = QRadialGradient(node['x'], node['y'], size * 2)
            radial.setColorAt(0, QColor(node['color'].red(),
                                        node['color'].green(),
                                        node['color'].blue(), 100))
            radial.setColorAt(1, QColor(node['color'].red(),
                                        node['color'].green(),
                                        node['color'].blue(), 0))
            painter.setBrush(radial)
            painter.drawEllipse(int(node['x'] - size * 2), int(node['y'] - size * 2),
                                size * 4, size * 4)

            # Core node
            radial = QRadialGradient(node['x'], node['y'], size)
            radial.setColorAt(0, QColor(255, 255, 255, 200))
            radial.setColorAt(0.3, node['color'])
            radial.setColorAt(1, QColor(node['color'].red(),
                                        node['color'].green(),
                                        node['color'].blue(), 50))
            painter.setBrush(radial)
            painter.drawEllipse(int(node['x'] - size), int(node['y'] - size),
                                size * 2, size * 2)


class NetworkIcon(QWidget):
    """Custom widget to draw the network icon."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(120, 120)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x, center_y = 60, 60

        # Draw central globe
        painter.setPen(QPen(QColor(100, 230, 255), 2))
        painter.setBrush(QColor(30, 50, 70, 100))
        painter.drawEllipse(center_x - 20, center_y - 20, 40, 40)

        # Draw latitude lines
        painter.setPen(QPen(QColor(100, 230, 255), 1))
        painter.drawEllipse(center_x - 20, center_y - 10, 40, 20)
        painter.drawEllipse(center_x - 20, center_y - 5, 40, 10)

        # Draw longitude line
        painter.drawArc(center_x - 20, center_y - 20, 40, 40, 0, 180 * 16)

        # Draw surrounding documents
        positions = [
            (center_x, center_y - 45),
            (center_x + 40, center_y - 30),
            (center_x + 40, center_y + 30),
            (center_x, center_y + 45),
            (center_x - 40, center_y + 30),
            (center_x - 40, center_y - 30),
        ]

        for px, py in positions:
            painter.setPen(QPen(QColor(100, 230, 255), 2))
            painter.setBrush(QColor(30, 50, 70, 150))
            painter.drawRect(int(px - 8), int(py - 10), 16, 20)

            painter.setPen(QPen(QColor(100, 230, 255), 1))
            painter.drawLine(int(px - 5), int(py - 5), int(px + 5), int(py - 5))
            painter.drawLine(int(px - 5), int(py), int(px + 5), int(py))
            painter.drawLine(int(px - 5), int(py + 5), int(px + 5), int(py + 5))

            painter.setPen(QPen(QColor(100, 200, 255, 100), 1))
            painter.drawLine(center_x, center_y, int(px), int(py))


class LandingWindow(QMainWindow):
    """Landing window for selecting XML input method."""

    browse_clicked = Signal()
    manual_clicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("🌐 SocialX XML Data Editor")
        self.setMinimumSize(1200, 700)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add animated background
        self.bg = AnimatedBackground(central)

        # Create content container
        content_widget = QWidget()
        content_widget.setAttribute(Qt.WA_TranslucentBackground)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignCenter)

        # Create card container
        card = QWidget()
        card.setFixedSize(750, 550)
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgba(20, 35, 55, 230),
                                           stop:1 rgba(15, 25, 45, 230));
                border: 1px solid rgba(100, 150, 200, 100);
                border-radius: 20px;
            }
        """)

        card_glow = QGraphicsDropShadowEffect()
        card_glow.setColor(QColor(50, 150, 255, 80))
        card_glow.setBlurRadius(40)
        card_glow.setOffset(0, 0)
        card.setGraphicsEffect(card_glow)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(30)
        card_layout.setContentsMargins(50, 50, 50, 50)

        # Title
        title = QLabel("SocialX XML Data Editor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: rgba(100, 230, 255, 255);
                font-size: 36px;
                font-weight: bold;
                background: transparent;
            }
        """)
        card_layout.addWidget(title)

        # Network icon
        icon_container = QWidget()
        icon_container.setFixedHeight(130)
        icon_container.setAttribute(Qt.WA_TranslucentBackground)
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        network_icon = NetworkIcon()
        icon_layout.addWidget(network_icon)
        card_layout.addWidget(icon_container)

        # Question text
        question = QLabel("<Welcome> Select mode to provide the XML Data </Welcome>")

        question.setAlignment(Qt.AlignCenter)
        question.setStyleSheet("""
            QLabel {
                color: rgba(200, 210, 220, 255);
                font-size: 18px;
                background: transparent;
            }
        """)
        card_layout.addWidget(question)

        # Buttons
        button_container = QWidget()
        button_container.setAttribute(Qt.WA_TranslucentBackground)
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(20)
        button_layout.setAlignment(Qt.AlignCenter)

        browse_btn = QPushButton("📁  Browse Local XML File")
        browse_btn.clicked.connect(self.browse_clicked.emit)
        browse_btn.setObjectName("browse_btn")
        browse_btn.setStyleSheet("""
        #browse_btn {
            background: rgba(40, 50, 65, 180);
            border: 2px solid rgba(80, 100, 130, 255);
            border-radius: 15px;
            color: rgba(200, 210, 220, 255);
            font-size: 18px;
            font-weight: bold;
            min-width: 400px;
            min-height: 35px;
        }
        #browse_btn:hover {
            background: rgba(50, 60, 75, 200);
            border: 2px solid rgba(100, 120, 150, 255);
            color: white;
        }

        #browse_btn:pressed {
            background: rgba(30, 40, 55, 180);
        }
        """)
        button_layout.addWidget(browse_btn, alignment=Qt.AlignCenter)

        manual_btn = QPushButton("⌨  Enter XML Manually")
        manual_btn.clicked.connect(self.manual_clicked.emit)
        manual_btn.setObjectName("manual_btn")
        manual_btn.setStyleSheet("""
            #manual_btn {
                background: rgba(40, 50, 65, 180);
                border: 2px solid rgba(80, 100, 130, 255);
                border-radius: 15px;
                color: rgba(200, 210, 220, 255);
                font-size: 18px;
                font-weight: bold;                            
                min-width: 400px;
                min-height: 35px;

            }
            #manual_btn:hover {
                background: rgba(50, 60, 75, 200);
                border: 2px solid rgba(100, 120, 150, 255);
                color: white;
            }

            #manual_btn:pressed {
                background: rgba(30, 40, 55, 180);
            }
        """)
        button_layout.addWidget(manual_btn, alignment=Qt.AlignCenter)

        card_layout.addWidget(button_container)

        # Version label
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                border: transparent;
            }
        """)
        card_layout.addWidget(version)

        content_layout.addWidget(card)
        main_layout.addWidget(content_widget)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.bg.setGeometry(0, 0, self.width(), self.height())