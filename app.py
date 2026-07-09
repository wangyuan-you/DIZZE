import sys

from PySide6.QtWidgets import QApplication

from src.database.db import init_database
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger


def main():
    logger = setup_logger()
    logger.info("DIZZE started")

    init_database()
    logger.info("Database initialized")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()