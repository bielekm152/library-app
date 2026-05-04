import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> None:
    # Načítaj úroveň logovacieho z premenného prostredia LOG_LEVEL
    # Default je INFO, môžeš to zmeniť na: DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "library_app.log"

    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Prevent duplicated logs when the app is started multiple times in one session.
    if logger.handlers:
        return

    logger.addHandler(handler)
