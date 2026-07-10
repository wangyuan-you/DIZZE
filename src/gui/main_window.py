from __future__ import annotations

from PySide6.QtCore import QThread
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.database.catalog_repository import (
    count_catalog_cases,
    count_catalog_items,
)
from src.database.market_repository import (
    count_market_prices,
)
from src.gui.pages.cases_page import CasesPage
from src.gui.workers.update_prices_worker import (
    UpdatePricesWorker,
)
from src.roi.case_roi_engine import get_case_roi_rows


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.thread: QThread | None = None
        self.worker: UpdatePricesWorker | None = None

        self.setWindowTitle(
            "DIZZE - CS2 Skin Terminal"
        )
        self.resize(1500, 900)
        self.setMinimumSize(1150, 700)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )
        root_layout.setSpacing(18)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)

        menu_items = [
            "Dashboard",
            "Cases",
            "Trade Up",
            "Inventory",
            "Market Watch",
            "Blue Gem",
            "Settings",
        ]

        for name in menu_items:
            QListWidgetItem(name, self.sidebar)

        self.page_stack = QStackedWidget()

        self.dashboard_page = self.create_dashboard_page()
        self.cases_page = CasesPage()

        self.page_stack.addWidget(
            self.dashboard_page
        )
        self.page_stack.addWidget(
            self.cases_page
        )
        self.page_stack.addWidget(
            self.create_placeholder_page(
                "Trade Up",
                "Trade Up Analyzer 將在後續版本加入。",
            )
        )
        self.page_stack.addWidget(
            self.create_placeholder_page(
                "Inventory",
                "Steam Inventory Manager 將在後續版本加入。",
            )
        )
        self.page_stack.addWidget(
            self.create_placeholder_page(
                "Market Watch",
                "價格追蹤、歷史走勢與提醒功能將在後續版本加入。",
            )
        )
        self.page_stack.addWidget(
            self.create_placeholder_page(
                "Blue Gem",
                "Case Hardened Pattern 分析功能將在後續版本加入。",
            )
        )
        self.page_stack.addWidget(
            self.create_placeholder_page(
                "Settings",
                "資料來源、匯率、鑰匙價格與快取設定將在後續版本加入。",
            )
        )

        self.sidebar.currentRowChanged.connect(
            self.change_page
        )
        self.sidebar.setCurrentRow(0)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.page_stack, 1)

        self.setCentralWidget(root)

        self.apply_styles()
        self.refresh_dashboard()

    def create_dashboard_page(self) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title = QLabel(
            "DIZZE - CS2 Skin Terminal"
        )
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "CS2 開箱 ROI、掉落池、Trade Up、庫存與市場分析工具"
        )
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        self.catalog_cases_value = QLabel("0")
        self.catalog_items_value = QLabel("0")
        self.market_cache_value = QLabel("0")
        self.roi_engine_value = QLabel("Ready")
        self.version_value = QLabel("v0.9")

        cards = [
            (
                "Catalog Cases",
                self.catalog_cases_value,
                "同步的 CS2 武器箱",
            ),
            (
                "Catalog Items",
                self.catalog_items_value,
                "磨損與 StatTrak 版本",
            ),
            (
                "Market Cache",
                self.market_cache_value,
                "Steam 市場快取",
            ),
            (
                "ROI Engine",
                self.roi_engine_value,
                "Case ROI Engine 2.0",
            ),
            (
                "Version",
                self.version_value,
                "Case Browser",
            ),
        ]

        for card_title, value_label, description in cards:
            cards_layout.addWidget(
                self.create_info_card(
                    title_text=card_title,
                    value_label=value_label,
                    description_text=description,
                )
            )

        layout.addLayout(cards_layout)

        section_title = QLabel("ROI Preview")
        section_title.setObjectName("SectionTitle")

        layout.addWidget(section_title)

        self.roi_table = QTableWidget()
        self.roi_table.setColumnCount(7)
        self.roi_table.setHorizontalHeaderLabels(
            [
                "Case",
                "Cost (NT$)",
                "EV (NT$)",
                "Profit",
                "ROI",
                "Gold Pool",
                "Updated",
            ]
        )

        self.roi_table.setAlternatingRowColors(True)
        self.roi_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.roi_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        header = self.roi_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        for column_index in range(1, 5):
            header.setSectionResizeMode(
                column_index,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.dashboard_status_label = QLabel("Ready")
        self.dashboard_status_label.setObjectName(
            "StatusLabel"
        )

        self.update_button = QPushButton(
            "Update Steam Prices"
        )
        self.update_button.clicked.connect(
            self.update_prices
        )

        layout.addWidget(self.roi_table, 1)
        layout.addWidget(
            self.dashboard_status_label
        )
        layout.addWidget(self.update_button)

        return page

    def create_info_card(
        self,
        title_text: str,
        value_label: QLabel,
        description_text: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            15,
            13,
            15,
            13,
        )
        layout.setSpacing(5)

        title = QLabel(title_text)
        title.setObjectName("CardTitle")

        value_label.setObjectName("CardValue")

        description = QLabel(description_text)
        description.setObjectName(
            "CardDescription"
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(value_label)
        layout.addWidget(description)

        return card

    def create_placeholder_page(
        self,
        title_text: str,
        description_text: str,
    ) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(title_text)
        title.setObjectName("PageTitle")

        description = QLabel(description_text)
        description.setObjectName("PageSubtitle")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        return page

    def change_page(self, index: int) -> None:
        if index < 0:
            return

        self.page_stack.setCurrentIndex(index)

        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.cases_page.reload_catalog()

    def refresh_dashboard(self) -> None:
        self.catalog_cases_value.setText(
            f"{count_catalog_cases():,}"
        )
        self.catalog_items_value.setText(
            f"{count_catalog_items():,}"
        )
        self.market_cache_value.setText(
            f"{count_market_prices():,}"
        )

        self.refresh_roi_table()

    def refresh_roi_table(self) -> None:
        roi_rows = get_case_roi_rows()

        self.roi_table.setSortingEnabled(False)
        self.roi_table.clearContents()
        self.roi_table.setRowCount(
            len(roi_rows)
        )

        for row_index, row in enumerate(roi_rows):
            total_cost = float(
                row.get("total_cost_twd", 0)
            )
            expected_value = float(
                row.get("ev_twd", 0)
            )

            profit = float(
                row.get(
                    "profit_twd",
                    expected_value - total_cost,
                )
            )

            roi = float(row.get("roi", 0))

            values = [
                row.get("name", "-"),
                f"{total_cost:,.0f}",
                f"{expected_value:,.0f}",
                f"{profit:+,.0f}",
                f"{roi * 100:.2f}%",
                row.get("gold_pool", "-"),
                self.format_updated_at(
                    row.get("updated_at")
                ),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if column_index == 3:
                    if profit > 0:
                        item.setForeground(
                            QColor("#22c55e")
                        )
                    elif profit < 0:
                        item.setForeground(
                            QColor("#ef4444")
                        )

                if column_index == 4:
                    if roi > 0:
                        item.setForeground(
                            QColor("#22c55e")
                        )
                    elif roi > -0.3:
                        item.setForeground(
                            QColor("#f59e0b")
                        )
                    else:
                        item.setForeground(
                            QColor("#ef4444")
                        )

                self.roi_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

        self.roi_table.setSortingEnabled(True)

        self.dashboard_status_label.setText(
            f"Ready · Loaded {len(roi_rows)} ROI rows"
        )

    @staticmethod
    def format_updated_at(
        updated_at: object,
    ) -> str:
        if updated_at is None:
            return "-"

        text = str(updated_at)

        if len(text) >= 16:
            return text[:16]

        return text

    def update_prices(self) -> None:
        if (
            self.thread is not None
            and self.thread.isRunning()
        ):
            return

        self.update_button.setEnabled(False)
        self.update_button.setText(
            "Updating Steam Prices..."
        )
        self.dashboard_status_label.setText(
            "Connecting to Steam Market..."
        )

        self.thread = QThread(self)
        self.worker = UpdatePricesWorker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.finished.connect(
            self.on_update_finished
        )
        self.worker.error.connect(
            self.on_update_error
        )

        self.worker.finished.connect(
            self.thread.quit
        )
        self.worker.error.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )
        self.worker.error.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )
        self.thread.finished.connect(
            self.clear_update_objects
        )

        self.thread.start()

    def on_update_finished(self) -> None:
        self.refresh_dashboard()

        self.update_button.setEnabled(True)
        self.update_button.setText(
            "Update Steam Prices"
        )
        self.dashboard_status_label.setText(
            "Steam prices updated successfully"
        )

    def on_update_error(
        self,
        message: str,
    ) -> None:
        print(f"Steam update error: {message}")

        self.update_button.setEnabled(True)
        self.update_button.setText(
            "Update Steam Prices"
        )
        self.dashboard_status_label.setText(
            f"Update failed · Cached data retained · {message}"
        )

    def clear_update_objects(self) -> None:
        self.worker = None
        self.thread = None

    def apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #080d19;
            }

            QWidget {
                background-color: #0f172a;
                color: #e5e7eb;
                font-family: "Microsoft JhengHei", "Segoe UI", Arial;
                font-size: 14px;
            }

            QLabel#PageTitle {
                color: #f8fafc;
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#PageSubtitle {
                color: #94a3b8;
                font-size: 14px;
            }

            QLabel#SectionTitle {
                color: #f8fafc;
                font-size: 21px;
                font-weight: 700;
                margin-top: 8px;
            }

            QLabel#PanelTitle {
                color: #f8fafc;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#StatusLabel,
            QLabel#BrowserSummary {
                color: #94a3b8;
                padding: 4px;
            }

            QLabel#CatalogStatLabel {
                color: #cbd5e1;
                font-weight: 600;
            }

            QListWidget {
                background-color: #0b1120;
                border: 1px solid #1e293b;
                border-radius: 10px;
                padding: 7px;
            }

            QListWidget::item {
                padding: 12px;
                margin-bottom: 3px;
                border-radius: 7px;
            }

            QListWidget::item:hover {
                background-color: #172033;
            }

            QListWidget::item:selected {
                background-color: #2563eb;
                color: white;
            }

            QFrame#Card,
            QFrame#CatalogStatsFrame,
            QFrame#CaseListPanel,
            QFrame#BrowserFilterFrame {
                background-color: #111827;
                border: 1px solid #263247;
                border-radius: 11px;
            }

            QLabel#CardTitle {
                color: #94a3b8;
                font-size: 12px;
            }

            QLabel#CardValue {
                color: #f8fafc;
                font-size: 25px;
                font-weight: 700;
            }

            QLabel#CardDescription {
                color: #94a3b8;
                font-size: 11px;
            }

            QLineEdit,
            QComboBox {
                background-color: #0f172a;
                color: #e5e7eb;
                border: 1px solid #334155;
                border-radius: 7px;
                min-height: 34px;
                padding: 3px 9px;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #3b82f6;
            }

            QCheckBox {
                spacing: 7px;
                color: #cbd5e1;
            }

            QTableWidget {
                background-color: #111827;
                alternate-background-color: #0f172a;
                border: 1px solid #263247;
                border-radius: 10px;
                gridline-color: #334155;
                selection-background-color: #1d4ed8;
                selection-color: white;
            }

            QTableWidget::item {
                padding: 6px;
            }

            QHeaderView::section {
                background-color: #1e293b;
                color: #f8fafc;
                border: none;
                border-right: 1px solid #334155;
                padding: 9px;
                font-weight: 600;
            }

            QTableCornerButton::section {
                background-color: #1e293b;
                border: none;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                min-height: 40px;
                padding: 7px 14px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }

            QPushButton:disabled {
                background-color: #334155;
                color: #94a3b8;
            }

            QSplitter::handle {
                background-color: #1e293b;
                width: 2px;
            }

            QScrollBar:vertical {
                background: #111827;
                width: 12px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #334155;
                border-radius: 6px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background: #475569;
            }
            """
        )