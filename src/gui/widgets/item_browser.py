from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ItemBrowser(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._all_items: list[dict[str, Any]] = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(12)

        filter_frame = QFrame()
        filter_frame.setObjectName("BrowserFilterFrame")

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "搜尋物品名稱、Market Hash Name 或磨損..."
        )
        self.search_input.setClearButtonEnabled(True)

        self.rarity_filter = QComboBox()
        self.rarity_filter.setMinimumWidth(180)
        self.rarity_filter.addItem("全部稀有度")

        self.rare_only_checkbox = QCheckBox("只顯示稀有物品")

        self.stattrak_only_checkbox = QCheckBox("只顯示 StatTrak")

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(self.rarity_filter)
        filter_layout.addWidget(self.rare_only_checkbox)
        filter_layout.addWidget(self.stattrak_only_checkbox)

        self.summary_label = QLabel("尚未選擇箱子")
        self.summary_label.setObjectName("BrowserSummary")

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "物品",
                "磨損",
                "稀有度",
                "StatTrak",
                "紀念品",
                "稀有池",
                "Market Hash Name",
            ]
        )

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.Stretch,
        )

        root_layout.addWidget(filter_frame)
        root_layout.addWidget(self.summary_label)
        root_layout.addWidget(self.table, 1)

        self.search_input.textChanged.connect(
            self.apply_filters
        )
        self.rarity_filter.currentIndexChanged.connect(
            self.apply_filters
        )
        self.rare_only_checkbox.toggled.connect(
            self.apply_filters
        )
        self.stattrak_only_checkbox.toggled.connect(
            self.apply_filters
        )

    def set_items(
        self,
        items: list[dict[str, Any]],
        case_name: str,
    ) -> None:
        self._all_items = items

        current_rarity = self.rarity_filter.currentText()

        rarities = sorted(
            {
                str(item.get("rarity_name"))
                for item in items
                if item.get("rarity_name")
            },
            key=str.lower,
        )

        self.rarity_filter.blockSignals(True)
        self.rarity_filter.clear()
        self.rarity_filter.addItem("全部稀有度")

        for rarity in rarities:
            self.rarity_filter.addItem(rarity)

        rarity_index = self.rarity_filter.findText(
            current_rarity
        )

        if rarity_index >= 0:
            self.rarity_filter.setCurrentIndex(
                rarity_index
            )

        self.rarity_filter.blockSignals(False)

        self.summary_label.setText(
            f"{case_name} · 共 {len(items):,} 個可交易版本"
        )

        self.apply_filters()

    def clear_items(self) -> None:
        self._all_items = []
        self.table.clearContents()
        self.table.setRowCount(0)
        self.summary_label.setText("尚未選擇箱子")

    def apply_filters(self) -> None:
        query = self.search_input.text().strip().lower()
        selected_rarity = self.rarity_filter.currentText()
        rare_only = self.rare_only_checkbox.isChecked()
        stattrak_only = (
            self.stattrak_only_checkbox.isChecked()
        )

        filtered_items: list[dict[str, Any]] = []

        for item in self._all_items:
            if selected_rarity != "全部稀有度":
                if (
                    str(item.get("rarity_name") or "")
                    != selected_rarity
                ):
                    continue

            if rare_only and not bool(item.get("is_rare")):
                continue

            if stattrak_only and not bool(
                item.get("stattrak")
            ):
                continue

            searchable_text = " ".join(
                [
                    str(item.get("display_name") or ""),
                    str(item.get("market_hash_name") or ""),
                    str(item.get("wear_name") or ""),
                    str(item.get("rarity_name") or ""),
                ]
            ).lower()

            if query and query not in searchable_text:
                continue

            filtered_items.append(item)

        self.populate_table(filtered_items)

    def populate_table(
        self,
        items: list[dict[str, Any]],
    ) -> None:
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(items))

        for row_index, item_data in enumerate(items):
            values = [
                item_data.get("display_name") or "-",
                item_data.get("wear_name") or "-",
                item_data.get("rarity_name") or "-",
                "是" if item_data.get("stattrak") else "否",
                "是" if item_data.get("souvenir") else "否",
                "是" if item_data.get("is_rare") else "否",
                item_data.get("market_hash_name") or "-",
            ]

            rarity_color = self.normalize_color(
                item_data.get("rarity_color")
            )

            for column_index, value in enumerate(values):
                table_item = QTableWidgetItem(str(value))

                if column_index == 0 and rarity_color:
                    table_item.setForeground(
                        QColor(rarity_color)
                    )

                if column_index in {3, 4, 5}:
                    table_item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                if (
                    column_index == 5
                    and item_data.get("is_rare")
                ):
                    table_item.setForeground(
                        QColor("#f59e0b")
                    )

                self.table.setItem(
                    row_index,
                    column_index,
                    table_item,
                )

        self.table.setSortingEnabled(True)

        self.summary_label.setText(
            self.summary_label.text().split(" · 顯示")[0]
            + f" · 顯示 {len(items):,} 筆"
        )

    @staticmethod
    def normalize_color(
        color_value: object,
    ) -> str | None:
        if not color_value:
            return None

        color_text = str(color_value).strip()

        if color_text.startswith("#"):
            return color_text

        if len(color_text) in {6, 8}:
            return f"#{color_text}"

        return None