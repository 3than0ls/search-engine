from indexer import Indexer


def main() -> None:
    indexer = Indexer('./ANALYST')
    indexer.construct()


if __name__ == '__main__':
    main()
