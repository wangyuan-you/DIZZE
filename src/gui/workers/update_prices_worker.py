from PySide6.QtCore import QObject, Signal, Slot

from src.market.market_service import MarketService


class UpdatePricesWorker(QObject):
    finished = Signal()
    error = Signal(str)

    @Slot()
    def run(self) -> None:
        try:
            service = MarketService()
            service.update_all_prices()
            self.finished.emit()

        except Exception as error:
            self.error.emit(str(error))