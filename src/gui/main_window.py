from src.roi.case_roi_engine import get_case_roi_rows
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DIZZE - CS2 Skin Terminal")
        self.resize(1400, 850)

        root = QWidget()
        root_layout = QHBoxLayout(root)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(230)

        for name in [
            "Dashboard",
            "Cases",
            "Trade Up",
            "Inventory",
            "Market Watch",
            "Blue Gem",
            "Settings",
        ]:
            QListWidgetItem(name, self.sidebar)

        content = QFrame()
        content_layout = QVBoxLayout(content)

        title = QLabel("DIZZE - CS2 Skin Terminal")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")

        subtitle = QLabel("CS2 開箱 ROI、Trade Up、庫存分析、刀價監控工具")
        subtitle.setStyleSheet("font-size: 16px; color: #9ca3af;")

        cards_layout = QHBoxLayout()

        cards = [
    ("Cases", "43", "已建立本地箱子資料庫"),
    ("ROI Engine", "Ready", "SQLite Driven"),
    ("Market", "Offline", "Steam connector ready for v0.8"),
    ("Cache", "4 Items", "Market Data Layer"),
    ("Version", "v0.7", "Market Data Layer"),
]
        for title_text, value_text, desc_text in cards:
            card = QFrame()
            card.setObjectName("Card")
            card_layout = QVBoxLayout(card)

            card_title = QLabel(title_text)
            card_title.setStyleSheet("color: #94a3b8; font-size: 14px;")

            card_value = QLabel(value_text)
            card_value.setStyleSheet("font-size: 28px; font-weight: bold;")

            card_desc = QLabel(desc_text)
            card_desc.setStyleSheet("color: #9ca3af; font-size: 13px;")

            card_layout.addWidget(card_title)
            card_layout.addWidget(card_value)
            card_layout.addWidget(card_desc)

            cards_layout.addWidget(card)

        section_title = QLabel("ROI Preview")
        section_title.setStyleSheet("font-size: 22px; font-weight: bold; margin-top: 20px;")

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
    "Case",
    "Cost (NT$)",
    "EV (NT$)",
    "Profit",
    "ROI",
    "Gold Pool",
    "Updated",
])

        roi_rows = get_case_roi_rows()

        table.setRowCount(len(roi_rows))

        for row_index, row in enumerate(roi_rows):
            profit = row.get("ev_twd", 0) - row.get("total_cost_twd", 0)

            values = [
                row.get("name", "-"),
                f'{row.get("total_cost_twd", 0):.0f}',
                f'{row.get("ev_twd", 0):.0f}',
                f'{profit:+.0f}',
                f'{row.get("roi", 0) * 100:.2f}%',
                row.get("gold_pool", "-"),
                row.get("updated_at", "-"),
            ]

            for col_index, value in enumerate(values):
                table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        next_button = QPushButton("Update Prices - coming in v0.8")

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addLayout(cards_layout)
        content_layout.addWidget(section_title)
        content_layout.addWidget(table)
        content_layout.addWidget(next_button)
        content_layout.addStretch()

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(content)

        self.setCentralWidget(root)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }

            QWidget {
                background-color: #0f172a;
                color: #e5e7eb;
                font-family: Microsoft JhengHei;
            }

            QListWidget {
                background-color: #111827;
                border: none;
                font-size: 16px;
                padding: 12px;
            }

            QListWidget::item {
                padding: 14px;
                border-radius: 8px;
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
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 14px;
            }

            QTableWidget {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 10px;
                gridline-color: #374151;
                font-size: 14px;
            }

            QHeaderView::section {
                background-color: #1f2937;
                color: #e5e7eb;
                padding: 8px;
                border: none;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)