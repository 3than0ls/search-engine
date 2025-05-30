from index import Indexer
from utils import load_config
import os
from pathlib import Path


def main() -> None:
    load_config()  # must be called to load critical environment variables

    webpages_dir = os.environ.get("WEBPAGES_DIR")
    assert webpages_dir
    partial_index_dir = os.environ.get("PARTIAL_INDEX_DIR")
    assert partial_index_dir
    index_dir = os.environ.get("INDEX_DIR")
    assert index_dir

    indexer = Indexer(
        Path(webpages_dir),
        Path(partial_index_dir),
        Path(index_dir)
    )
    indexer.construct()


if __name__ == '__main__':
    main()
