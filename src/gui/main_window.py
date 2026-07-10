from __future__ import annotations

from PySide6.QtCore import QThread
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.workers.update_prices_worker import UpdatePricesWorker
from src.roi.case_roi_engine import get_case_roi_rows


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.thread: QThread | None = None
        self.worker: UpdatePricesWorker | None = None

        self.setWindowTitle("DIZZE - CS2 Skin Terminal")
        self.resize(1400, 850)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(20)

        # ==============================
        # 左側選單
        # ==============================

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(230)

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

        self.sidebar.setCurrentRow(0)

        # ==============================
        # 主內容區
        # ==============================

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        title = QLabel("DIZZE - CS2 Skin Terminal")
        title.setObjectName("PageTitle")

        subtitle = QLabel("CS2 開箱 ROI、Trade Up、庫存分析、刀價監控工具")
        subtitle.setObjectName("PageSubtitle")

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)

        # ==============================
        # Dashboard 資訊卡
        # ==============================

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        cards = [
            ("Cases", "43", "已建立本地箱子資料庫"),
            ("ROI Engine", "Ready", "SQLite Driven"),
            ("Market", "Steam", "Real-time connector"),
            ("Cache", "4 Items", "SQLite market cache"),
            ("Version", "v0.8", "Steam Market Integration"),
        ]

        for card_title, card_value, card_description in cards:
            card = self.create_info_card(
                card_title,
                card_value,
                card_description,
            )
            cards_layout.addWidget(card)

        content_layout.addLayout(cards_layout)

        # ==============================
        # ROI 表格
        # ==============================

        section_title = QLabel("ROI Preview")
        section_title.setObjectName("SectionTitle")
        content_layout.addWidget(section_title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
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

        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

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
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        content_layout.addWidget(self.table, 1)

        # ==============================
        # 狀態與更新按鈕
        # ==============================

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")

        self.update_button = QPushButton("Update Steam Prices")
        self.update_button.clicked.connect(self.update_prices)

        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.update_button)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(content, 1)

        self.setCentralWidget(root)

        self.apply_styles()
        self.refresh_table()

    def create_info_card(
        self,
        title_text: str,
        value_text: str,
        description_text: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title = QLabel(title_text)
        title.setObjectName("CardTitle")

        value = QLabel(value_text)
        value.setObjectName("CardValue")

        description = QLabel(description_text)
        description.setObjectName("CardDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(value)
        layout.addWidget(description)

        return card

    def refresh_table(self) -> None:
        """重新從 SQLite 讀取 ROI 資料並刷新表格。"""

        roi_rows = get_case_roi_rows()

        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(roi_rows))

        for row_index, row in enumerate(roi_rows):
            total_cost = float(row.get("total_cost_twd", 0))
            expected_value = float(row.get("ev_twd", 0))
            profit = expected_value - total_cost
            roi = float(row.get("roi", 0))

            values = [
                row.get("name", "-"),
                f"{total_cost:,.0f}",
                f"{expected_value:,.0f}",
                f"{profit:+,.0f}",
                f"{roi * 100:.2f}%",
                row.get("gold_pool", "-"),
                self.format_updated_at(row.get("updated_at")),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                # Profit 欄位顏色
                if column_index == 3:
                    if profit > 0:
                        item.setForeground(QColor("#22c55e"))
                    elif profit < 0:
                        item.setForeground(QColor("#ef4444"))

                # ROI 欄位顏色
                if column_index == 4:
                    if roi >= 1:
                        item.setForeground(QColor("#22c55e"))
                    elif roi < 0.7:
                        item.setForeground(QColor("#ef4444"))
                    else:
                        item.setForeground(QColor("#f59e0b"))

                self.table.setItem(
                    row_index,
                    column_index,
                    item,
                )

        self.table.setSortingEnabled(True)

        self.status_label.setText(
            f"Ready · Loaded {len(roi_rows)} cases from SQLite"
        )

    @staticmethod
    def format_updated_at(updated_at: object) -> str:
        if updated_at is None:
            return "-"

        text = str(updated_at)

        if len(text) >= 16:
            return text[:16]

        return text

    def update_prices(self) -> None:
        """使用背景執行緒更新 Steam 市場價格。"""

        if self.thread is not None and self.thread.isRunning():
            return

        self.update_button.setEnabled(False)
        self.update_button.setText("Updating Steam Prices...")
        self.status_label.setText("Connecting to Steam Market...")

        self.thread = QThread(self)
        self.worker = UpdatePricesWorker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_update_finished)
        self.worker.error.connect(self.on_update_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_update_objects)

        self.thread.start()

    def on_update_finished(self) -> None:
        """背景更新成功後刷新表格。"""

        self.refresh_table()

        self.update_button.setEnabled(True)
        self.update_button.setText("Update Steam Prices")
        self.status_label.setText(
            "Steam prices updated successfully"
        )

    def on_update_error(self, message: str) -> None:
        """背景更新失敗時保留原本快取價格。"""

        print(f"Steam update error: {message}")

        self.update_button.setEnabled(True)
        self.update_button.setText("Update Steam Prices")
        self.status_label.setText(
            f"Update failed · Using cached prices · {message}"
        )

    def clear_update_objects(self) -> None:
        self.worker = None
        self.thread = None

    def apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0b1120;
            }

            QWidget {
                background-color: #0f172a;
                color: #e5e7eb;
                font-family: "Microsoft JhengHei", "Segoe UI", Arial;
                font-size: 14px;
            }

            QLabel#PageTitle {
                font-size: 32px;
                font-weight: 700;
                color: #f8fafc;
            }

            QLabel#PageSubtitle {
                color: #94a3b8;
                font-size: 15px;
                margin-bottom: 4px;
            }

            QLabel#SectionTitle {
                font-size: 22px;
                font-weight: 700;
                color: #f8fafc;
                margin-top: 10px;
            }

            QLabel#StatusLabel {
                color: #94a3b8;
                padding: 4px;
            }

            QListWidget {
                background-color: #0b1120;
                border: none;
                padding: 8px;
                font-size: 16px;
            }

            QListWidget::item {
                padding: 14px;
                margin-bottom: 4px;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #172033;
            }

            QListWidget::item:selected {
                background-color: #2563eb;
                color: white;
            }

            QFrame {
                background-color: #0f172a;
            }

            QFrame#Card {
                background-color: #111827;
                border: 1px solid #263247;
                border-radius: 12px;
            }

            QLabel#CardTitle {
                color: #94a3b8;
                font-size: 13px;
            }

            QLabel#CardValue {
                color: #f8fafc;
                font-size: 27px;
                font-weight: 700;
            }

            QLabel#CardDescription {
                color: #94a3b8;
                font-size: 12px;
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
                min-height: 42px;
                padding: 8px 14px;
                font-size: 15px;
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