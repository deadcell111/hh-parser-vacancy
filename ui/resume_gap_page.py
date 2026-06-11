from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHeaderView, QLabel, QPushButton, QTableView, QVBoxLayout, QWidget

from app.theme import Theme
from models.analysis import AnalysisState
from ui.table_models import ListTableModel


class ResumeGapPage(QWidget):
    resume_upload_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Resume Gap Analysis")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        button = QPushButton("Upload Resume DOCX / PDF / TXT")
        button.setObjectName("PrimaryButton")
        button.clicked.connect(self.resume_upload_requested.emit)
        layout.addWidget(button)

        self.model = ListTableModel(["Skill", "Frequency", "Priority"])
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.recommendation_card = QFrame()
        self.recommendation_card.setObjectName("Card")
        card_layout = QVBoxLayout(self.recommendation_card)
        self.recommendations = QLabel("Recommendations will appear after resume analysis.")
        self.recommendations.setWordWrap(True)
        self.recommendations.setStyleSheet(f"color: {Theme.MUTED};")
        card_layout.addWidget(QLabel("Recommendations"))
        card_layout.addWidget(self.recommendations)
        layout.addWidget(self.recommendation_card)

    def update_state(self, state: AnalysisState) -> None:
        result = state.resume_result or {}
        missing = result.get("missing_skills", [])
        top_map = {row.get("Навык"): row.get("Процент встречаемости", "") for row in state.summary.top_skills}
        rows = [[skill, top_map.get(skill, ""), self._priority(skill, state)] for skill in missing]
        self.model.set_rows(rows)
        recommendations = result.get("recommendations", []) or result.get("salary_growth_skills", [])
        self.recommendations.setText("\n".join(f"• {item}" for item in recommendations) if recommendations else "No recommendations yet.")

    def _priority(self, skill: str, state: AnalysisState) -> str:
        top_names = [row.get("Навык") for row in state.summary.top_skills[:10]]
        return "High" if skill in top_names else "Medium"
