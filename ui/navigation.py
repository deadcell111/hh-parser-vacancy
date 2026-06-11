from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout


class NavigationSidebar(QFrame):
    page_changed = pyqtSignal(str)

    PAGES = [
        ("dashboard", "🏠  Dashboard"),
        ("vacancies", "📄  Vacancies"),
        ("market", "📊  Market Analysis"),
        ("top_skills", "   ТОП навыков"),
        ("top_duties", "   ТОП обязанностей"),
        ("top_requirements", "   ТОП требований"),
        ("advisor", "🧠  AI Advisor"),
        ("resume", "📋  Resume Gap Analysis"),
        ("roadmap", "🛣  Learning Roadmap"),
        ("exports", "📁  Exports"),
        ("settings", "⚙  Settings"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 14)
        layout.setSpacing(6)
        title = QLabel("HH Career\nIntelligence")
        title.setStyleSheet("font-size: 22px; font-weight: 800; line-height: 1.2;")
        layout.addWidget(title)
        layout.addSpacing(18)
        for page_id, label in self.PAGES:
            button = QPushButton(label)
            button.setMinimumHeight(38)
            button.clicked.connect(lambda _=False, target=page_id: self.page_changed.emit(target))
            layout.addWidget(button)
        layout.addStretch()
