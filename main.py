from index import Indexer
import os


def main() -> None:
    indexer = Indexer(os.environ.get("WEBPAGES_DIR"))
    indexer.construct()


if __name__ == '__main__':
    main()
