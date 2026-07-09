import sys

from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger


def main():
    logger = setup_logger()
    logger.info("DIZZE started")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()