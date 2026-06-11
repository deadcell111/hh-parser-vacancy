from __future__ import annotations

from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from models.analysis import AnalysisState
from ui.charts import SkillsChart
from ui.widgets.cards import KpiCard


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        grid = QGridLayout()
        self.cards = {
            "found": KpiCard("Найдено вакансий"),
            "salary": KpiCard("Средняя зарплата"),
            "match": KpiCard("Соответствие резюме"),
            "skills": KpiCard("Уникальные навыки"),
        }
        for index, card in enumerate(self.cards.values()):
            grid.addWidget(card, 0, index)
        layout.addLayout(grid)
        self.skills_chart = SkillsChart()
        layout.addWidget(self.skills_chart)
        layout.addStretch()

    def update_state(self, state: AnalysisState) -> None:
        self.cards["found"].set_value(state.summary.vacancies_found)
        self.cards["salary"].set_value(state.summary.average_salary or "N/A")
        self.cards["match"].set_value(f"{state.summary.resume_match}%")
        self.cards["skills"].set_value(state.summary.unique_skills)
        self.skills_chart.update_state(state)
