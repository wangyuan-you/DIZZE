import sys

from PySide6.QtWidgets import QApplication

from src.database.db import init_database
from src.gui.main_window import MainWindow
from src.market.market_service import MarketService
from src.services.case_drop_importer import import_case_drops_from_json
from src.utils.logger import setup_logger


def main() -> None:
    logger = setup_logger()
    logger.info("DIZZE started")

    try:
        init_database()
        logger.info("Database initialized")

        imported_drops = import_case_drops_from_json()
        logger.info("Imported %s case drops", imported_drops)

        market_service = MarketService()
        logger.info(
            "Market data layer initialized: %s",
            market_service.get_market_status(),
        )

    except Exception:
        logger.exception("Application initialization failed")
        raise

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    exit_code = app.exec()

    logger.info("DIZZE closed with exit code %s", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()