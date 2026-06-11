from __future__ import annotations


class Theme:
    BACKGROUND = "#0F172A"
    SURFACE = "#1E293B"
    SURFACE_2 = "#334155"
    BORDER = "#334155"
    TEXT = "#F9FAFB"
    MUTED = "#9CA3AF"
    ACCENT = "#7C3AED"
    ACCENT_2 = "#A78BFA"
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"


APP_STYLESHEET = f"""
* {{
    font-family: -apple-system, "Segoe UI", "Inter", Arial, sans-serif;
    color: {Theme.TEXT};
}}
QMainWindow, QWidget {{
    background: {Theme.BACKGROUND};
}}
QFrame#Sidebar {{
    background: #08111F;
    border-right: 1px solid {Theme.BORDER};
}}
QFrame#Card {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E293B, stop:1 #111827);
    border: 1px solid {Theme.BORDER};
    border-radius: 16px;
}}
QFrame#Card:hover {{
    background: #263449;
    border-color: {Theme.ACCENT_2};
}}
QPushButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 9px 12px;
    text-align: left;
}}
QPushButton:hover {{
    border-color: {Theme.BORDER};
    background: {Theme.SURFACE_2};
}}
QPushButton#PrimaryButton {{
    background: {Theme.ACCENT};
    border-color: {Theme.ACCENT};
    font-weight: 600;
    text-align: center;
}}
QLineEdit, QComboBox, QSpinBox {{
    background: {Theme.SURFACE};
    border: 1px solid {Theme.BORDER};
    border-radius: 12px;
    padding: 9px 12px;
}}
QTableView {{
    background: {Theme.SURFACE};
    border: 1px solid {Theme.BORDER};
    border-radius: 12px;
    gridline-color: transparent;
    selection-background-color: {Theme.ACCENT};
    alternate-background-color: #172033;
}}
QHeaderView::section {{
    background: #111827;
    color: {Theme.MUTED};
    padding: 10px;
    border: none;
    border-bottom: 1px solid {Theme.BORDER};
    font-weight: 700;
}}
QProgressBar {{
    border: 1px solid {Theme.BORDER};
    border-radius: 8px;
    background: {Theme.SURFACE};
    height: 12px;
}}
QProgressBar::chunk {{
    border-radius: 8px;
    background: {Theme.ACCENT};
}}
QTextEdit {{
    background: {Theme.SURFACE};
    border: 1px solid {Theme.BORDER};
    border-radius: 12px;
    padding: 10px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {Theme.BORDER};
    border-radius: 5px;
}}
"""
