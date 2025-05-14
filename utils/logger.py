import logging
from pathlib import Path
import os

index_log = None
engine_log = None

_created = False


def _create_logs():
    global index_log, engine_log, _created

    if _created:
        return

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    index_log_path = log_dir / "indexer.log"
    index_log = logging.getLogger("INDEXER")
    index_log.setLevel(logging.INFO)

    if not index_log.handlers and os.environ.get("TESTING") != "true":
        file_handler = logging.FileHandler(index_log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        index_log.addHandler(file_handler)
        index_log.info("Initializing index logger...")

    engine_log_path = log_dir / "engine.log"
    engine_log = logging.getLogger("ENGINE")
    engine_log.setLevel(logging.INFO)

    if not engine_log.handlers and os.environ.get("TESTING") != "true":
        file_handler = logging.FileHandler(engine_log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        engine_log.addHandler(file_handler)
        engine_log.info("Initializing engine logger...")

    _created = True


_create_logs()
