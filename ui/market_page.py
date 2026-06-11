from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from app.theme import Theme

_DEFAULT_WORKERS = 5
_DEFAULT_MIN_RELEVANCE = 50


class MarketPage(QWidget):
    run_requested = pyqtSignal(str, str, int, int, int)
    import_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("Анализ рынка")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.query_input = QLineEdit("Системный администратор")
        self.query_input.setPlaceholderText("Например: DevOps, Linux, Python developer")

        self.region_input = QLineEdit("Алматы")
        self.region_input.setPlaceholderText("Алматы, Астана, Москва или ID региона")

        self.pages_input = QSpinBox()
        self.pages_input.setRange(1, 100)
        self.pages_input.setValue(1)
        self.pages_input.setSuffix(" стр. (~100 вак./стр.)")

        form.addRow("Поисковый запрос", self.query_input)
        form.addRow("Регион", self.region_input)
        form.addRow("Страниц", self.pages_input)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.run_button = QPushButton("Запустить анализ")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self._emit_run)
        import_button = QPushButton("Импорт TXT / CSV / XLSX")
        import_button.clicked.connect(self.import_requested.emit)
        buttons.addWidget(self.run_button)
        buttons.addWidget(import_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.status = QLabel("Готово к запуску")
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
            _DEFAULT_WORKERS,
            _DEFAULT_MIN_RELEVANCE,
        )
