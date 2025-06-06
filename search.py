import sys
from pathlib import Path
from engine.inverted_index import InvertedIndex
from utils.config import load_config
import os
import time


def main():
    load_config()
    index_dir = Path(os.environ.get('INDEX_DIR', './inverted_index'))

    try:
        inverted_index = InvertedIndex(index_dir)
    except FileNotFoundError:
        print(
            f"Error: Inverted index file not found at {index_dir}. Please run the indexer first.")
        sys.exit(1)

    while True:
        query = input("\nEnter query: ")
        if query.lower() == 'quit':
            break

        start = time.time()
        results = inverted_index.ranked_retrieve(query)
        end = time.time()

        if results:
            for i, url in enumerate(results):
                print(f"{i+1}. {url}")
        else:
            print("\nNo results found.")
        print(f"\nQuery executed in {end - start:.4f} seconds.")


if __name__ == "__main__":
    main()
