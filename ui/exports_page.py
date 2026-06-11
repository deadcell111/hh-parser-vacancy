from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.theme import Theme


class ExportCard(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        label = QLabel(title)
        label.setStyleSheet("font-size: 18px; font-weight: 800;")
        self.status = QLabel("Ready")
        self.status.setStyleSheet(f"color: {Theme.MUTED};")
        layout.addWidget(label)
        layout.addWidget(self.status)

    def set_status(self, text: str) -> None:
        self.status.setText(text)


class ExportsPage(QWidget):
    export_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Exports")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        grid = QGridLayout()
        self.excel_card = ExportCard("Excel Export")
        self.pdf_card = ExportCard("PDF Export")
        grid.addWidget(self.excel_card, 0, 0)
        grid.addWidget(self.pdf_card, 0, 1)
        layout.addLayout(grid)
        button = QPushButton("Generate Reports")
        button.setObjectName("PrimaryButton")
        button.clicked.connect(self.export_requested.emit)
        layout.addWidget(button)
        self.status = QLabel("No export yet.")
        self.status.setStyleSheet(f"color: {Theme.MUTED};")
        layout.addWidget(self.status)
        layout.addStretch()

    def set_status(self, value: str) -> None:
        self.status.setText(value)

    def set_export_stats(self, elapsed: float, sizes: dict[str, int]) -> None:
        self.excel_card.set_status(f"Generated in {elapsed:.1f}s | {sizes.get('xlsx', 0) / 1024:.1f} KB")
        self.pdf_card.set_status(f"Generated in {elapsed:.1f}s | {sizes.get('pdf', 0) / 1024:.1f} KB")
