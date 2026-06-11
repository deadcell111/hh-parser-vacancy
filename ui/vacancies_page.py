from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QTableView, QVBoxLayout, QWidget

from models.analysis import AnalysisState
from ui.table_models import ContainsFilterProxy, ListTableModel


class VacanciesPage(QWidget):
    analyze_url_requested = pyqtSignal(str)
    import_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Vacancies")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        controls = QHBoxLayout()
        self.url_input = QLineEdit("https://hh.kz/vacancy/")
        analyze_button = QPushButton("Analyze URL")
        analyze_button.setObjectName("PrimaryButton")
        import_button = QPushButton("Import TXT / CSV / XLSX")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search vacancies, skills, company...")
        analyze_button.clicked.connect(lambda: self.analyze_url_requested.emit(self.url_input.text()))
        import_button.clicked.connect(self.import_requested.emit)
        controls.addWidget(self.url_input)
        controls.addWidget(analyze_button)
        controls.addWidget(import_button)
        controls.addWidget(self.search_input)
        layout.addLayout(controls)
        self.model = ListTableModel(["Title", "Company", "City", "Salary", "Score", "Skills", "URL"])
        self.proxy = ContainsFilterProxy()
        self.proxy.setSourceModel(self.model)
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.search_input.textChanged.connect(self.proxy.set_query)
        layout.addWidget(self.table)

    def update_state(self, state: AnalysisState) -> None:
        rows = [
            [
                vacancy.title,
                vacancy.company,
                vacancy.city,
                vacancy.salary,
                vacancy.relevance_score,
                ", ".join(skill["name"] for skill in vacancy.skills[:8]),
                vacancy.url,
            ]
            for vacancy in state.vacancies
        ]
        self.model.set_rows(rows)
