from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from app.theme import Theme


class MarketPage(QWidget):
    run_requested = pyqtSignal(str, str, int, int, int)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Market Analysis")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)

        form = QFormLayout()
        self.query_input = QLineEdit("Системный администратор")
        self.region_input = QLineEdit("Алматы")
        self.pages_input = QSpinBox()
        self.pages_input.setRange(1, 100)
        self.pages_input.setValue(1)
        self.workers_input = QComboBox()
        self.workers_input.addItems(["3", "5", "10"])
        self.workers_input.setCurrentText("5")
        self.relevance_input = QSpinBox()
        self.relevance_input.setRange(-100, 500)
        self.relevance_input.setValue(50)
        form.addRow("Search query", self.query_input)
        form.addRow("Region", self.region_input)
        form.addRow("Pages", self.pages_input)
        form.addRow("Workers", self.workers_input)
        form.addRow("Min relevance", self.relevance_input)
        layout.addLayout(form)

        self.run_button = QPushButton("Run Market Analysis")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self._emit_run)
        layout.addWidget(self.run_button)
        self.status = QLabel("Ready")
        self.status.setStyleSheet(f"color: {Theme.MUTED};")
        layout.addWidget(self.status)
        layout.addStretch()

    def set_status(self, value: str) -> None:
        self.status.setText(value)

    def _emit_run(self) -> None:
        self.run_requested.emit(
            self.query_input.text(),
            self.region_input.text(),
            self.pages_input.value(),
            int(self.workers_input.currentText()),
            self.relevance_input.value(),
        )
