from __future__ import annotations

from PyQt6.QtWidgets import QHeaderView, QLabel, QLineEdit, QTableView, QVBoxLayout, QWidget

from models.analysis import AnalysisState
from ui.table_models import ContainsFilterProxy, ListTableModel


class TopTablePage(QWidget):
    def __init__(self, title_text: str, data_key: str) -> None:
        super().__init__()
        self.data_key = data_key
        layout = QVBoxLayout(self)
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        layout.addWidget(self.search)
        self.model = ListTableModel(["Name", "Count", "Frequency"])
        self.proxy = ContainsFilterProxy()
        self.proxy.setSourceModel(self.model)
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search.textChanged.connect(self.proxy.set_query)
        layout.addWidget(self.table)

    def update_state(self, state: AnalysisState) -> None:
        rows = getattr(state.summary, self.data_key)
        self.model.set_rows([list(row.values())[:3] for row in rows])
