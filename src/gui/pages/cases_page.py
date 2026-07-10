from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.database.catalog_repository import (
    count_catalog_cases,
    count_catalog_items,
    get_catalog_cases,
    get_catalog_items,
)
from src.gui.widgets.item_browser import ItemBrowser


class CasesPage(QWidget):
    CASE_ID_ROLE = Qt.ItemDataRole.UserRole

    def __init__(self) -> None:
        super().__init__()

        self.catalog_cases: list[dict[str, Any]] = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(14)

        header_layout = QHBoxLayout()

        title_container = QVBoxLayout()
        title_container.setSpacing(2)

        title = QLabel("Case Browser")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "瀏覽已同步的 CS2 武器箱、掉落池、磨損版本與 Market Hash Name"
        )
        subtitle.setObjectName("PageSubtitle")

        title_container.addWidget(title)
        title_container.addWidget(subtitle)

        self.refresh_button = QPushButton("重新載入資料庫")
        self.refresh_button.setFixedWidth(160)
        self.refresh_button.clicked.connect(
            self.reload_catalog
        )

        header_layout.addLayout(title_container, 1)
        header_layout.addWidget(self.refresh_button)

        statistics_frame = QFrame()
        statistics_frame.setObjectName("CatalogStatsFrame")

        statistics_layout = QHBoxLayout(statistics_frame)
        statistics_layout.setContentsMargins(16, 12, 16, 12)

        self.case_count_label = QLabel("箱子：0")
        self.item_count_label = QLabel("物品版本：0")
        self.selected_case_label = QLabel("目前選擇：-")

        for label in (
            self.case_count_label,
            self.item_count_label,
            self.selected_case_label,
        ):
            label.setObjectName("CatalogStatLabel")

        statistics_layout.addWidget(self.case_count_label)
        statistics_layout.addWidget(self.item_count_label)
        statistics_layout.addStretch()
        statistics_layout.addWidget(self.selected_case_label)

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )
        splitter.setChildrenCollapsible(False)

        case_panel = QFrame()
        case_panel.setObjectName("CaseListPanel")
        case_panel.setMinimumWidth(270)
        case_panel.setMaximumWidth(380)

        case_panel_layout = QVBoxLayout(case_panel)
        case_panel_layout.setContentsMargins(12, 12, 12, 12)
        case_panel_layout.setSpacing(10)

        case_panel_title = QLabel("武器箱")
        case_panel_title.setObjectName("PanelTitle")

        self.case_search_input = QLineEdit()
        self.case_search_input.setPlaceholderText(
            "搜尋箱子..."
        )
        self.case_search_input.setClearButtonEnabled(True)

        self.case_list = QListWidget()
        self.case_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        case_panel_layout.addWidget(case_panel_title)
        case_panel_layout.addWidget(
            self.case_search_input
        )
        case_panel_layout.addWidget(self.case_list, 1)

        self.item_browser = ItemBrowser()

        splitter.addWidget(case_panel)
        splitter.addWidget(self.item_browser)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 900])

        root_layout.addLayout(header_layout)
        root_layout.addWidget(statistics_frame)
        root_layout.addWidget(splitter, 1)

        self.case_search_input.textChanged.connect(
            self.filter_case_list
        )
        self.case_list.currentItemChanged.connect(
            self.on_case_selected
        )

        self.reload_catalog()

    def reload_catalog(self) -> None:
        self.catalog_cases = get_catalog_cases()

        self.case_count_label.setText(
            f"箱子：{count_catalog_cases():,}"
        )
        self.item_count_label.setText(
            f"物品版本：{count_catalog_items():,}"
        )

        self.populate_case_list(
            self.catalog_cases
        )

    def populate_case_list(
        self,
        cases: list[dict[str, Any]],
    ) -> None:
        current_case_id = self.get_selected_case_id()

        self.case_list.blockSignals(True)
        self.case_list.clear()

        selected_row = -1

        for row_index, case_data in enumerate(cases):
            case_name = str(case_data.get("name") or "-")
            item_count = int(
                case_data.get("item_count") or 0
            )

            list_item = QListWidgetItem(
                f"{case_name}\n{item_count:,} 個版本"
            )
            list_item.setData(
                self.CASE_ID_ROLE,
                case_data.get("case_id"),
            )

            self.case_list.addItem(list_item)

            if (
                current_case_id
                and case_data.get("case_id")
                == current_case_id
            ):
                selected_row = row_index

        self.case_list.blockSignals(False)

        if selected_row >= 0:
            self.case_list.setCurrentRow(selected_row)
        elif self.case_list.count() > 0:
            self.case_list.setCurrentRow(0)
        else:
            self.item_browser.clear_items()
            self.selected_case_label.setText(
                "目前選擇：-"
            )

    def filter_case_list(self) -> None:
        query = (
            self.case_search_input.text()
            .strip()
            .lower()
        )

        if not query:
            filtered_cases = self.catalog_cases
        else:
            filtered_cases = [
                case_data
                for case_data in self.catalog_cases
                if query
                in str(
                    case_data.get("name") or ""
                ).lower()
            ]

        self.populate_case_list(filtered_cases)

    def on_case_selected(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        del previous

        if current is None:
            self.item_browser.clear_items()
            self.selected_case_label.setText(
                "目前選擇：-"
            )
            return

        case_id = current.data(self.CASE_ID_ROLE)

        if not case_id:
            return

        selected_case = next(
            (
                case_data
                for case_data in self.catalog_cases
                if case_data.get("case_id") == case_id
            ),
            None,
        )

        case_name = (
            str(selected_case.get("name"))
            if selected_case
            else str(current.text().splitlines()[0])
        )

        items = get_catalog_items(str(case_id))

        self.selected_case_label.setText(
            f"目前選擇：{case_name}"
        )

        self.item_browser.set_items(
            items=items,
            case_name=case_name,
        )

    def get_selected_case_id(self) -> str | None:
        current_item = self.case_list.currentItem()

        if current_item is None:
            return None

        case_id = current_item.data(
            self.CASE_ID_ROLE
        )

        return str(case_id) if case_id else None