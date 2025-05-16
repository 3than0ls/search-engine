from index import Indexer
from utils import load_config
import os


def main() -> None:
    load_config()  # must be called to load critical environment variables
    indexer = Indexer(os.environ.get("WEBPAGES_DIR"))
    indexer.construct()


if __name__ == '__main__':
    main()
