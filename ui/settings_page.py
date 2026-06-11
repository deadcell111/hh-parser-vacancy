from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    settings_saved = pyqtSignal(str, str)

    def __init__(self, api_key: str, model: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        form = QFormLayout()
        self.api_key_input = QLineEdit(api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.model_input = QLineEdit(model)
        form.addRow("Gemini API Key", self.api_key_input)
        form.addRow("Gemini Model", self.model_input)
        layout.addLayout(form)
        button = QPushButton("Save local settings")
        button.setObjectName("PrimaryButton")
        button.clicked.connect(lambda: self.settings_saved.emit(self.api_key_input.text(), self.model_input.text()))
        layout.addWidget(button)
        self.status = QLabel("Stored in data/settings.local.json, ignored by git.")
        layout.addWidget(self.status)
        layout.addStretch()

    def set_status(self, value: str) -> None:
        self.status.setText(value)
