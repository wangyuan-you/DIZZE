from __future__ import annotations

import json
import sys
import traceback

from src.database.catalog_repository import (
    count_catalog_cases,
    count_catalog_items,
)
from src.database.db import init_database
from src.services.case_catalog_sync_service import (
    CaseCatalogSyncService,
)
from src.utils.logger import setup_logger


def main() -> int:
    logger = setup_logger()

    try:
        print("Initializing DIZZE database...")
        init_database()

        print("Downloading CS2 case catalog...")
        service = CaseCatalogSyncService()
        result = service.synchronize()

        database_cases = count_catalog_cases()
        database_items = count_catalog_items()

        print()
        print("Catalog synchronization completed.")
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )
        print()
        print(f"Database cases: {database_cases}")
        print(f"Database catalog items: {database_items}")

        logger.info(
            "Catalog sync completed: %s",
            result,
        )

        return 0

    except Exception as error:
        logger.exception("Catalog synchronization failed")

        print()
        print("Catalog synchronization failed:")
        print(str(error))
        print()
        traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())