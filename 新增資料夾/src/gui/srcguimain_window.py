from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFrame,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DIZZE - CS2 Skin Terminal")
        self.resize(1400, 850)

        root = QWidget()
        root_layout = QHBoxLayout(root)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)

        for item in [
            "Dashboard",
            "Cases ROI",
            "Trade Up",
            "Inventory",
            "Market Watch",
            "Blue Gem",
            "Settings",
        ]:
            QListWidgetItem(item, self.sidebar)

        content = QFrame()
        content_layout = QVBoxLayout(content)

        title = QLabel("DIZZE - CS2 Skin Terminal")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")

        subtitle = QLabel("CS2 開箱 ROI、Trade Up、庫存分析、刀價監控工具")
        subtitle.setStyleSheet("font-size: 16px; color: #9ca3af;")

        status = QLabel(
            "v0.2 Dashboard\n\n"
            "✅ GUI 啟動成功\n"
            "✅ 專案架構正常\n"
            "⏳ 下一步：加入 Cases ROI 表格\n"
            "⏳ 再下一步：加入 EV / ROI 計算器"
        )
        status.setStyleSheet("font-size: 18px; padding-top: 30px;")

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addWidget(status)
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
                padding: 24px;
            }
        """)