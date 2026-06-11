from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.theme import Theme
from models.analysis import AnalysisState


class SectionCard(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        label = QLabel(title)
        label.setStyleSheet("font-size: 16px; font-weight: 800;")
        self.layout.addWidget(label)

    def add_text(self, value: object) -> None:
        text = QLabel(self._format(value))
        text.setWordWrap(True)
        text.setStyleSheet(f"color: {Theme.MUTED}; font-size: 13px;")
        self.layout.addWidget(text)

    def _format(self, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(f"• {item}" for item in value)
        return str(value)


class TextReportPage(QWidget):
    def __init__(self, title_text: str, state_attr: str) -> None:
        super().__init__()
        self.state_attr = state_attr
        root = QVBoxLayout(self)
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        root.addWidget(title)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(12)
        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll)
        self._empty()

    def update_state(self, state: AnalysisState) -> None:
        value = getattr(state, self.state_attr)
        self._clear()
        if not value:
            self._empty()
            return
        if self.state_attr == "roadmap":
            self._roadmap(value)
            return
        self._report(value)

    def _report(self, value: dict[str, object]) -> None:
        labels = {
            "current_level": "Current Level",
            "market_match": "Market Match",
            "top_strengths": "Top Strengths",
            "critical_gaps": "Critical Gaps",

            "recommendations": "Recommendations",
            "market_overview": "Market Overview",
            "missing_skills": "Missing Skills",
            "missing_technologies": "Missing Technologies",
            "knowledge_gaps": "Knowledge Gaps",

            "summary": "Summary",
        }
        for key, item in value.items():
            card = SectionCard(labels.get(key, key.replace("_", " ").title()))
            card.add_text(item)
            self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    def _roadmap(self, value: dict[str, object]) -> None:
        weeks = value.get("weeks", []) if isinstance(value, dict) else []
        if not weeks:
            self._empty()
            return
        for week in weeks:
            if not isinstance(week, dict):
                continue
            card = SectionCard(f"Week {week.get('week', '')}")
            card.add_text("Skills: " + ", ".join(map(str, week.get("skills", []))))
            card.add_text("Why: " + str(week.get("why", "")))
            card.add_text("Frequency: " + str(week.get("market_frequency", "")))
            card.add_text("Career impact: " + str(week.get("career_impact", "")))
            card.add_text("Practice: " + str(week.get("practice_task", "")))
            self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    def _empty(self) -> None:
        card = SectionCard("No data yet")
        card.add_text("Run market analysis and AI generation to see this report.")
        self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    def _clear(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
