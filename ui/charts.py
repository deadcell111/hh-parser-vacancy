from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.theme import Theme
from models.analysis import AnalysisState


class SkillsChart(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.title = QLabel("ТОП навыков рынка")
        self.title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(self.title)
        try:
            import pyqtgraph as pg

            self.plot = pg.PlotWidget()
            self.plot.setBackground(Theme.SURFACE)
            layout.addWidget(self.plot)
        except Exception:
            self.plot = None
            self.fallback = QLabel("Install pyqtgraph to render charts.")
            layout.addWidget(self.fallback)

    def update_state(self, state: AnalysisState) -> None:
        if not self.plot:
            return
        self.plot.clear()
        import pyqtgraph as pg

        rows = state.summary.top_skills[:10]
        if not rows:
            return
        counts = [int(row.get("Количество упоминаний", 0)) for row in rows]
        labels = [str(row.get("Навык", "")) for row in rows]
        x = list(range(len(counts)))
        self.plot.addItem(pg.BarGraphItem(x=x, height=counts, width=0.55, brush=Theme.ACCENT))
        axis = self.plot.getAxis("bottom")
        axis.setTicks([list(enumerate(labels))])
