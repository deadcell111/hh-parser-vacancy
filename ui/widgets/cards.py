from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout
from PyQt6.QtGui import QColor

from app.theme import Theme


class KpiCard(QFrame):
    def __init__(self, title: str, value: str = "0") -> None:
        super().__init__()
        self.setObjectName("Card")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {Theme.MUTED}; font-size: 12px; font-weight: 700; letter-spacing: .4px;")
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: object) -> None:
        self.value_label.setText(str(value))
