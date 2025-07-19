import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from config import Config

class AssistantGUI(QMainWindow, Config):
    STATES = {
        "idle": {"color": QColor(100, 100, 100), "dots": "idle"},
        "wake_detected": {"color": QColor(255, 165, 0), "dots": "active"},
        "listening": {"color": QColor(0, 150, 255), "dots": "idle"},
        "processing": {"color": QColor(138, 43, 226), "dots": "active"},
        "speaking": {"color": QColor(50, 205, 50), "dots": "active"}
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.WINDOW_SIZE)

        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(
            max(0, min(screen_geo.width() - self.width() - self.MARGIN, screen_geo.width() - self.width() - self.MARGIN)),
            max(0, self.MARGIN)
        )

        self.state = "idle"
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(1000 // self.ANIMATION_FPS)

        self.animation_counter = 0
        self.dot_positions = [0] * self.DOT_COUNT
        self.pin_scales = [1.0] * self.PIN_COUNT
        self.pin_phases = [random.uniform(0, 2 * math.pi) for _ in range(self.PIN_COUNT)]
        self.pin_frequencies = [random.uniform(5, 15) for _ in range(self.PIN_COUNT)]

        try:
            self.mic_pixmap = self.create_mic_icon(self.MIC_ICON_SIZE)
        except Exception as e:
            print(f"Error creating mic icon: {e}")
            self.mic_pixmap = QPixmap(self.MIC_ICON_SIZE)
            self.mic_pixmap.fill(Qt.transparent)

    def create_mic_icon(self, size):
        """Create a scalable circular microphone icon with pins."""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        try:
            painter.setRenderHint(QPainter.Antialiasing)

            center = QPoint(size.width() // 2, size.height() // 2)
            radius = min(size.width(), size.height()) // 3

            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(200, 200, 200))
            gradient.setColorAt(1, QColor(100, 100, 100))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(80, 80, 80), 2))
            painter.drawEllipse(center, radius, radius)

            stand_height = int(radius * 1.2)
            stand_width = radius // 3
            painter.drawRect(
                QRect(
                    center.x() - stand_width // 2,
                    center.y() - stand_height // 2,
                    stand_width,
                    stand_height
                )
            )

            grille_radius = int(radius * 0.6)
            painter.drawEllipse(center, grille_radius, grille_radius)
        except Exception as e:
            print(f"Error in create_mic_icon: {e}")
        finally:
            painter.end()
        return pixmap

    def set_state(self, state):
        """Change the assistant state with validation."""
        if state not in self.STATES:
            print(f"Warning: Invalid state '{state}'. Keeping current state '{self.state}'.")
            return
        if self.state in ["wake_detected", "processing", "speaking"] and state not in ["wake_detected", "processing", "speaking"]:
            self.dot_positions = [0] * self.DOT_COUNT
        print(f"Setting state to '{state}'")
        self.state = state
        self.update()

    def update_animation(self):
        """Update animation elements for dots and pins."""
        self.animation_counter += 1

        if self.STATES[self.state]["dots"] == "active":
            for i in range(self.DOT_COUNT):
                phase = i * math.pi / 2
                self.dot_positions[i] = math.sin(self.animation_counter / 5 + phase) * 10
        else:
            self.dot_positions = [0] * self.DOT_COUNT

        if self.state == "listening":
            for i in range(self.PIN_COUNT):
                self.pin_scales[i] = 0.9 + 0.3 * (math.sin(self.animation_counter / self.pin_frequencies[i] + self.pin_phases[i]) + 1) / 2

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)

            painter.setBrush(QBrush(self.BACKGROUND_COLOR))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 0, 0)

            mic_rect = self.mic_pixmap.rect()
            mic_rect.moveTo(self.MARGIN, (self.height() - mic_rect.height()) // 2)
            painter.drawPixmap(mic_rect, self.mic_pixmap)

            if self.state == "listening":
                self.draw_pins(painter, mic_rect.center())

            self.draw_dots(painter, mic_rect.right() + self.MARGIN * 5)

        except Exception as e:
            print(f"Error in paintEvent: {e}")
        finally:
            painter.end()

    def draw_pins(self, painter, center):
        """Draw animated pins around the mic icon with decreased length."""
        pin_width = 3
        painter.setPen(QPen(QColor(255, 255, 255, 150), pin_width))

        for i in range(self.PIN_COUNT):
            angle = i * (2 * math.pi / self.PIN_COUNT)
            dx = math.cos(angle) * 20
            dy = math.sin(angle) * 20
            end_x = center.x() + dx * self.pin_scales[i]
            end_y = center.y() + dy * self.pin_scales[i]
            painter.drawLine(center.x(), center.y(), int(end_x), int(end_y))

    def draw_dots(self, painter, start_x):
        """Draw animated dots with glow effect."""
        dot_radius = 5
        dot_spacing = 15
        base_y = self.height() // 2

        for i in range(self.DOT_COUNT):
            x = start_x + i * dot_spacing
            y = base_y + self.dot_positions[i]
            color = QColor(255, 255, 255) if self.STATES[self.state]["dots"] == "active" else QColor(150, 150, 150)
            painter.setPen(QPen(Qt.NoPen))

            for r in range(5, 0, -1):
                alpha = 50 - r * 10
                painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), alpha)))
                painter.drawEllipse(QPoint(int(x), int(y)), dot_radius + r, dot_radius + r)

            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPoint(int(x), int(y)), dot_radius, dot_radius)

    def mousePressEvent(self, event):
        """Initiate window dragging for non-title bar areas."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle window dragging with boundary checks."""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            screen_geo = QApplication.primaryScreen().availableGeometry()
            new_pos = event.globalPos() - self.drag_position
            new_pos.setX(max(0, min(new_pos.x(), screen_geo.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen_geo.height() - self.height())))
            self.move(new_pos)
            event.accept()