import sys

from PySide6.QtWidgets import QApplication

from src.database.db import init_database
from src.database.case_repository import import_cases_from_json
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.market.market_service import MarketService


def main():
    logger = setup_logger()
    logger.info("DIZZE started")

    init_database()
    #import_cases_from_json()
    market_service = MarketService()
    #market_service.seed_demo_prices()
    logger.info("Market data layer initialized")
    logger.info("Database initialized and cases imported")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()