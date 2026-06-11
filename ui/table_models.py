from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt


class ListTableModel(QAbstractTableModel):
    def __init__(self, headers: list[str], rows: list[list[Any]] | None = None) -> None:
        super().__init__()
        self.headers = headers
        self.rows = rows or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None
        value = self.rows[index.row()][index.column()]
        return "" if value is None else str(value)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return str(section + 1)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self.layoutAboutToBeChanged.emit()
        reverse = order == Qt.SortOrder.DescendingOrder
        self.rows.sort(key=lambda row: self._sort_key(row[column]), reverse=reverse)
        self.layoutChanged.emit()

    def set_rows(self, rows: list[list[Any]]) -> None:
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def _sort_key(self, value: Any) -> Any:
        try:
            return float(str(value).replace("%", "").replace(" ", "").replace(",", "."))
        except ValueError:
            return str(value).lower()


class ContainsFilterProxy(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self.query = ""

    def set_query(self, query: str) -> None:
        self.query = query.lower().strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self.query:
            return True
        model = self.sourceModel()
        if model is None:
            return True
        for column in range(model.columnCount()):
            index = model.index(source_row, column, source_parent)
            if self.query in str(model.data(index, Qt.ItemDataRole.DisplayRole)).lower():
                return True
        return False
