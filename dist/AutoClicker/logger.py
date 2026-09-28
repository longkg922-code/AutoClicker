import logging
import os
from logging.handlers import RotatingFileHandler


def get_data_dir():
    path = os.path.join(
        os.environ.get(
            "APPDATA",
            os.path.expanduser("~")
        ),
        "AutoClicker"
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    return path


def setup_logger():
    logger = logging.getLogger("AutoClicker")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_file = os.path.join(
        get_data_dir(),
        "autoclicker.log"
    )

    handler = RotatingFileHandler(
        log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logger()

